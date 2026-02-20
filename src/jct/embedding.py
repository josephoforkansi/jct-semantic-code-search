# src/jct/embedding.py
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

MODEL_NAME = "all-MiniLM-L6-v2"  # fast, small, good for code+text

model = SentenceTransformer(MODEL_NAME)

def embed_texts(texts: List[str]) -> np.ndarray:
    """Convert list of texts to dense vectors."""
    return model.encode(texts, convert_to_tensor=False, show_progress_bar=True)