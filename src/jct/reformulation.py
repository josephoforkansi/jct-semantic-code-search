"""Generate alternative natural-language formulations for code search."""

import re
from typing import List

# Map behavioral terms to related code-search terminology.
BEHAVIOR_SYNONYMS = {
    "read": ["load", "retrieve", "extract"],
    "write": ["save", "store", "persist"],
    "find": ["locate", "identify", "search"],
    "search": ["find", "locate", "lookup"],
    "sort": ["order", "arrange"],
    "validate": ["check", "verify"],
    "handle": ["manage", "catch"],
    "create": ["build", "construct"],
    "remove": ["delete", "discard"],
    "calculate": ["compute", "evaluate"],
    "chunk": ["split", "divide", "partition"],
    "chunking": ["splitting", "partitioning", "segmentation"],
    "parse": ["analyze", "process", "interpret"],
    "extract": ["retrieve", "identify", "collect"],
    "detect": ["identify", "recognize", "find"],
    "convert": ["transform", "translate", "change"],
    "compare": ["match", "evaluate", "contrast"],
    "load": ["read", "retrieve", "import"],
    "save": ["write", "store", "persist"],
    "exception": ["error", "failure"],
    "exceptions": ["errors", "failures"],
    "function": ["method", "callable"],
    "functions": ["methods", "callables"],
    "class": ["type", "object definition"],
    "classes": ["types", "object definitions"],
    "ast": ["abstract syntax tree", "syntax tree"],
    "syntax": ["structure", "grammar"],
    "code": ["source code", "program"],
    "file": ["module", "source file"],
    "files": ["modules", "source files"],
}


# Templates for common programming behaviors and concepts.
BEHAVIOR_TEMPLATES = {
    "file": [
        "Find code that opens and reads a file.",
        "Find a function that loads file contents.",
        "Find code that uses a context manager for file access.",
        "Find code that handles errors when accessing a file.",
    ],
    "error": [
        "Find code that catches exceptions.",
        "Find a function that handles runtime failures.",
        "Find code that uses try and except.",
    ],
    "exception": [
        "Find code that catches exceptions.",
        "Find code that handles errors and failures.",
    ],
    "sort": [
        "Find code that orders a collection.",
        "Find a function that arranges elements by value.",
    ],
    "loop": [
        "Find code that repeats an operation.",
        "Find a function that iterates over a collection.",
    ],
    "ast": [
        "Find code that parses Python source using the AST module.",
        "Find a function that walks an abstract syntax tree.",
        "Find code that identifies function and class definitions in an AST.",
        "Find code that analyzes Python syntax trees.",
    ],
    "chunk": [
        "Find code that splits source code into chunks.",
        "Find a function that extracts functions and classes from Python code.",
        "Find code that divides a Python file into searchable code segments.",
        "Find code that creates chunks from Python source using AST nodes.",
    ],
    "chunking": [
        "Find code that splits source code into chunks.",
        "Find a function that extracts functions and classes from Python code.",
        "Find code that divides a Python file into searchable code segments.",
        "Find code that creates chunks from Python source using AST nodes.",
    ],
    "parse": [
        "Find code that parses Python source code.",
        "Find a function that converts source code into an AST.",
        "Find code that analyzes Python syntax.",
    ],
    "function": [
        "Find a Python function definition.",
        "Find code that extracts function definitions from source code.",
    ],
    "class": [
        "Find code that defines or extracts Python classes.",
        "Find code that identifies class definitions in Python source.",
    ],
}


def normalize_text(text: str) -> str:
    """Normalize whitespace and capitalization."""
    return re.sub(r"\s+", " ", text.strip().lower())


def reformulate_query(
    query: str,
    max_alternatives: int = 5,
) -> List[str]:
    """Generate alternative queries using deterministic rules.

    Alternatives come from programming-concept templates and terminology
    substitutions. The original query is excluded, and duplicate
    alternatives are removed.

    Args:
        query: The user's original natural-language query.
        max_alternatives: Maximum number of alternatives to return.

    Returns:
        A deduplicated list of alternative queries.
    """
    if not query.strip() or max_alternatives <= 0:
        return []

    normalized_query = normalize_text(query)
    alternatives: List[str] = []

    # Match complete words rather than arbitrary substrings.
    query_words = set(
        re.findall(r"\b[a-z0-9_]+\b", normalized_query)
    )

    # Add templates for concepts present in the query.
    for concept, templates in BEHAVIOR_TEMPLATES.items():
        if concept in query_words:
            alternatives.extend(templates)

    # Expand known programming terms.
    expanded_words = []

    for word in normalized_query.split():
        clean_word = word.strip(".,!?;:()[]{}\"'")

        replacements = BEHAVIOR_SYNONYMS.get(clean_word, [])

        if replacements:
            expanded_words.append(replacements[0])
        else:
            expanded_words.append(word)

    terminology_alternative = " ".join(expanded_words)

    if terminology_alternative != normalized_query:
        alternatives.append(terminology_alternative)

    # Generate a natural-language alternative for short concept queries.
    if len(query_words) <= 5:
        alternatives.append(
            f"Find Python code related to {normalized_query}."
        )

    # Remove duplicates while preserving their original order.
    unique_alternatives: List[str] = []
    seen = {normalized_query}

    for alternative in alternatives:
        normalized_alternative = normalize_text(alternative)

        if not normalized_alternative:
            continue

        if normalized_alternative in seen:
            continue

        seen.add(normalized_alternative)
        unique_alternatives.append(alternative)

        if len(unique_alternatives) >= max_alternatives:
            break

    return unique_alternatives
