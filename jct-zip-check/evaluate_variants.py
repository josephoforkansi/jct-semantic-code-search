
"""Compare baseline search, query expansion, and typo-tolerant JCT."""

import argparse
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from jct.demo import index_folder
from jct.search import search

VARIANTS = {
    "baseline": {
        "use_query_expansion": False,
        "use_typo_correction": False,
    },
    "query_expansion": {
        "use_query_expansion": True,
        "use_typo_correction": False,
    },
    "full_jct": {
        "use_query_expansion": True,
        "use_typo_correction": True,
    },
}

TOP_K = 5
RANK_CUTOFF = 10

REQUIRED_COLUMNS = {
    "project_path",
    "target_name",
    "target_file",
    "query",
    "typo_type",
}


def normalize_path(path: str) -> str:
    """Normalize path separators for path comparisons."""
    return path.replace("\\", "/").strip("/").casefold()


def matches_target(
    result: Dict,
    target_name: str,
    target_file: str,
) -> bool:
    """Match a retrieved code entity by name and expected file."""
    result_name = str(result.get("name", ""))
    result_file = normalize_path(str(result.get("file", "")))
    expected_file = normalize_path(target_file)

    name_matches = result_name.casefold() == target_name.casefold()

    # Match the expected relative path within an absolute project path.
    file_matches = (
        not expected_file or expected_file in result_file
    )

    return name_matches and file_matches


def find_target_rank(
    results: List[Dict],
    target_name: str,
    target_file: str,
) -> Optional[int]:
    """Return the target's one-based rank, or None if not retrieved."""
    for rank, result in enumerate(results, start=1):
        if matches_target(result, target_name, target_file):
            return rank

    return None


def precision_at_k(rank: Optional[int], k: int) -> float:
    """
    Precision@k when exactly one designated relevant target exists.

    This returns 1/k if the target is retrieved within the first k
    positions, otherwise zero. It assumes the designated target is the
    only relevant result for that query.
    """
    if rank is not None and rank <= k:
        return 1.0 / k

    return 0.0


def success_at_k(rank: Optional[int], k: int) -> float:
    """Return 1 if the target appears in the top k, otherwise 0."""
    return float(rank is not None and rank <= k)


def reciprocal_rank(
    rank: Optional[int],
    cutoff: int = RANK_CUTOFF,
) -> float:
    """Return reciprocal rank within the specified cutoff."""
    if rank is None or rank > cutoff:
        return 0.0

    return 1.0 / rank


def read_queries(csv_path: Path) -> List[Dict[str, str]]:
    """Read and validate benchmark queries from a CSV file."""
    if not csv_path.is_file():
        raise FileNotFoundError(
            f"Benchmark CSV file does not exist: {csv_path}"
        )

    with csv_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError(
                f"The CSV file is empty or has no header: {csv_path}"
            )

        # Strip whitespace and BOM characters from header names.
        normalized_headers = [
            header.strip().lstrip("\ufeff").strip()
            for header in reader.fieldnames
        ]

        reader.fieldnames = normalized_headers

        missing = REQUIRED_COLUMNS - set(normalized_headers)

        if missing:
            raise ValueError(
                "Missing CSV columns: "
                + ", ".join(sorted(missing))
                + f"\nDetected columns: {normalized_headers}"
                + f"\nCSV file: {csv_path}"
            )

        rows = []

        for line_number, row in enumerate(reader, start=2):
            cleaned = {
                key.strip(): (value or "").strip()
                for key, value in row.items()
                if key is not None
            }

            for column in (
                "project_path",
                "target_name",
                "target_file",
                "query",
                "typo_type",
            ):
                if column not in cleaned:
                    raise ValueError(
                        f"CSV line {line_number}: missing column "
                        f"'{column}'."
                    )

            for column in (
                "project_path",
                "target_name",
                "target_file",
                "query",
            ):
                if not cleaned[column]:
                    raise ValueError(
                        f"CSV line {line_number}: "
                        f"'{column}' must not be empty."
                    )

            project_path = Path(cleaned["project_path"])

            if not project_path.is_dir():
                raise ValueError(
                    f"CSV line {line_number}: project directory "
                    f"does not exist: {project_path}"
                )

            rows.append(cleaned)

    if not rows:
        raise ValueError(
            f"The benchmark CSV contains no query rows: {csv_path}"
        )

    return rows


