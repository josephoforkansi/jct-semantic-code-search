
from pathlib import Path
import zipfile

import numpy as np
import pytest

from jct import demo


def fake_chunk(file_path: Path) -> dict:
    """Create a representative code chunk for testing."""
    return {
        "file": file_path.name,
        "name": "example_function",
        "type": "function",
        "code": "def example_function():\n    return True",
        "docstring": "Example function.",
        "concepts": [],
        "text": "example function",
        "start_line": 1,
    }


def test_index_folder_indexes_python_files(tmp_path, monkeypatch):
    """A valid folder should be indexed and embedded."""
    source_file = tmp_path / "example.py"
    source_file.write_text(
        "def example_function():\n    return True\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        demo,
        "extract_chunks",
        lambda path: [fake_chunk(path)],
    )
    monkeypatch.setattr(
        demo,
        "embed_texts",
        lambda texts: np.array([[1.0, 0.0]]),
    )

    chunks, embeddings = demo.index_folder(tmp_path)

    assert len(chunks) == 1
    assert chunks[0]["file"] == "example.py"
    assert embeddings.shape == (1, 2)


def test_index_folder_handles_missing_directory(tmp_path):
    """A nonexistent directory should return empty results."""
    chunks, embeddings = demo.index_folder(tmp_path / "missing")

    assert chunks == []
    assert embeddings.size == 0


def test_index_folder_rejects_file_path(tmp_path):
    """A file path should not be accepted as a directory."""
    file_path = tmp_path / "example.py"
    file_path.write_text("# Example\n", encoding="utf-8")

    chunks, embeddings = demo.index_folder(file_path)

    assert chunks == []
    assert embeddings.size == 0


def test_index_folder_handles_empty_directory(tmp_path, monkeypatch):
    """An empty directory should not trigger embedding generation."""
    monkeypatch.setattr(demo, "extract_chunks", lambda path: [])

    def unexpected_embedding_call(texts):
        pytest.fail("Embeddings should not be generated for empty results")

    monkeypatch.setattr(demo, "embed_texts", unexpected_embedding_call)

    chunks, embeddings = demo.index_folder(tmp_path)

    assert chunks == []
    assert embeddings.size == 0


def test_index_folder_skips_excluded_directories(tmp_path, monkeypatch):
    """Excluded directories should not be indexed."""
    source_dir = tmp_path / "src"
    source_dir.mkdir()
    (source_dir / "kept.py").write_text("# Keep\n", encoding="utf-8")

    excluded_dir = tmp_path / ".venv"
    excluded_dir.mkdir()
    (excluded_dir / "ignored.py").write_text("# Ignore\n", encoding="utf-8")

    processed_files = []

    def fake_extract_chunks(file_path):
        processed_files.append(Path(file_path).name)
        return [fake_chunk(file_path)]

    monkeypatch.setattr(demo, "extract_chunks", fake_extract_chunks)
    monkeypatch.setattr(
        demo,
        "embed_texts",
        lambda texts: np.array([[1.0, 0.0]]),
    )

    chunks, embeddings = demo.index_folder(tmp_path)

    assert processed_files == ["kept.py"]
    assert len(chunks) == 1
    assert chunks[0]["file"] == "src/kept.py"
    assert embeddings.shape == (1, 2)


def test_index_zip_indexes_python_files(tmp_path, monkeypatch):
    """A valid ZIP should be indexed without extracting its files."""
    archive_path = tmp_path / "project.zip"

    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(
            "src/helpers.py",
            "def example_function():\n    return True\n",
        )
        archive.writestr("README.md", "# Example project\n")

    processed_files = []

    def fake_extract_source(source, file_name):
        processed_files.append(file_name)
        return [{
            "file": file_name,
            "name": "example_function",
            "type": "function",
            "code": source,
            "docstring": "",
            "concepts": [],
            "text": source,
            "start_line": 1,
        }]

    monkeypatch.setattr(
        demo,
        "extract_chunks_from_source",
        fake_extract_source,
    )
    monkeypatch.setattr(
        demo,
        "embed_texts",
        lambda texts: np.array([[1.0, 0.0]]),
    )

    chunks, embeddings = demo.index_zip(archive_path)

    assert len(chunks) == 1
    assert chunks[0]["file"] == "src/helpers.py"
    assert processed_files == ["src/helpers.py"]
    assert embeddings.shape == (1, 2)

    # The ZIP member should not have been extracted to disk.
    assert not (tmp_path / "src" / "helpers.py").exists()


def test_index_zip_rejects_invalid_archive(tmp_path):
    """A non-ZIP file should return empty results."""
    archive_path = tmp_path / "invalid.zip"
    archive_path.write_text("This is not a ZIP file.", encoding="utf-8")

    chunks, embeddings = demo.index_zip(archive_path)

    assert chunks == []
    assert embeddings.size == 0


def test_index_zip_handles_archive_without_python_files(tmp_path, monkeypatch):
    """An archive without Python files should return empty results."""
    archive_path = tmp_path / "docs.zip"

    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("README.md", "# Documentation\n")
        archive.writestr("notes.txt", "Some notes.")

    def unexpected_embedding_call(texts):
        pytest.fail("Embeddings should not be generated for empty results")

    monkeypatch.setattr(demo, "embed_texts", unexpected_embedding_call)

    chunks, embeddings = demo.index_zip(archive_path)

    assert chunks == []
    assert embeddings.size == 0


def test_index_zip_skips_unsafe_paths(tmp_path, monkeypatch):
    """Path-traversal entries should not be processed or extracted."""
    archive_path = tmp_path / "unsafe.zip"

    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(
            "../outside.py",
            "def unsafe_function():\n    return True\n",
        )
        archive.writestr(
            "src/safe.py",
            "def safe_function():\n    return True\n",
        )

    processed_files = []

    def fake_extract_source(source, file_name):
        processed_files.append(file_name)
        return [{
            "file": file_name,
            "name": "safe_function",
            "type": "function",
            "code": source,
            "docstring": "",
            "concepts": [],
            "text": source,
            "start_line": 1,
        }]

    monkeypatch.setattr(
        demo,
        "extract_chunks_from_source",
        fake_extract_source,
    )
    monkeypatch.setattr(
        demo,
        "embed_texts",
        lambda texts: np.array([[1.0, 0.0]]),
    )

    chunks, embeddings = demo.index_zip(archive_path)

    assert processed_files == ["src/safe.py"]
    assert len(chunks) == 1
    assert chunks[0]["file"] == "src/safe.py"
    assert embeddings.shape == (1, 2)
    assert not (tmp_path.parent / "outside.py").exists()
