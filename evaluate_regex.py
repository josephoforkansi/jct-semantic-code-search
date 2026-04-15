import re
from pathlib import Path

# Dataset path (same as JCT)
folder = Path("eval_benchmarks/concepts/file_handling/generated")

# Queries → regex patterns
queries = {
    "safe_file": r"try:.*open\(",
    "try_except": r"try:.*except",
    "robust": r"open\(",
    "file_not_found": r"FileNotFoundError"
}

# Ground truth (same logic as JCT)
ground_truth = [f.name for f in folder.glob("*_100_*.py")]


def search_regex(pattern):
    matches = []

    for file in folder.glob("*.py"):
        text = file.read_text(encoding="utf-8")

        if re.search(pattern, text, re.DOTALL):
            matches.append(file.name)

    return matches


# Run evaluation
for name, pattern in queries.items():
    results = search_regex(pattern)

    top = results[:1]
    success = any(f in ground_truth for f in top)

    print(f"\n🔍 Query: {name}")
    print(f"Pattern: {pattern}")
    print(f"Top result: {top}")
    print(f"Success@1: {success}")