def evaluate(
    csv_path: Path,
    output_dir: Path,
) -> Tuple[List[Dict], List[Dict]]:
    """Evaluate all search variants on the same query dataset."""
    query_rows = read_queries(csv_path)

    # Index each project only once.
    project_cache = {}

    for row in query_rows:
        project_key = str(Path(row["project_path"]).resolve())

        if project_key not in project_cache:
            print(f"Indexing project: {project_key}")

            chunks, embeddings = index_folder(project_key)

            if not chunks:
                raise ValueError(
                    f"No code chunks were indexed from {project_key}"
                )

            project_cache[project_key] = (chunks, embeddings)

            print(f"  Indexed {len(chunks)} code chunks.")

    detailed_rows = []
    grouped_metrics = defaultdict(list)

    for query_index, row in enumerate(query_rows, start=1):
        project_key = str(Path(row["project_path"]).resolve())
        chunks, embeddings = project_cache[project_key]

        print(
            f"\n[{query_index}/{len(query_rows)}] "
            f"Query: {row['query']}"
        )

        for variant_name, options in VARIANTS.items():
            # Use the same low cutoff for every configuration so that
            # the comparison measures ranking rather than thresholding.
            results = search(
                row["query"],
                chunks,
                embeddings,
                top_k=RANK_CUTOFF,
                min_score=-1.0,
                **options,
            )

            rank = find_target_rank(
                results,
                row["target_name"],
                row["target_file"],
            )

            p_at_5 = precision_at_k(rank, TOP_K)
            success_5 = success_at_k(rank, TOP_K)
            mrr_10 = reciprocal_rank(rank, RANK_CUTOFF)

            record = {
                "query_id": query_index,
                "project_path": project_key,
                "target_name": row["target_name"],
                "target_file": row["target_file"],
                "query": row["query"],
                "typo_type": row["typo_type"],
                "variant": variant_name,
                "target_rank": rank if rank is not None else "",
                "precision_at_5": p_at_5,
                "success_at_5": success_5,
                "reciprocal_rank_at_10": mrr_10,
                "top_results": " | ".join(
                    f"{result.get('file', '')}:"
                    f"{result.get('name', '')}:"
                    f"{result.get('score', '')}"
                    for result in results[:TOP_K]
                ),
            }

            detailed_rows.append(record)
            grouped_metrics[variant_name].append(record)

            rank_text = str(rank) if rank is not None else "not found"

            print(
                f"  {variant_name}: rank={rank_text}, "
                f"P@5={p_at_5:.3f}, "
                f"Success@5={success_5:.0f}, "
                f"RR@10={mrr_10:.3f}"
            )

    summary_rows = []

    for variant_name, records in grouped_metrics.items():
        count = len(records)

        summary_rows.append(
            {
                "variant": variant_name,
                "query_count": count,
                "precision_at_5": sum(
                    record["precision_at_5"]
                    for record in records
                ) / count,
                "success_at_5": sum(
                    record["success_at_5"]
                    for record in records
                ) / count,
                "mrr_at_10": sum(
                    record["reciprocal_rank_at_10"]
                    for record in records
                ) / count,
            }
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    detailed_path = output_dir / "query_results.csv"
    summary_path = output_dir / "summary.csv"

    with detailed_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(detailed_rows[0].keys()),
        )
        writer.writeheader()
        writer.writerows(detailed_rows)

    with summary_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "variant",
                "query_count",
                "precision_at_5",
                "success_at_5",
                "mrr_at_10",
            ],
        )
        writer.writeheader()
        writer.writerows(summary_rows)

    return detailed_rows, summary_rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare JCT search configurations."
    )

    parser.add_argument(
        "--queries",
        default="eval_benchmarks/natural_language/queries.csv",
        help="Path to the benchmark CSV file.",
    )

    parser.add_argument(
        "--output-dir",
        default=None,
        help=(
            "Output directory. If omitted, a timestamped "
            "directory under eval_results is created."
        ),
    )

    args = parser.parse_args()

    csv_path = Path(args.queries)

    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("eval_results") / f"variants_{timestamp}"

    _, summary_rows = evaluate(csv_path, output_dir)

    print("\nAggregate results")
    print("=" * 72)

    for row in summary_rows:
        print(
            f"{row['variant']:18} "
            f"P@5={row['precision_at_5']:.3f}  "
            f"Success@5={row['success_at_5']:.3f}  "
            f"MRR@10={row['mrr_at_10']:.3f}"
        )

    print(f"\nDetailed results: {output_dir / 'query_results.csv'}")
    print(f"Summary results:  {output_dir / 'summary.csv'}")


if __name__ == "__main__":
    main()
