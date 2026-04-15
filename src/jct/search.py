# src/jct/search.py
from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import List, Dict

MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)


def compute_score(query: str, chunk: Dict, cos_score: float) -> float:
    """Hybrid scoring: embedding similarity + concept match bonus."""
    query_lower = query.lower()
    concept_bonus = 0.0

    for concept in chunk.get("concepts", []):
        if concept in query_lower:
            concept_bonus += 0.1  # boost per matching concept

    return cos_score + concept_bonus


def search(
    query: str,
    chunks: List[Dict],
    embeddings: np.ndarray,
    top_k: int = 5,
    min_score: float = 0.5
) -> List[Dict]:
    """Find top-k most relevant chunks using hybrid scoring."""

    if len(chunks) == 0 or embeddings.size == 0:
        return []

    query_emb = model.encode([query])[0]
    cos_scores = util.cos_sim(query_emb, embeddings)[0]

    scored_results = []

    for idx, chunk in enumerate(chunks):
        cos_score = cos_scores[idx].item()

        # 🔥 NEW: hybrid score
        final_score = compute_score(query, chunk, cos_score)

        if final_score >= min_score:
            result = chunk.copy()
            result["score"] = round(final_score, 3)
            result["cos_score"] = round(cos_score, 3)
            scored_results.append(result)

    # Sort descending by score
    scored_results.sort(key=lambda x: x["score"], reverse=True)

    return scored_results[:top_k]