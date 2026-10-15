"""Tests for semantic code search."""

import importlib

import numpy as np

search_module = importlib.import_module("jct.search")

from jct.search import correct_typos, expand_query, search


def test_search_basic(monkeypatch):
    """Search returns matching chunks without loading a real model."""
    chunks = [
        {
            "file": "a.py",
            "name": "foo",
            "type": "function",
            "code": "def foo(): pass",
            "docstring": "",
            "concepts": ["file_handling"],
            "text": "file_handling open file",
            "start_line": 1,
        }
    ]

    class FakeModel:
        """Provide deterministic embeddings for testing."""

        def encode(self, texts):
            return np.zeros((len(texts), 384), dtype="float32")

    monkeypatch.setattr(
        search_module,
        "get_model",
        lambda: FakeModel(),
    )

    embeddings = np.zeros((1, 384), dtype="float32")

    results = search(
        "file handling",
        chunks,
        embeddings,
        top_k=1,
        min_score=0,
    )

    assert len(results) == 1
    assert results[0]["name"] == "foo"
    assert results[0]["file"] == "a.py"


def test_expand_query_removes_filler_phrases():
    """Query expansion removes filler words but preserves useful terms."""
    expanded = expand_query(
        "show me where the interface is defined"
    )

    words = expanded.split()

    assert "interface" in words
    assert "defined" in words
    assert "show" not in words
    assert "where" not in words
    assert "the" not in words


def test_expand_query_adds_interface_synonyms():
    """Query expansion adds synonyms for programming interfaces."""
    expanded = expand_query("interface")
    words = expanded.split()

    assert "interface" in words
    assert "class" in words
    assert "definition" in words
    assert "declaration" in words


def test_expand_query_preserves_project_identifier():
    """Query expansion preserves project-specific identifiers."""
    query = "JCT semantic code search"
    expanded = expand_query(query)

    assert "jct" in expanded.split()
    assert "semantic" in expanded.split()
    assert "code" in expanded.split()
    assert "search" in expanded.split()


def test_search_empty_query_returns_no_results():
    """An empty query returns no results without loading the model."""
    results = search(
        "",
        [],
        np.zeros((0, 384), dtype="float32"),
    )

    assert results == []


def test_correct_typos_fixes_lppk():
    """Common spelling mistakes are corrected."""
    assert correct_typos("lppk for code") == "look for code"


def test_correct_typos_preserves_function_call():
    """Correct words and function-call syntax remain intact."""
    query = "call read_file(path)"
    assert correct_typos(query) == query


def test_correct_typos_preserves_project_identifier():
    """Typo correction preserves the JCT identifier."""
    query = "JCT semantic code search"
    assert correct_typos(query) == query


def test_correct_typos_preserves_dotted_identifier():
    """Typo correction preserves dotted programming identifiers."""
    query = "os.path.isfile"
    assert correct_typos(query) == query


def test_correct_typos_preserves_correct_words():
    """Correctly spelled words are not modified."""
    query = "function retrieve file exception"
    assert correct_typos(query) == query
