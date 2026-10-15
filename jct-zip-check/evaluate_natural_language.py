import argparse
from pathlib import Path

from jct.demo import index_folder
from jct.search import search

QUERY_VARIATIONS = [
    "class interface",
    "find the interface class",
    "show me where the interface is defined",
    "look for the class that stores interface labels",
    "where is the interface for system information defined?",
    "lppk around for class interface",
]


def is_target(result, target_name: str) -> bool:
    """Check whether a result matches the expected code entity."""
    return result["name"].casefold() == target_name.casefold()


def evaluate_queries(
    folder: str,
    target_name: str = "Interface",
    top_k: int = 5,
) -> None:
    """Evaluate query variations against a known target class."""
    chunks, embeddings = index_folder(folder)

    if not chunks:
        print("No code chunks were indexed. Evaluation stopped.")
        return

    hits = 0

    print(f"\nTarget code entity: {target_name}")
    print(f"Project: {Path(folder).expanduser().resolve()}")
    print(f"Queries tested: {len(QUERY_VARIATIONS)}")
    print("=" * 70)

    for query in QUERY_VARIATIONS:
        # Use a low threshold to inspect the ranking before filtering.
        results = search(
            query,
            chunks,
            embeddings,
            top_k=top_k,
            min_score=-1.0,
        )

        target_rank = next(
            (
                rank
                for rank, result in enumerate(results, start=1)
                if is_target(result, target_name)
            ),
            None,
        )

        # Also check whether the target survives the normal 0.5 threshold.
        normal_results = search(
            query,
            chunks,
            embeddings,
            top_k=top_k,
            min_score=0.5,
        )
        passes_threshold = any(
            is_target(result, target_name)
            for result in normal_results
        )

        if target_rank is not None:
            hits += 1
            rank_message = f"Rank: {target_rank}/{top_k}"
        else:
            rank_message = f"Not in top {top_k}"

        threshold_message = (
            "Yes" if passes_threshold else "No"
        )

        print(f"\nQuery: {query}")
        print(f"  {rank_message}")
        print(f"  Target passes 0.5 threshold: {threshold_message}")

        for rank, result in enumerate(results, start=1):
            print(
                f"    {rank}. {result['score']:.3f} | "
                f"{result['file']} | "
                f"{result['type']} {result['name']}"
            )

    total = len(QUERY_VARIATIONS)
    print("\n" + "=" * 70)
    print(f"Top-{top_k} success rate: {hits}/{total} ({hits / total:.1%})")
    print("This is a small, target-specific test—not a general accuracy score.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate JCT against natural-language query variations."
    )
    parser.add_argument(
        "folder",
        help="Path to the Python project to evaluate.",
    )
    parser.add_argument(
        "--target-name",
        default="Interface",
        help="Expected class or function name (default: Interface).",
    )
    args = parser.parse_args()

    evaluate_queries(args.folder, args.target_name)


if __name__ == "__main__":
    main()
