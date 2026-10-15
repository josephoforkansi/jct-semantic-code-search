
"""Manage JCT's private Ollama runtime and safe Llama fallback."""

from __future__ import annotations

import json
import os
import platform
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zipfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

MODEL_NAME = "llama3.2"
OLLAMA_HOST = "127.0.0.1:11435"
OLLAMA_API = f"http://{OLLAMA_HOST}"

RUNTIME_URL = (
    "https://github.com/ollama/ollama/releases/latest/download/"
    "ollama-windows-amd64.zip"
)

CONSENSUS_TERMS = (
    "distributed consensus",
    "consensus algorithm",
    "consensus protocol",
    "paxos",
    "raft",
    "byzantine fault tolerance",
    "byzantine fault-tolerant",
    "byzantine consensus",
    "leader election",
    "distributed agreement",
)

CODE_REQUEST_PATTERNS = (
    r"\bwrite\s+(?:me\s+)?(?:some\s+)?code\b",
    r"\bgenerate\s+(?:some\s+)?code\b",
    r"\bshow\s+(?:me\s+)?(?:the\s+)?code\b",
    r"\bprovide\s+(?:me\s+)?(?:some\s+)?code\b",
    r"\bcode\s+example\b",
    r"\bexample\s+code\b",
    r"\bimplement(?:ation)?\b",
    r"\bwrite\s+(?:a|an)\s+(?:python\s+)?"
    r"(?:function|class|script|program|module)\b",
    r"\bcreate\s+(?:a|an)\s+(?:python\s+)?"
    r"(?:function|class|script|program|module)\b",
    r"\bbuild\s+(?:a|an)\s+(?:python\s+)?"
    r"(?:function|class|script|program|module)\b",
    r"\bshow\s+me\s+how\s+to\s+code\b",
    r"\bpython\s+code\b",
)

CODE_FENCE_PATTERN = re.compile(
    r"^[ \t]*(```|~~~)[^\n]*\n.*?"
    r"^[ \t]*\1[ \t]*$",
    flags=re.MULTILINE | re.DOTALL,
)


def _is_consensus_query(query: str) -> bool:
    """Identify requests concerning distributed consensus protocols."""
    normalized = query.casefold()

    return any(term in normalized for term in CONSENSUS_TERMS)


def _explicitly_requests_code(query: str) -> bool:
    """Check whether the user explicitly asks for code or implementation."""
    return any(
        re.search(pattern, query, flags=re.IGNORECASE)
        for pattern in CODE_REQUEST_PATTERNS
    )


def _remove_code_blocks(answer: str) -> str:
    """Remove fenced code blocks from a generated answer."""
    cleaned = CODE_FENCE_PATTERN.sub(
        "[Code block omitted by JCT's output safety guard.]",
        answer,
    )

    return cleaned.strip()


def _apply_output_safety(query: str, answer: str) -> str:
    """Apply deterministic code-output restrictions to generated answers."""
    if _is_consensus_query(query):
        cleaned = _remove_code_blocks(answer)

        notice = (
            "\n\nJCT SAFETY NOTICE: Code generation is disabled for "
            "distributed consensus queries. This response is explanatory "
            "and does not provide an implementation of Paxos, Raft, "
            "or another distributed consensus protocol."
        )

        return cleaned + notice

    if not _explicitly_requests_code(query):
        cleaned = _remove_code_blocks(answer)

        if cleaned != answer.strip():
            cleaned += (
                "\n\nJCT SAFETY NOTICE: Code was omitted because your "
                "request did not explicitly ask for code. Ask JCT for "
                "a code example if you want generated code."
            )

        return cleaned

    return answer.strip()


def get_data_dir() -> Path:
    """Return JCT's per-user application-data directory."""
    if sys.platform == "win32":
        base = Path(
            os.environ.get(
                "LOCALAPPDATA",
                str(Path.home() / "AppData" / "Local"),
            )
        )
    else:
        base = Path.home() / ".local" / "share"

    return base / "JCT"


def get_runtime_dir() -> Path:
    """Return the directory containing JCT's private Ollama runtime."""
    return get_data_dir() / "ollama"


def get_ollama_executable() -> Path:
    """Return the expected path to the Ollama executable."""
    return get_runtime_dir() / "ollama.exe"


def _safe_extract_zip(archive: Path, destination: Path) -> None:
    """Extract a ZIP while rejecting paths outside the destination."""
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()

    with zipfile.ZipFile(archive) as zipped:
        for member in zipped.infolist():
            target = (destination / member.filename).resolve()

            if not target.is_relative_to(root):
                raise RuntimeError(
                    "The Ollama archive contains an unsafe file path."
                )

        zipped.extractall(destination)


def install_runtime() -> Path:
    """Download the private Ollama runtime for Windows x86-64."""
    if sys.platform != "win32":
        raise RuntimeError(
            "The JCT-managed Ollama installer currently supports "
            "Windows only."
        )

    if platform.machine().lower() not in {"amd64", "x86_64"}:
        raise RuntimeError(
            "The current JCT Ollama download supports Windows x86-64 only."
        )

    runtime_dir = get_runtime_dir()
    executable = get_ollama_executable()

    if executable.is_file():
        return executable

    data_dir = get_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    runtime_dir.mkdir(parents=True, exist_ok=True)

    archive_path = data_dir / "ollama-download.zip"
    temporary_path = data_dir / "ollama-download.zip.part"

    print("Downloading the Ollama runtime for JCT...")

    try:
        request = urllib.request.Request(
            RUNTIME_URL,
            headers={"User-Agent": "JCT-Semantic-Code-Search"},
        )

        with urllib.request.urlopen(request, timeout=60) as response:
            with temporary_path.open("wb") as output:
                while True:
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    output.write(block)

        temporary_path.replace(archive_path)
        _safe_extract_zip(archive_path, runtime_dir)

        if not executable.is_file():
            raise RuntimeError(
                "The downloaded Ollama archive did not contain "
                "ollama.exe at its root."
            )

        print(f"Ollama runtime installed at: {runtime_dir}")
        return executable

    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise

    finally:
        archive_path.unlink(missing_ok=True)


