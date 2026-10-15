"""Programmatic interface for JCT semantic code search."""

from pathlib import Path
from typing import Any

from jct.demo import index_folder, index_zip
from jct.search import search, search_with_reformulation


def search_code(
    query: str,
    path: str | Path = ".",
    top_k: int = 5,
    min_score: float = 0.5,
    use_query_reformulation: bool = True,
    use_query_expansion: bool = True,
    use_typo_correction: bool = True,
    use_cache: bool = True,
) -> list[dict[str, Any]]:
    """Search a Python project or ZIP archive programmatically.

    Args:
        query: Natural-language description of the desired code.
        path: Python project directory or ZIP archive.
        top_k: Maximum number of results to return.
        min_score: Minimum relevance threshold between 0 and 1.
        use_query_reformulation: Whether to reformulate the query
            and combine rankings.
        use_query_expansion: Whether to expand the search query.
        use_typo_correction: Whether to correct query typos.
        use_cache: Whether to use the saved index cache.

    Returns:
        A list of ranked code-search result dictionaries.

    Raises:
        ValueError: If the query or search parameters are invalid.
        FileNotFoundError: If the source path does not exist.
        ValueError: If the source is neither a directory nor a ZIP archive.
    """
    query = query.strip()

    if not query:
        raise ValueError("The search query must not be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    if not 0.0 <= min_score <= 1.0:
        raise ValueError("min_score must be between 0 and 1.")

    source_path = Path(path).expanduser()

    if not source_path.exists():
        raise FileNotFoundError(
            f"Source path does not exist: {source_path}"
        )

    if source_path.is_file() and source_path.suffix.lower() == ".zip":
        chunks, embeddings = index_zip(
            source_path,
            use_cache=use_cache,
        )

    elif source_path.is_dir():
        chunks, embeddings = index_folder(
            source_path,
            use_cache=use_cache,
        )

    else:
        raise ValueError(
            "The source must be a directory or a ZIP archive."
        )

    if not chunks:
        return []

    search_function = (
        search_with_reformulation
        if use_query_reformulation
        else search
    )

    results = search_function(
        query,
        chunks,
        embeddings,
        top_k=top_k,
        min_score=min_score,
        use_query_expansion=use_query_expansion,
        use_typo_correction=use_typo_correction,
    )

    # Return ordinary dictionaries suitable for use by other programs.
    return [dict(result) for result in results]
