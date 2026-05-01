import numpy as np
from jct.embedding import embed_texts


def test_embed_texts_shape():
    texts = ["hello world", "semantic search"]
    embeddings = embed_texts(texts)

    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape[0] == 2