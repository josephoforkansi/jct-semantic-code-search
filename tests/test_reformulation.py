"""Tests for query reformulation."""

from jct.reformulation import reformulate_query


def test_empty_query_returns_no_alternatives():
    """Empty queries should produce no alternatives."""
    assert reformulate_query("") == []
    assert reformulate_query("   ") == []


def test_nonpositive_limit_returns_no_alternatives():
    """A nonpositive limit should produce no alternatives."""
    assert reformulate_query(
        "read a file",
        max_alternatives=0,
    ) == []

    assert reformulate_query(
        "read a file",
        max_alternatives=-1,
    ) == []


def test_file_query_generates_behavioral_alternatives():
    """File-related queries should produce file-related alternatives."""
    alternatives = reformulate_query(
        "Find code that reads a file"
    )

    assert alternatives

    assert any(
        "opens and reads a file" in alternative
        for alternative in alternatives
    )


def test_alternatives_are_unique():
    """Alternative queries should not contain duplicates."""
    alternatives = reformulate_query(
        "Find code that reads a file"
    )

    normalized = [
        alternative.strip().lower()
        for alternative in alternatives
    ]

    assert len(normalized) == len(set(normalized))


def test_original_query_is_not_returned():
    """The original query should not appear among its alternatives."""
    query = "Find code that reads a file"

    alternatives = reformulate_query(query)

    assert query.lower() not in [
        alternative.strip().lower()
        for alternative in alternatives
    ]


def test_alternative_limit_is_respected():
    """The number of alternatives should respect the requested limit."""
    alternatives = reformulate_query(
        "Find code that reads a file",
        max_alternatives=2,
    )

    assert len(alternatives) <= 2


def test_nonpositive_limit_does_not_return_results():
    """Negative limits should not return results."""
    assert reformulate_query(
        "Find code that reads a file",
        max_alternatives=-5,
    ) == []


def test_empty_query_with_limit_returns_no_results():
    """Whitespace-only queries should remain empty with a custom limit."""
    assert reformulate_query(
        "   ",
        max_alternatives=3,
    ) == []
