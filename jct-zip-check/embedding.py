
"""Lazy, shared embedding model for JCT."""

from functools import lru_cache
from typing import List

import numpy as np

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model():
    """Load the Sentence Transformer once, when first needed."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def embed_texts(texts: List[str]) -> np.ndarray:
    """Convert a list of texts to dense vectors."""
    return get_model().encode(
        texts,
        convert_to_tensor=False,
        show_progress_bar=True,
    )
