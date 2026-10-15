
"""Semantic search over Python code chunks."""

import re
from typing import Dict, List

import numpy as np

from .embedding import get_model

# Only correct common natural-language search terms.
# Do not use a general-purpose vocabulary that could rewrite identifiers.
TYPO_VOCABULARY = (
    "look",
    "find",
    "search",
    "show",
    "where",
    "class",
    "function",
    "method",
    "defined",
    "definition",
    "interface",
    "file",
    "error",
    "read",
    "write",
)

# Words that should be removed from natural-language queries.
FILLER_WORDS = {
    "show",
    "me",
    "find",
    "look",
    "search",
    "please",
    "where",
    "can",
    "you",
    "is",
    "the",
    "around",
    "for",
}

QUERY_SYNONYMS = {
    "interface": ["class", "definition", "declaration"],
    "defined": ["definition", "declared", "implemented"],
    "function": ["method", "procedure"],
    "error": ["exception", "failure"],
    "read": ["load", "retrieve"],
    "write": ["save", "store"],
    "file": ["document", "path"],
    "loop": ["iteration", "repeat"],
    "sort": ["ordering", "arrange"],
    "search": ["find", "lookup", "retrieve"],
}


def normalize_query(query: str) -> str:
    """Normalize whitespace and capitalization."""
    return re.sub(r"\s+", " ", query.strip().lower())


def _edit_distance(first: str, second: str) -> int:
    """Calculate the Levenshtein edit distance between two words."""
    previous_row = list(range(len(second) + 1))

    for i, first_char in enumerate(first, start=1):
        current_row = [i]

        for j, second_char in enumerate(second, start=1):
            insert_cost = current_row[j - 1] + 1
            delete_cost = previous_row[j] + 1
            replace_cost = previous_row[j - 1] + (
                first_char != second_char
            )

            current_row.append(
                min(insert_cost, delete_cost, replace_cost)
            )

        previous_row = current_row

    return previous_row[-1]


def correct_typos(query: str) -> str:
    """
    Correct likely misspellings of a small set of ordinary query words.

    Tokens that look like identifiers, dotted names, or function calls
    are preserved. Plural forms of known vocabulary words are preserved.
    """
    if not query.strip():
        return query

    def replace_word(match: re.Match) -> str:
        word = match.group(0)
        start, end = match.span()

        # Preserve words attached to identifier punctuation.
        if start > 0 and (
            query[start - 1].isalnum()
            or query[start - 1] in "_."
        ):
            return word

        if end < len(query) and (
            query[end].isalnum()
            or query[end] in "_.("
        ):
            return word

        lower_word = word.lower()

        # Preserve plural forms of known vocabulary words.
        if (
            lower_word.endswith("s")
            and lower_word[:-1] in TYPO_VOCABULARY
        ):
            return word

        if lower_word in TYPO_VOCABULARY:
            return word

        # Only consider alphabetic words of reasonable length.
        if not 4 <= len(word) <= 10 or not word.isalpha():
            return word

        distances = [
            (candidate, _edit_distance(lower_word, candidate))
            for candidate in TYPO_VOCABULARY
        ]

        best_distance = min(distance for _, distance in distances)

        if best_distance > 2:
            return word

        best_matches = [
            candidate
            for candidate, distance in distances
            if distance == best_distance
        ]

        # Avoid guessing if multiple candidates are equally close.
        if len(best_matches) != 1:
            return word

        corrected = best_matches[0]

        if word[0].isupper():
            return corrected.capitalize()

        return corrected

    return re.sub(r"[A-Za-z]+", replace_word, query)


def expand_query(query: str) -> str:
    """Remove conversational filler and add relevant search synonyms."""
    expanded = normalize_query(query).strip(" ?!.,")
    if not expanded:
        return normalize_query(query)

    tokens = expanded.split()
    words = [
        token for token in tokens
        if token not in FILLER_WORDS
    ]

    additions = []

    for word in words:
        additions.extend(QUERY_SYNONYMS.get(word, []))

    unique_additions = [
        word
        for word in dict.fromkeys(additions)
        if word not in words
    ]

    words.extend(unique_additions)

    result = " ".join(words)
    return result or normalize_query(query)


def compute_score(query: str, chunk: Dict, cos_score: float) -> float:
    """Combine embedding similarity with a concept-match bonus."""
    query_lower = query.lower()
    concept_bonus = 0.0

    for concept in chunk.get("concepts", []):
        if concept.lower() in query_lower:
            concept_bonus += 0.1

    return cos_score + concept_bonus


def search(
    query: str,
    chunks: List[Dict],
    embeddings,
    top_k: int = 5,
    min_score: float = 0.5,
    use_query_expansion: bool = True,
    use_typo_correction: bool = True,
) -> List[Dict]:
    """Search code chunks with optional typo correction and expansion."""
    if not chunks or embeddings.size == 0:
        return []

    if top_k <= 0 or not query.strip():
        return []

    processed_query = query.strip()

    if use_typo_correction:
        processed_query = correct_typos(processed_query)

    if use_query_expansion:
        expanded_query = expand_query(processed_query)
    else:
        expanded_query = processed_query

    # Load the shared model only when an actual search is needed.
    model = get_model()

    query_embeddings = model.encode(
        [processed_query, expanded_query],
        convert_to_tensor=False,
        show_progress_bar=False,
    )

    # Ensure the query embeddings are a two-dimensional NumPy array.
    query_embeddings = np.asarray(query_embeddings)

    if (
        query_embeddings.ndim != 2
        or query_embeddings.shape[0] != 2
    ):
        raise ValueError(
            "The embedding model must return two embedding vectors."
        )

    # Import similarity utilities only when searching.
    from sentence_transformers import util

    original_scores = util.cos_sim(
        query_embeddings[0], embeddings
    )[0]

    expanded_scores = util.cos_sim(
        query_embeddings[1], embeddings
    )[0]

    scored_results = []

    for idx, chunk in enumerate(chunks):
        original_cosine = float(original_scores[idx].item())
        expanded_cosine = float(expanded_scores[idx].item())

        combined_cosine = (
            0.7 * original_cosine
            + 0.3 * expanded_cosine
        )

        final_score = compute_score(
            processed_query,
            chunk,
            combined_cosine,
        )

        if final_score >= min_score:
            result = chunk.copy()
            result["score"] = round(final_score, 3)
            result["cos_score"] = round(combined_cosine, 3)
            scored_results.append(result)

    scored_results.sort(
        key=lambda result: result["score"],
        reverse=True,
    )

    return scored_results[:top_k]


if __name__ == "__main__":
    example_query = "lppk for code that handles errors"
    print("Original:", example_query)

    corrected_query = correct_typos(example_query)
    print("Corrected:", corrected_query)
    print("Expanded:", expand_query(corrected_query))
