
"""Tests for JCT CLI search and Llama fallback behavior."""

from argparse import Namespace

import numpy as np

from jct import cli


def make_args(path, *, no_llm=False):
    """Build arguments for a CLI search."""
    return Namespace(
        query="find code that safely reads a file",
        path=str(path),
        top_k=5,
        min_score=0.5,
        no_query_expansion=False,
        no_typo_correction=False,
        no_cache=False,
        no_llm=no_llm,
    )


def test_found_results_do_not_trigger_llm(tmp_path, monkeypatch, capsys):
    """Successful retrieval should return archive code without calling Llama."""
    chunks = [{"name": "read_file"}]
    embeddings = np.ones((1, 384))

    monkeypatch.setattr(
        cli,
        "index_folder",
        lambda *args, **kwargs: (chunks, embeddings),
    )
    monkeypatch.setattr(
        cli,
        "search",
        lambda *args, **kwargs: [
            {
                "score": 0.82,
                "file": "reader.py",
                "start_line": 1,
                "type": "function",
                "name": "read_file",
                "code": (
                    "def read_file(path):\n"
                    "    with open(path) as f:\n"
                    "        return f.read()"
                ),
            }
        ],
    )

    def unexpected_fallback(query):
        raise AssertionError("Llama must not run when results are found.")

    monkeypatch.setattr(cli, "run_fallback", unexpected_fallback)

    exit_code = cli.run_search(make_args(tmp_path))

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "reader.py:1" in output
    assert "read_file" in output


def test_no_results_trigger_llm(tmp_path, monkeypatch):
    """An unsuccessful semantic search should invoke Llama."""
    chunks = [{"name": "unrelated_function"}]
    embeddings = np.ones((1, 384))
    fallback_calls = []

    monkeypatch.setattr(
        cli,
        "index_folder",
        lambda *args, **kwargs: (chunks, embeddings),
    )
    monkeypatch.setattr(cli, "search", lambda *args, **kwargs: [])
    monkeypatch.setattr(
        cli,
        "run_fallback",
        lambda query: fallback_calls.append(query) or 0,
    )

    exit_code = cli.run_search(make_args(tmp_path))

    assert exit_code == 0
    assert fallback_calls == ["find code that safely reads a file"]


def test_empty_archive_triggers_llm(tmp_path, monkeypatch):
    """An archive with no searchable Python chunks should invoke Llama."""
    fallback_calls = []

    monkeypatch.setattr(
        cli,
        "index_folder",
        lambda *args, **kwargs: ([], np.array([])),
    )
    monkeypatch.setattr(
        cli,
        "run_fallback",
        lambda query: fallback_calls.append(query) or 0,
    )

    exit_code = cli.run_search(make_args(tmp_path))

    assert exit_code == 0
    assert len(fallback_calls) == 1


def test_no_llm_disables_fallback(tmp_path, monkeypatch):
    """The --no-llm option should prevent fallback on an empty archive."""
    monkeypatch.setattr(
        cli,
        "index_folder",
        lambda *args, **kwargs: ([], np.array([])),
    )

    def unexpected_fallback(query):
        raise AssertionError("Fallback should be disabled.")

    monkeypatch.setattr(cli, "run_fallback", unexpected_fallback)

    exit_code = cli.run_search(make_args(tmp_path, no_llm=True))

    assert exit_code == 1


def test_missing_path_does_not_trigger_llm(tmp_path, monkeypatch):
    """A missing source path is an error, not a search miss."""
    missing_path = tmp_path / "does-not-exist"

    def unexpected_fallback(query):
        raise AssertionError("A missing path must not trigger Llama.")

    monkeypatch.setattr(cli, "run_fallback", unexpected_fallback)

    exit_code = cli.run_search(make_args(missing_path))

    assert exit_code == 2


def test_zip_file_is_indexed_as_zip(tmp_path, monkeypatch):
    """ZIP archives should be passed to the ZIP indexer."""
    archive = tmp_path / "project.zip"
    archive.touch()

    chunks = [{"name": "read_file"}]
    embeddings = np.ones((1, 384))
    calls = []

    monkeypatch.setattr(
        cli,
        "index_zip",
        lambda path, **kwargs: calls.append(path) or (chunks, embeddings),
    )
    monkeypatch.setattr(
        cli,
        "search",
        lambda *args, **kwargs: [
            {
                "score": 0.9,
                "file": "reader.py",
                "start_line": 1,
                "type": "function",
                "name": "read_file",
                "code": "def read_file(): pass",
            }
        ],
    )

    exit_code = cli.run_search(make_args(archive))

    assert exit_code == 0
    assert calls == [archive]