def _runtime_environment() -> dict[str, str]:
    """Create an environment for JCT's private Ollama instance."""
    env = os.environ.copy()
    env["OLLAMA_HOST"] = OLLAMA_HOST
    env["OLLAMA_MODELS"] = str(get_data_dir() / "models")
    return env


def _port_is_available() -> bool:
    """Return whether JCT's dedicated port can be bound."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", 11435))
            return True
        except OSError:
            return False


def _api_get(path: str, timeout: float = 2.0) -> dict[str, Any]:
    """Read a JSON response from JCT's private Ollama API."""
    request = urllib.request.Request(f"{OLLAMA_API}{path}")

    with urllib.request.urlopen(request, timeout=timeout) as response:
        result = json.loads(response.read().decode("utf-8"))

    if not isinstance(result, dict):
        raise RuntimeError("Ollama returned an unexpected response.")

    return result


@contextmanager
def _running_server() -> Iterator[tuple[Path, dict[str, str]]]:
    """Run JCT's private Ollama server for one operation, then stop it."""
    executable = install_runtime()

    if not _port_is_available():
        raise RuntimeError(
            "JCT's dedicated port 11435 is already in use. "
            "JCT will not connect to an unverified Ollama service. "
            "Stop the conflicting process and try again."
        )

    runtime_dir = get_runtime_dir()
    log_path = runtime_dir / "server.log"
    env = _runtime_environment()
    creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    with log_path.open("ab") as log_file:
        process = subprocess.Popen(
            [str(executable), "serve"],
            cwd=str(runtime_dir),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            creationflags=creation_flags,
        )

    try:
        for _ in range(60):
            if process.poll() is not None:
                raise RuntimeError(
                    "JCT's Ollama process exited unexpectedly. "
                    f"Check the log at {log_path}"
                )

            try:
                _api_get("/api/version")
                break
            except (
                OSError,
                urllib.error.URLError,
                TimeoutError,
            ):
                time.sleep(1)
        else:
            raise RuntimeError(
                "JCT's Ollama server did not become ready within "
                f"60 seconds. Check the log at {log_path}"
            )

        yield executable, env

    finally:
        if process.poll() is None:
            process.terminate()

            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def setup_model() -> None:
    """Install the runtime and download the configured Llama model."""
    with _running_server() as (executable, env):
        print(
            f"Downloading model {MODEL_NAME}. "
            "The initial download may take several minutes."
        )

        subprocess.run(
            [str(executable), "pull", MODEL_NAME],
            env=env,
            cwd=str(get_runtime_dir()),
            check=True,
            timeout=None,
        )

    print(f"JCT is ready to use {MODEL_NAME}.")


def generate_fallback(query: str) -> str:
    """Generate a response with application-level output safeguards."""
    is_consensus = _is_consensus_query(query)
    allows_code = (
        _explicitly_requests_code(query) and not is_consensus
    )

    if is_consensus:
        task_instruction = (
            "Explain the concepts and design of distributed consensus. "
            "Do not provide source code, pseudocode, or code blocks. "
            "You may explain Paxos or Raft at a conceptual level. "
            "Describe protocol roles, phases, quorum requirements, and "
            "limitations accurately. Do not claim a toy simulation is "
            "a genuine consensus implementation."
        )
    elif allows_code:
        task_instruction = (
            "The user explicitly requested code. You may provide an "
            "AI-generated example, but explain assumptions and limitations. "
            "Do not claim the code was tested or verified."
        )
    else:
        task_instruction = (
            "Explain the topic in ordinary prose. Do not provide source "
            "code, pseudocode, or fenced code blocks because the user did "
            "not explicitly request code."
        )

    prompt = f"""
You are JCT's AI fallback assistant.

JCT searched the user's project or ZIP archive but did not find code
that met its relevance threshold.

User request:
{query}

Response instructions:
{task_instruction}

General rules:
- Do not claim you inspected files that were not supplied to you.
- Do not claim generated content was retrieved from the user's archive.
- Do not invent test results, benchmark results, or correctness guarantees.
- Clearly distinguish a conceptual explanation from an implementation.
- Prefer a concise and accurate answer over a long, speculative answer.
- If uncertain, state the uncertainty.
"""

    with _running_server():
        payload = json.dumps(
            {
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_ctx": 1024,
                    "num_batch": 128,
                },
            }
        ).encode("utf-8")

        request = urllib.request.Request(
            f"{OLLAMA_API}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=600,
            ) as response:
                result = json.loads(response.read().decode("utf-8"))

        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise RuntimeError(
                    f"The {MODEL_NAME} model is not installed. "
                    "Run `uv run jct setup` first."
                ) from exc

            if exc.code == 500:
                raise RuntimeError(
                    "Ollama could not generate a response. This may be "
                    "caused by insufficient available RAM. Close other "
                    "applications and check the JCT server log at "
                    f"{get_runtime_dir() / 'server.log'}"
                ) from exc

            raise RuntimeError(
                f"The Ollama API request failed: {exc}"
            ) from exc

        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError(
                f"Could not contact JCT's Ollama service: {exc}"
            ) from exc

        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Ollama returned an invalid JSON response."
            ) from exc

    answer = result.get("response", "").strip()

    if not answer:
        raise RuntimeError("Llama returned an empty response.")

    return _apply_output_safety(query, answer)
