# src/jct/evaluate.py
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from .chunking import extract_chunks
from .embedding import embed_texts
from .search import search

def run_evaluation(
    benchmark_folder: str = "eval_benchmarks/concepts/file_handling",
    queries: List[str] = None,
    ground_truth_files: List[str] = None,
    top_k: int = 5,
    min_score: float = 0.5
):
    """
    Run multiple queries on a benchmark folder and save results.
    - benchmark_folder: path to graded files (e.g., file_handling)
    - queries: list of test queries
    - ground_truth_files: expected best files (e.g. ['file_handling_100.py'])
    """
    # Default queries if none provided
    if queries is None:
        queries = [
            "safe file reading with error handling",
            "read file safely and handle not found",
            "handle file not found exception",
            "open and read file with try except"
        ]

    # Index the benchmark folder
    print(f"Indexing benchmark folder: {benchmark_folder}")
    all_chunks = []
    folder_path = Path(benchmark_folder)
    for py_file in folder_path.rglob("*.py"):
        chunks = extract_chunks(py_file)
        all_chunks.extend(chunks)

    if not all_chunks:
        print("No chunks found in benchmark folder.")
        return

    texts = [c["text"] for c in all_chunks]
    embeddings = embed_texts(texts)
    print(f"Indexed {len(all_chunks)} chunks.")

    # Create timestamped output folder
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = Path("eval_results") / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Saving results to: {output_dir}")

    results_data: List[Dict[str, Any]] = []
    summary_rows = []

    for query in queries:
        top_results = search(query, all_chunks, embeddings, top_k=top_k, min_score=min_score)

        # Simple metrics
        top_files = [r["file"] for r in top_results]
        top1_correct = ground_truth_files and ground_truth_files[0] in top_files[:1]
        top5_correct = ground_truth_files and any(f in top_files for f in ground_truth_files)

        result_entry = {
            "query": query,
            "top_results": [
                {"rank": i+1, "score": r["score"], "file": r["file"], "name": r["name"], "start_line": r["start_line"]}
                for i, r in enumerate(top_results)
            ],
            "top1_correct": top1_correct,
            "top5_correct": top5_correct
        }
        results_data.append(result_entry)

        summary_rows.append({
            "query": query,
            "top1_correct": "Yes" if top1_correct else "No",
            "top5_correct": "Yes" if top5_correct else "No",
            "top_score": top_results[0]["score"] if top_results else 0.0
        })

        # Print to console
        print(f"\nQuery: {query}")
        for i, r in enumerate(top_results, 1):
            print(f"  {i}. [{r['score']:.3f}] {r['file']}:{r['start_line']} {r['type']} {r['name']}")
        print("-" * 60)

    # Save full JSON results
    (output_dir / "full_results.json").write_text(json.dumps(results_data, indent=2))

    # Save CSV summary
    import csv
    with (output_dir / "summary.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["query", "top1_correct", "top5_correct", "top_score"])
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"\nEvaluation complete. Results saved in: {output_dir}")
    print(f" - full_results.json: detailed rankings")
    print(f" - summary.csv: quick metrics")

if __name__ == "__main__":
    run_evaluation()
