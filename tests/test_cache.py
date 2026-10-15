
import json

import numpy as np
import pytest

from jct.cache import load_cache, save_cache


def sample_chunks():
    return [
        {
            "name": "example_function",
            "code": "def example_function():\n    return 1",
        }
    ]


def sample_embeddings():
    return np.array([[0.1, 0.2, 0.3]], dtype=np.float32)


def test_cache_round_trip(tmp_path):
    source = tmp_path / "project"
    source.mkdir()
    (source / "example.py").write_text(
        "def example_function():\n    return 1\n",
        encoding="utf-8",
    )

    chunks = sample_chunks()
    embeddings = sample_embeddings()

    save_cache(source, chunks, embeddings)
    result = load_cache(source)

    assert result is not None
    cached_chunks, cached_embeddings = result
    assert cached_chunks == chunks
    np.testing.assert_array_equal(cached_embeddings, embeddings)


def test_source_change_invalidates_cache(tmp_path):
    source = tmp_path / "project"
    source.mkdir()
    source_file = source / "example.py"
    source_file.write_text("x = 1\n", encoding="utf-8")

    save_cache(source, sample_chunks(), sample_embeddings())
    assert load_cache(source) is not None

    source_file.write_text("x = 2\n", encoding="utf-8")

    assert load_cache(source) is None


def test_corrupted_metadata_returns_cache_miss(tmp_path):
    source = tmp_path / "project"
    source.mkdir()
    (source / "example.py").write_text(
        "x = 1\n",
        encoding="utf-8",
    )

    save_cache(source, sample_chunks(), sample_embeddings())

    metadata_path = next(source.rglob("index.json"))
    metadata_path.write_text("{invalid json", encoding="utf-8")

    assert load_cache(source) is None


def test_corrupted_embeddings_return_cache_miss(tmp_path):
    source = tmp_path / "project"
    source.mkdir()
    (source / "example.py").write_text(
        "x = 1\n",
        encoding="utf-8",
    )

    save_cache(source, sample_chunks(), sample_embeddings())

    embeddings_path = next(source.rglob("embeddings.npy"))
    embeddings_path.write_bytes(b"not a valid numpy file")

    assert load_cache(source) is None


def test_save_rejects_mismatched_chunk_count(tmp_path):
    source = tmp_path / "project"
    source.mkdir()
    (source / "example.py").write_text(
        "x = 1\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="matching row counts"):
        save_cache(
            source,
            sample_chunks() * 2,
            sample_embeddings(),
        )
