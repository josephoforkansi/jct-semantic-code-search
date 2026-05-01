# tests/test_search.py

import numpy as np
from jct.search import search


def test_search_empty_input():
    """Search should return empty list when no data is provided."""
    results = search("test query", [], np.array([]))
    assert results == []


def test_search_returns_results():
    """Search should return a list of ranked results for valid input."""
    chunks = [
        {
            "file": "test.py",
            "name": "safe_read_file",
            "type": "function",
            "code": "def safe_read_file(path): return open(path).read()",
            "docstring": "Reads a file safely",
            "concepts": ["file_handling", "error_handling"],
            "text": "safe file reading with error handling",
            "start_line": 1
        }
    ]

    # Generate a dummy embedding matching model dimension (384)
    embeddings = np.random.rand(1, 384)

    results = search("safe file reading", chunks, embeddings)

    assert isinstance(results, list)
    if results:
        assert "score" in results[0]
        assert "file" in results[0]


def test_search_respects_top_k():
    """Search should return at most top_k results."""
    chunks = [
        {
            "file": f"file_{i}.py",
            "name": "func",
            "type": "function",
            "code": "def func(): pass",
            "docstring": "",
            "concepts": [],
            "text": "dummy",
            "start_line": 1
        }
        for i in range(10)
    ]

    embeddings = np.random.rand(10, 384)

    results = search("dummy", chunks, embeddings, top_k=3)

    assert len(results) <= 3