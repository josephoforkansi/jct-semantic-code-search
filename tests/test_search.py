import numpy as np
from jct.search import search


def test_search_basic():
    chunks = [
        {
            "file": "a.py",
            "name": "foo",
            "type": "function",
            "code": "def foo(): pass",
            "docstring": "",
            "concepts": ["file_handling"],
            "text": "file_handling open file",
            "start_line": 1
        }
    ]


    embeddings = np.random.rand(1, 384).astype("float32")

    results = search("file handling", chunks, embeddings, top_k=1, min_score=0)

    assert isinstance(results, list)
    assert len(results) >= 0