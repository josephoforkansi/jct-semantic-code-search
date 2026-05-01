# tests/test_embedding.py

from jct.embedding import embed_texts


def test_embedding_output_shape():
    """Embedding function should return vectors for each input."""
    texts = ["hello world", "semantic search"]

    vectors = embed_texts(texts)

    assert len(vectors) == 2
    assert len(vectors[0]) > 0


def test_embedding_consistency():
    """Embedding should return same number of vectors as input texts."""
    texts = ["test one", "test two", "test three"]

    vectors = embed_texts(texts)

    assert len(vectors) == len(texts)