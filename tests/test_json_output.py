"""Tests for JCT JSON output utilities."""

import io
import json

from jct.json_output import (
    format_search_response,
    write_json_response,
)


def test_format_search_response() -> None:
    """The response should contain the query, count, and results."""
    query = "Find code that reads a file"
    results = [
        {
            "name": "read_file",
            "file": "files.py",
            "score": 0.92,
        }
    ]

    response = format_search_response(query, results)

    assert response["query"] == query
    assert response["result_count"] == 1
    assert response["results"] == results


def test_format_empty_search_response() -> None:
    """An empty search should produce a valid empty response."""
    response = format_search_response("missing concept", [])

    assert response == {
        "query": "missing concept",
        "result_count": 0,
        "results": [],
    }


def test_write_json_response() -> None:
    """The JSON writer should produce valid JSON."""
    query = "Find code that reads a file"
    results = [
        {
            "name": "read_file",
            "file": "files.py",
            "score": 0.92,
        }
    ]
    output = io.StringIO()

    write_json_response(query, results, output)

    decoded = json.loads(output.getvalue())

    assert decoded["query"] == query
    assert decoded["result_count"] == 1
    assert decoded["results"] == results


def test_write_json_response_handles_empty_results() -> None:
    """The JSON writer should support empty result lists."""
    output = io.StringIO()

    write_json_response("missing concept", [], output)

    decoded = json.loads(output.getvalue())

    assert decoded["result_count"] == 0
    assert decoded["results"] == []


def test_write_json_response_preserves_unicode() -> None:
    """Unicode characters should be preserved in JSON output."""
    output = io.StringIO()

    write_json_response(
        "Find code",
        [{"name": "读取文件", "file": "文件.py", "score": 0.9}],
        output,
    )

    assert "读取文件" in output.getvalue()
    assert "文件.py" in output.getvalue()


def test_write_json_response_ends_with_newline() -> None:
    """The JSON response should end with a newline."""
    output = io.StringIO()

    write_json_response("Find code", [], output)

    assert output.getvalue().endswith("\n")
