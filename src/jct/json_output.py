"""JSON output utilities for JCT semantic code search."""

import json
import sys
from typing import Any, TextIO


def format_search_response(
    query: str,
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Create a structured response from a search query and its results."""
    return {
        "query": query,
        "result_count": len(results),
        "results": results,
    }


def write_json_response(
    query: str,
    results: list[dict[str, Any]],
    output: TextIO | None = None,
) -> None:
    """Write search results as valid JSON."""
    response = format_search_response(query, results)

    json_text = json.dumps(
        response,
        indent=2,
        ensure_ascii=False,
        default=str,
    )

    if output is None or output is sys.stdout:
        # Write UTF-8 bytes directly, avoiding Windows cp1252 encoding.
        sys.stdout.buffer.write((json_text + "\n").encode("utf-8"))
        sys.stdout.buffer.flush()
    else:
        output.write(json_text + "\n")
