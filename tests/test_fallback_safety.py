
"""Regression tests for JCT's fallback safety rules."""

from jct import cli
from jct.llm_runtime import (
    _apply_output_safety,
    _explicitly_requests_code,
    _is_consensus_query,
)


def test_detects_consensus_queries() -> None:
    """Recognize common distributed consensus terminology."""
    assert _is_consensus_query(
        "Explain how distributed consensus works"
    )
    assert _is_consensus_query(
        "Describe the Paxos protocol"
    )
    assert _is_consensus_query(
        "Explain Raft leader election"
    )


def test_consensus_query_removes_code_even_if_requested() -> None:
    """Consensus requests must not return fenced code."""
    query = "Implement a Paxos consensus algorithm"

    answer = (
        "Paxos uses multiple protocol phases.\n"
        "```python\n"
        "class Consensus:\n"
        "    pass\n"
        "```\n"
        "The example is simplified."
    )

    safe_answer = _apply_output_safety(query, answer)

    assert "class Consensus" not in safe_answer
    assert "```python" not in safe_answer
    assert "JCT SAFETY NOTICE" in safe_answer
    assert "not provide an implementation" in safe_answer


def test_explanation_without_code_request_removes_code() -> None:
    """A conceptual question should not return a fenced code example."""
    query = "Explain how file handling works"

    answer = (
        "Files can be opened and read.\n"
        "```python\n"
        "open('example.txt')\n"
        "```\n"
    )

    safe_answer = _apply_output_safety(query, answer)

    assert "open('example.txt')" not in safe_answer
    assert "```" not in safe_answer
    assert "JCT SAFETY NOTICE" in safe_answer


def test_explicit_code_request_allows_non_consensus_code() -> None:
    """An explicit ordinary code request may return its code."""
    query = "Write Python code to read a text file"

    answer = (
        "AI-GENERATED, UNVERIFIED EXAMPLE\n"
        "```python\n"
        "with open('example.txt') as file:\n"
        "    content = file.read()\n"
        "```"
    )

    assert _explicitly_requests_code(query)
    assert _apply_output_safety(query, answer) == answer.strip()


def test_explanation_request_does_not_explicitly_request_code() -> None:
    """Conceptual explanations do not count as explicit code requests."""
    assert not _explicitly_requests_code(
        "Explain how file handling works"
    )


def test_cli_fallback_displays_unverified_label(
    monkeypatch,
    capsys,
) -> None:
    """Fallback output must be visibly labeled as unverified."""
    from jct import llm_runtime

    monkeypatch.setattr(
        llm_runtime,
        "generate_fallback",
        lambda query: "A generated explanation.",
    )

    result = cli.run_fallback("Explain file handling")
    output = capsys.readouterr().out

    assert result == 0
    assert "AI-GENERATED, UNVERIFIED" in output
    assert "not retrieved from your project or ZIP archive" in output
    assert "A generated explanation." in output
