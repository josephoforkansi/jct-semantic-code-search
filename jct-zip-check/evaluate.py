# src/jct/evaluate.py
import json
import math
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from .chunking import extract_chunks
from .embedding import embed_texts
from .search import search


# =========================
# 📊 METRICS
# =========================

def precision_at_k(results, ground_truth_files, k=5):
    if not ground_truth_files:
        return 0.0
    relevant = sum(1 for r in results[:k] if r["file"] in ground_truth_files)
    return relevant / k


def ndcg_at_k(results, ground_truth_files, k=5):
    if not ground_truth_files:
        return 0.0

    # Compute DCG
    dcg = 0.0
    for i, r in enumerate(results[:k]):
        if r["file"] in ground_truth_files:
            dcg += 1 / math.log2(i + 2)

    # Compute ideal DCG (best possible ranking)
    ideal_hits = min(len(ground_truth_files), k)
    ideal_dcg = sum(1 / math.log2(i + 2) for i in range(ideal_hits))

    return dcg / ideal_dcg if ideal_dcg > 0 else 0.0


def success_rate_at_1(results, ground_truth_files):
    if not results or not ground_truth_files:
        return 0.0
    return 1.0 if results[0]["file"] in ground_truth_files else 0.0


# =========================
# 🔍 AUTO GROUND TRUTH
# =========================

def get_ground_truth_files(folder_path: Path) -> List[str]:
    """
    Detect all 'perfect' implementations (100-level files)
    ONLY from generated dataset.
    """
    gt_files = []

    for file in folder_path.rglob("*.py"):
        if "_100_" in file.name:
            gt_files.append(file.name)

    return gt_files


# =========================
# 🚀 MAIN EVALUATION
# =========================

def run_evaluation(
    benchmark_folder: str = "eval_benchmarks/concepts/file_handling/generated",
    queries: List[str] = None,
    top_k: int = 5,
    min_score: float = 0.5
):
    """
    Evaluation pipeline using ONLY generated dataset.
    """

    if queries is None:
        queries = [
            "safe file reading with error handling",
            "handle file not found exception",
            "read file safely with try except",
            "robust file reading function"
        ]

    folder_path = Path(benchmark_folder)

    print(f"\n📂 Indexing dataset: {benchmark_folder}")

    # =========================
    # AUTO GROUND TRUTH
    # =========================
    ground_truth_files = get_ground_truth_files(folder_path)

    if not ground_truth_files:
        print("⚠️ No ground truth (100-level) files found.")
    else:
        print(f"✅ Ground truth files detected: {len(ground_truth_files)}")

    # =========================
    # INDEXING
    # =========================
    all_chunks = []

    for py_file in folder_path.rglob("*.py"):
        all_chunks.extend(extract_chunks(py_file))

    if not all_chunks:
        print("❌ No chunks found.")
        return

    texts = [c["text"] for c in all_chunks]
    embeddings = embed_texts(texts)

    print(f"✅ Indexed {len(all_chunks)} chunks")

    # =========================
    # OUTPUT SETUP
    # =========================
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = Path("eval_results") / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    full_results: List[Dict[str, Any]] = []
    summary_rows = []

    # =========================
    # RUN QUERIES
    # =========================
    for query in queries:
        results = search(query, all_chunks, embeddings, top_k, min_score)

        # -------------------------
        # Metrics
        # -------------------------
        p_at_5 = precision_at_k(results, ground_truth_files, 5)
        ndcg = ndcg_at_k(results, ground_truth_files, 5)
        success = success_rate_at_1(results, ground_truth_files)
        avg_score = sum(r["score"] for r in results) / len(results) if results else 0.0

        # -------------------------
        # Store detailed results
        # -------------------------
        result_entry = {
            "query": query,
            "metrics": {
                "precision@5": round(p_at_5, 3),
                "ndcg@5": round(ndcg, 3),
                "success_rate@1": round(success, 3),
                "avg_score": round(avg_score, 3)
            },
            "top_results": [
                {
                    "rank": i + 1,
                    "score": r["score"],
                    "cos_score": r.get("cos_score"),
                    "file": r["file"],
                    "name": r["name"],
                    "start_line": r["start_line"],
                    "concepts": r.get("concepts", [])
                }
                for i, r in enumerate(results)
            ]
        }

        full_results.append(result_entry)

        # -------------------------
        # CSV Row (for charts)
        # -------------------------
        summary_rows.append({
            "query": query,
            "precision@5": round(p_at_5, 3),
            "ndcg@5": round(ndcg, 3),
            "success_rate@1": round(success, 3),
            "avg_score": round(avg_score, 3)
        })

        # -------------------------
        # Console Output
        # -------------------------
        print(f"\n🔍 Query: {query}")
        print(f"Precision@5: {p_at_5:.3f}")
        print(f"NDCG@5: {ndcg:.3f}")
        print(f"Success@1: {success:.0%}")
        print(f"Avg Score: {avg_score:.3f}")

        for i, r in enumerate(results, 1):
            print(f"  {i}. [{r['score']:.3f}] {r['file']}:{r['start_line']} {r['name']}")

        print("-" * 60)

    # =========================
    # SAVE FILES
    # =========================

    (output_dir / "full_results.json").write_text(
        json.dumps(full_results, indent=2)
    )

    with (output_dir / "summary.csv").open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["query", "precision@5", "ndcg@5", "success_rate@1", "avg_score"]
        )
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"\n📁 Results saved to: {output_dir}")
    print(" - full_results.json (detailed rankings)")
    print(" - summary.csv (metrics for charts)")


# =========================
# ▶ RUN
# =========================

if __name__ == "__main__":
    run_evaluation()