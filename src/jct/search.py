"""Semantic code search using embeddings, query expansion, and RRF."""

import re
from typing import Dict, List, Sequence, Tuple

import numpy as np

from jct.embedding import get_model
from jct.reformulation import reformulate_query


def normalize_query(query: str) -> str:
    """Normalize a query for comparison and deduplication."""
    return re.sub(r"\s+", " ", query.strip().lower())


def correct_typos(query: str) -> str:
    """Correct common spelling mistakes in a query."""
    corrections = {
        "lppk": "look",
        "funciton": "function",
        "retrive": "retrieve",
        "fiel": "file",
        "expection": "exception",
    }

    words = query.split()
    corrected = [corrections.get(word.lower(), word) for word in words]

    return " ".join(corrected)


def expand_query(query: str) -> str:
    """Expand a query by removing filler words and adding synonyms."""
    if not query:
        return ""

    expanded = query.lower().strip()

    # Remove common filler phrases and words.
    filler_phrases = [
        "show me",
        "find me",
        "tell me",
        "can you",
        "could you",
        "how do i",
        "how can i",
        "what is",
        "what are",
        "please",
        "show",
        "where",
        "the",
        "me",
        "is",
    ]

    for phrase in filler_phrases:
        expanded = re.sub(
            rf"\b{re.escape(phrase)}\b",
            "",
            expanded,
        )

    # Normalize whitespace after removing filler words.
    expanded = " ".join(expanded.split())

    # Add synonyms for common programming concepts.
    synonyms = {
        "interface": [
            "class",
            "definition",
            "declaration",
            "abstract",
            "protocol",
        ],
        "function": ["method", "def"],
        "method": ["function"],
        "file": ["document"],
        "error": ["exception"],
    }

    words = expanded.split()
    additional_words = []

    for word in words:
        if word in synonyms:
            additional_words.extend(synonyms[word])

    # Preserve original terms and append relevant synonyms.
    return " ".join(words + additional_words)


def _chunk_identity(result: Dict) -> Tuple:
    """Return an identity used to recognize duplicate code chunks."""
    return (
        result.get("file", ""),
        result.get("start_line", 0),
        result.get("name", ""),
        result.get("code", ""),
    )


def search(
    query: str,
    chunks: List[Dict],
    embeddings,
    top_k: int = 5,
    min_score: float = 0.5,
    use_query_expansion: bool = True,
    use_typo_correction: bool = True,
) -> List[Dict]:
    """
    Search code chunks using semantic similarity.

    Combines the original query embedding with an optional expanded
    query embedding, then ranks results by similarity.
    """
    if not chunks or top_k <= 0 or not query.strip():
        return []

    model = get_model()

    processed_query = (
        correct_typos(query) if use_typo_correction else query
    )

    expanded_query = (
        expand_query(processed_query)
        if use_query_expansion
        else processed_query
    )

    query_embedding = model.encode([processed_query])[0]
    expanded_embedding = model.encode([expanded_query])[0]

    query_embedding = np.asarray(query_embedding)
    expanded_embedding = np.asarray(expanded_embedding)

    chunk_embeddings = np.asarray(embeddings)

    if chunk_embeddings.ndim != 2 or len(chunk_embeddings) != len(chunks):
        raise ValueError(
            "The number of embeddings must match the number of code chunks."
        )

    query_norm = np.linalg.norm(query_embedding)
    expanded_norm = np.linalg.norm(expanded_embedding)
    chunk_norms = np.linalg.norm(chunk_embeddings, axis=1)

    query_norm = max(float(query_norm), 1e-12)
    expanded_norm = max(float(expanded_norm), 1e-12)
    chunk_norms = np.maximum(chunk_norms, 1e-12)

    original_similarities = (
        chunk_embeddings @ query_embedding
    ) / (chunk_norms * query_norm)

    expanded_similarities = (
        chunk_embeddings @ expanded_embedding
    ) / (chunk_norms * expanded_norm)

    scores = (
        0.7 * original_similarities
        + 0.3 * expanded_similarities
    )

    results = []

    for index, chunk in enumerate(chunks):
        score = float(scores[index])

        if score < min_score:
            continue

        result = chunk.copy()
        result["score"] = score
        results.append(result)

    results.sort(
        key=lambda result: result["score"],
        reverse=True,
    )

    return results[:top_k]


