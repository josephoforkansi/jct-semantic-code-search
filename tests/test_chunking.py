from jct.chunking import extract_chunks, detect_concepts
from pathlib import Path


def test_detect_concepts_basic():
    code = """
def foo():
    try:
        open("file.txt")
    except:
        pass
"""
    concepts = detect_concepts(code)

    assert "file_handling" in concepts
    assert "error_handling" in concepts


def test_extract_chunks_valid_file(tmp_path):
    file = tmp_path / "test.py"
    file.write_text("""
def hello():
    return "world"
""")

    chunks = extract_chunks(file)

    assert len(chunks) > 0
    assert chunks[0]["name"] == "hello"


def test_extract_chunks_invalid_file():
    chunks = extract_chunks("nonexistent.py")
    assert chunks == []