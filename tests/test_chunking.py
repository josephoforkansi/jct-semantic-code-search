# tests/test_chunking.py

from jct.chunking import extract_chunks
from pathlib import Path


def test_extract_chunks_valid_file():
    """Chunk extraction should return structured data for valid Python files."""
    file_path = Path("demo_codebase/file_handler.py")

    chunks = extract_chunks(file_path)

    assert isinstance(chunks, list)

    if chunks:
        chunk = chunks[0]
        assert "file" in chunk
        assert "code" in chunk
        assert "text" in chunk
        assert "start_line" in chunk


def test_extract_chunks_invalid_file():
    """Chunk extraction should gracefully handle invalid file paths."""
    chunks = extract_chunks("non_existent_file.py")

    assert chunks == []


def test_extract_chunks_non_python_file():
    """Chunk extraction should ignore non-Python files."""
    chunks = extract_chunks("README.md")

    assert chunks == []