def reciprocal_rank_fusion(
    ranked_lists: Sequence[List[Dict]],
    top_k: int = 5,
    rrf_k: int = 60,
    weights: Sequence[float] | None = None,
) -> List[Dict]:
    """
    Combine ranked search-result lists using weighted reciprocal rank fusion.

    Each result receives a weighted contribution based on its rank
    in each result list. Duplicate chunks are combined by identity.
    """
    if top_k <= 0 or rrf_k < 0:
        return []

    if weights is None:
        weights = [1.0] * len(ranked_lists)

    if len(weights) != len(ranked_lists):
        raise ValueError(
            "The number of weights must match the number of ranked lists."
        )

    if any(weight < 0 for weight in weights):
        raise ValueError("RRF weights must be non-negative.")

    fused_results = {}
    accumulated_scores = {}
    best_similarities = {}

    for ranked_list, weight in zip(ranked_lists, weights):
        seen_in_list = set()

        for rank, result in enumerate(ranked_list, start=1):
            identity = _chunk_identity(result)

            # Do not count the same chunk twice in one ranked list.
            if identity in seen_in_list:
                continue

            seen_in_list.add(identity)

            if identity not in fused_results:
                fused_results[identity] = result.copy()
                accumulated_scores[identity] = 0.0
                best_similarities[identity] = float(
                    result.get("score", 0.0)
                )

            accumulated_scores[identity] += weight / (rrf_k + rank)

            best_similarities[identity] = max(
                best_similarities[identity],
                float(result.get("score", 0.0)),
            )

    results = []

    for identity, result in fused_results.items():
        result["score"] = accumulated_scores[identity]
        result["best_similarity"] = best_similarities[identity]
        result["fusion_method"] = "weighted_reciprocal_rank_fusion"
        results.append(result)

    results.sort(
        key=lambda result: result["score"],
        reverse=True,
    )

    return results[:top_k]


def search_with_reformulation(
    query: str,
    chunks: List[Dict],
    embeddings,
    top_k: int = 5,
    min_score: float = 0.5,
    use_query_expansion: bool = True,
    use_typo_correction: bool = True,
) -> List[Dict]:
    """
    Search using the original query and its reformulations.

    The original query receives weight 3.0, while each unique
    reformulated query receives weight 1.0 during fusion.
    """
    if not chunks or top_k <= 0 or not query.strip():
        return []

    alternatives = reformulate_query(query)

    queries = [query]
    weights = [3.0]
    seen_queries = {normalize_query(query)}

    for alternative in alternatives:
        normalized = normalize_query(alternative)

        if normalized and normalized not in seen_queries:
            seen_queries.add(normalized)
            queries.append(alternative)
            weights.append(1.0)

    ranked_lists = []

    for candidate_query in queries:
        results = search(
            candidate_query,
            chunks,
            embeddings,
            top_k=top_k,
            min_score=min_score,
            use_query_expansion=use_query_expansion,
            use_typo_correction=use_typo_correction,
        )

        ranked_lists.append(results)

    return reciprocal_rank_fusion(
        ranked_lists,
        top_k=top_k,
        weights=weights,
    )


if __name__ == "__main__":
    example_query = "lppk for code that handles errors"

    print("Original:", example_query)

    corrected_query = correct_typos(example_query)

    print("Corrected:", corrected_query)
    print("Expanded:", expand_query(corrected_query))
    print("Reformulated:", reformulate_query(corrected_query))
