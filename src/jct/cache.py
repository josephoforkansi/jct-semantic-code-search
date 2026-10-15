
"""Persistent storage for JCT code chunks and embeddings."""

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

CACHE_DIR_NAME = ".jct_cache"
CACHE_VERSION = 1

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    CACHE_DIR_NAME,
}


def _source_signature(source: Path) -> str:
    """Create a signature from source file paths and their contents."""
    digest = hashlib.sha256()

    if source.is_file():
        files = [source]
    elif source.is_dir():
        files = sorted(
            path
            for path in source.rglob("*.py")
            if not any(
                part in EXCLUDED_DIRS
                for part in path.relative_to(source).parts
            )
        )
    else:
        raise FileNotFoundError(
            f"Source does not exist: {source}"
        )

    for file_path in files:
        relative_path = (
            file_path.name
            if source.is_file()
            else file_path.relative_to(source).as_posix()
        )

        digest.update(relative_path.encode("utf-8"))
        digest.update(b"\0")

        try:
            content = file_path.read_bytes()
        except OSError as error:
            raise OSError(
                f"Cannot read source file for cache: {file_path}"
            ) from error

        digest.update(content)
        digest.update(b"\0")

    return digest.hexdigest()


def _cache_paths(source: Path) -> Tuple[Path, Path]:
    """Return cache metadata and embedding paths for a source."""
    source = source.resolve()

    identity = str(source)

    if source.is_file():
        cache_root = source.parent / CACHE_DIR_NAME
    else:
        cache_root = source / CACHE_DIR_NAME

    key = hashlib.sha256(
        identity.encode("utf-8")
    ).hexdigest()[:16]

    cache_dir = cache_root / key

    return (
        cache_dir / "index.json",
        cache_dir / "embeddings.npy",
    )


def load_cache(
    source: str | Path,
) -> Optional[Tuple[List[Dict], np.ndarray]]:
    """
    Load a valid cache.

    Return None when the cache is missing, stale, malformed, or unreadable.
    """
    source_path = Path(source).expanduser().resolve()

    if not source_path.exists():
        return None

    metadata_path, embeddings_path = _cache_paths(source_path)

    if not metadata_path.is_file() or not embeddings_path.is_file():
        return None

    try:
        metadata = json.loads(
            metadata_path.read_text(encoding="utf-8")
        )

        if not isinstance(metadata, dict):
            return None

        if metadata.get("cache_version") != CACHE_VERSION:
            return None

        current_signature = _source_signature(source_path)

        if metadata.get("source_signature") != current_signature:
            return None

        chunks = metadata.get("chunks")

        if not isinstance(chunks, list):
            return None

        if not all(isinstance(chunk, dict) for chunk in chunks):
            return None

        embeddings = np.load(
            embeddings_path,
            allow_pickle=False,
        )

        if not isinstance(embeddings, np.ndarray):
            return None

        if embeddings.ndim != 2:
            return None

        if len(chunks) != embeddings.shape[0]:
            return None

        return chunks, embeddings

    except (
        OSError,
        ValueError,
        TypeError,
        KeyError,
        EOFError,
        json.JSONDecodeError,
    ):
        return None


def save_cache(
    source: str | Path,
    chunks: List[Dict],
    embeddings: np.ndarray,
) -> None:
    """Atomically save chunks and embeddings for a source."""
    source_path = Path(source).expanduser().resolve()

    if not source_path.exists():
        raise FileNotFoundError(
            f"Source does not exist: {source_path}"
        )

    if not isinstance(embeddings, np.ndarray):
        raise TypeError("Embeddings must be a NumPy array.")

    if embeddings.ndim != 2 or len(chunks) != embeddings.shape[0]:
        raise ValueError(
            "Chunks and embeddings must have matching row counts."
        )

    if not all(isinstance(chunk, dict) for chunk in chunks):
        raise TypeError("Every chunk must be a dictionary.")

    metadata_path, embeddings_path = _cache_paths(source_path)
    cache_dir = metadata_path.parent
    cache_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "cache_version": CACHE_VERSION,
        "source_signature": _source_signature(source_path),
        "chunks": chunks,
    }

    metadata_temp_name = None
    embeddings_temp_name = None

    try:
        metadata_fd, metadata_temp_name = tempfile.mkstemp(
            prefix="index_",
            suffix=".tmp",
            dir=cache_dir,
        )

        embeddings_fd, embeddings_temp_name = tempfile.mkstemp(
            prefix="embeddings_",
            suffix=".tmp",
            dir=cache_dir,
        )

        with os.fdopen(
            metadata_fd,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                metadata,
                file,
                ensure_ascii=False,
            )

        with os.fdopen(embeddings_fd, "wb") as file:
            np.save(
                file,
                embeddings,
                allow_pickle=False,
            )

        # Replace the array first and metadata last. The metadata is the
        # final marker that the new cache is ready to be read.
        os.replace(embeddings_temp_name, embeddings_path)
        embeddings_temp_name = None

        os.replace(metadata_temp_name, metadata_path)
        metadata_temp_name = None

    finally:
        for temporary_name in (
            metadata_temp_name,
            embeddings_temp_name,
        ):
            if temporary_name is not None:
                try:
                    os.unlink(temporary_name)
                except FileNotFoundError:
                    pass
