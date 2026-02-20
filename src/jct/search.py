# src/jct/search.py
from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import List, Dict

MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)

def search(
    query: str,
    chunks: List[Dict],
    embeddings: np.ndarray,
    top_k: int = 5,
    min_score: float = 0.5
) -> List[Dict]:
    """Find top-k most similar chunks to the query."""
    if len(chunks) == 0 or embeddings.size == 0 or len(embeddings) == 0:
        return []

    query_emb = model.encode([query])[0]
    cos_scores = util.cos_sim(query_emb, embeddings)[0]

    # Safe descending sort and slice
    sorted_indices = np.argsort(-cos_scores)  # Negative for descending
    top_indices = sorted_indices[:top_k]

    results = []
    for idx in top_indices:
        score = cos_scores[idx].item()
        if score < min_score:
            break
        chunk = chunks[idx].copy()
        chunk["score"] = round(score, 3)
        results.append(chunk)

    return results