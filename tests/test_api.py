"""Tests for the JCT programmatic search API."""

from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

from jct.api import search_code


@pytest.fixture
def fake_chunks() -> list[dict]:
    """Provide sample indexed code chunks."""
    return [
        {
            "name": "read_file",
            "file": "files.py",
            "start_line": 1,
            "end_line": 5,
            "code": "def read_file(path): return open(path).read()",
        },
        {
            "name": "write_file",
            "file": "files.py",
            "start_line": 7,
            "end_line": 11,
            "code": "def write_file(path, data): open(path, 'w').write(data)",
        },
    ]


@pytest.fixture
def fake_embeddings() -> np.ndarray:
    """Provide sample embeddings for the fake code chunks."""
    return np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        dtype=np.float32,
    )


@pytest.fixture
def mock_index(fake_chunks: list[dict], fake_embeddings: np.ndarray):
    """Mock folder and ZIP indexing without loading an embedding model."""
    with (
        patch(
            "jct.api.index_folder",
            return_value=(fake_chunks, fake_embeddings),
        ) as folder_index,
        patch(
            "jct.api.index_zip",
            return_value=(fake_chunks, fake_embeddings),
        ) as zip_index,
    ):
        yield folder_index, zip_index


@pytest.fixture
def mock_search_results() -> list[dict]:
    """Provide sample search results."""
    return [
        {
            "name": "read_file",
            "file": "files.py",
            "score": 0.92,
            "code": "def read_file(path): return open(path).read()",
        }
    ]


def test_search_code_rejects_empty_query() -> None:
    """An empty or whitespace-only query must be rejected."""
    with pytest.raises(ValueError, match="query must not be empty"):
        search_code("   ")


@pytest.mark.parametrize("top_k", [0, -1, -5])
def test_search_code_rejects_invalid_top_k(top_k: int) -> None:
    """top_k must be a positive integer."""
    with pytest.raises(ValueError, match="top_k must be greater than zero"):
        search_code("read a file", top_k=top_k)


@pytest.mark.parametrize("min_score", [-0.1, 1.1, 2.0])
def test_search_code_rejects_invalid_min_score(min_score: float) -> None:
    """min_score must be between zero and one."""
    with pytest.raises(ValueError, match="min_score must be between 0 and 1"):
        search_code("read a file", min_score=min_score)


@pytest.mark.parametrize("min_score", [0.0, 0.5, 1.0])
def test_search_code_accepts_valid_min_score(min_score: float) -> None:
    """Boundary values and an ordinary threshold should be accepted."""
    with patch("jct.api.Path") as mocked_path:
        source = mocked_path.return_value
        source.expanduser.return_value = source
        source.exists.return_value = True
        source.is_file.return_value = False
        source.is_dir.return_value = True

        with patch(
            "jct.api.index_folder",
            return_value=([], np.empty((0, 3))),
        ):
            results = search_code("read a file", min_score=min_score)

    assert results == []


def test_search_code_rejects_missing_path(tmp_path: Path) -> None:
    """A nonexistent source path must raise FileNotFoundError."""
    missing_path = tmp_path / "does_not_exist"

    with pytest.raises(FileNotFoundError, match="Source path does not exist"):
        search_code("read a file", path=missing_path)


def test_search_code_rejects_unsupported_file(tmp_path: Path) -> None:
    """A file that is not a ZIP archive must be rejected."""
    unsupported_file = tmp_path / "example.txt"
    unsupported_file.write_text("sample text", encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="The source must be a directory or a ZIP archive",
    ):
        search_code("read a file", path=unsupported_file)


def test_search_code_indexes_directory(
    tmp_path: Path,
    mock_index,
    mock_search_results: list[dict],
) -> None:
    """Directory searches should use folder indexing and return dictionaries."""
    folder_index, zip_index = mock_index

    with patch(
        "jct.api.search_with_reformulation",
        return_value=mock_search_results,
    ) as search_mock:
        results = search_code("read a file", path=tmp_path)

    folder_index.assert_called_once()
    zip_index.assert_not_called()
    search_mock.assert_called_once()

    assert results == mock_search_results
    assert all(isinstance(result, dict) for result in results)


def test_search_code_indexes_zip(
    tmp_path: Path,
    mock_index,
    mock_search_results: list[dict],
) -> None:
    """ZIP archive searches should use ZIP indexing."""
    folder_index, zip_index = mock_index
    archive = tmp_path / "project.zip"
    archive.touch()

    with patch(
        "jct.api.search_with_reformulation",
        return_value=mock_search_results,
    ) as search_mock:
        results = search_code("read a file", path=archive)

    zip_index.assert_called_once()
    folder_index.assert_not_called()
    search_mock.assert_called_once()

    assert results == mock_search_results


def test_search_code_uses_baseline_search(
    tmp_path: Path,
    mock_index,
    mock_search_results: list[dict],
) -> None:
    """Disabling query reformulation should use baseline search."""
    with (
        patch(
            "jct.api.search",
            return_value=mock_search_results,
        ) as baseline_search,
        patch("jct.api.search_with_reformulation") as reformulated_search,
    ):
        results = search_code(
            "read a file",
            path=tmp_path,
            use_query_reformulation=False,
        )

    baseline_search.assert_called_once()
    reformulated_search.assert_not_called()
    assert results == mock_search_results


def test_search_code_uses_reformulation_by_default(
    tmp_path: Path,
    mock_index,
    mock_search_results: list[dict],
) -> None:
    """Query reformulation should be enabled by default."""
    with (
        patch(
            "jct.api.search",
            return_value=mock_search_results,
        ) as baseline_search,
        patch(
            "jct.api.search_with_reformulation",
            return_value=mock_search_results,
        ) as reformulated_search,
    ):
        results = search_code("read a file", path=tmp_path)

    reformulated_search.assert_called_once()
    baseline_search.assert_not_called()
    assert results == mock_search_results


def test_search_code_returns_empty_list_when_no_chunks(
    tmp_path: Path,
    mock_index,
) -> None:
    """An empty index should return an empty list without searching."""
    with (
        patch(
            "jct.api.index_folder",
            return_value=([], np.empty((0, 3))),
        ),
        patch("jct.api.search") as baseline_search,
        patch("jct.api.search_with_reformulation") as reformulated_search,
    ):
        results = search_code("read a file", path=tmp_path)

    assert results == []
    baseline_search.assert_not_called()
    reformulated_search.assert_not_called()


def test_search_code_passes_search_options(
    tmp_path: Path,
    mock_index,
    mock_search_results: list[dict],
) -> None:
    """Search options should be forwarded to the search implementation."""
    with patch(
        "jct.api.search_with_reformulation",
        return_value=mock_search_results,
    ) as search_mock:
        search_code(
            "read a file",
            path=tmp_path,
            top_k=3,
            min_score=0.2,
            use_query_expansion=False,
            use_typo_correction=False,
            use_cache=False,
        )

    kwargs = search_mock.call_args.kwargs

    assert kwargs["top_k"] == 3
    assert kwargs["min_score"] == 0.2
    assert kwargs["use_query_expansion"] is False
    assert kwargs["use_typo_correction"] is False

    folder_index, _ = mock_index
    assert folder_index.call_args.kwargs["use_cache"] is False
