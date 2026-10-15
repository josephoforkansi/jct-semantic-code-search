import argparse
import os
import zipfile
from datetime import datetime
from pathlib import Path, PurePosixPath

import numpy as np
from colorama import Fore, Style, init

from jct.cache import load_cache, save_cache
from jct.chunking import extract_chunks, extract_chunks_from_source
from jct.embedding import embed_texts
from jct.search import search

init(autoreset=True)

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".jct_cache",
}

MAX_ZIP_MEMBER_SIZE = 2 * 1024 * 1024
MAX_ZIP_TOTAL_SIZE = 50 * 1024 * 1024


def embed_chunks(chunks):
    """Generate embeddings for non-empty code chunks."""
    if not chunks:
        return [], np.array([])

    embeddings = embed_texts([chunk["text"] for chunk in chunks])
    return chunks, embeddings


def index_folder(
    folder: str | Path,
    use_cache: bool = True,
):
    """Index Python code in a directory, optionally using a saved cache."""
    folder_path = Path(folder).expanduser()

    if not folder_path.exists():
        print(Fore.RED + f"Error: Folder does not exist: {folder_path}")
        return [], np.array([])

    if not folder_path.is_dir():
        print(Fore.RED + f"Error: Path is not a directory: {folder_path}")
        return [], np.array([])

    root_path = folder_path.resolve()

    if use_cache:
        cached = load_cache(root_path)

        if cached is not None:
            chunks, embeddings = cached
            print(
                Fore.GREEN
                + f"Loaded {len(chunks)} cached code chunks from "
                + str(root_path)
            )
            return chunks, embeddings

    all_chunks = []

    for current_dir, dirs, files in os.walk(root_path):
        dirs[:] = sorted(
            directory
            for directory in dirs
            if directory not in EXCLUDED_DIRS
        )

        for filename in sorted(files):
            if not filename.lower().endswith(".py"):
                continue

            py_file = Path(current_dir) / filename
            chunks = extract_chunks(py_file)

            for chunk in chunks:
                chunk["file"] = py_file.relative_to(root_path).as_posix()

            all_chunks.extend(chunks)

    if not all_chunks:
        print(Fore.YELLOW + f"No Python code chunks found in {root_path}.")
        return [], np.array([])

    chunks, embeddings = embed_chunks(all_chunks)

    if use_cache:
        save_cache(root_path, chunks, embeddings)
        print(Fore.GREEN + "Saved index cache.")

    print(
        Fore.GREEN
        + f"Indexed {len(chunks)} code chunks from {root_path}"
    )

    return chunks, embeddings


def index_zip(
    archive_path: str | Path,
    use_cache: bool = True,
):
    """Index Python files from a ZIP archive, optionally using a cache."""
    archive_path = Path(archive_path).expanduser()

    if not archive_path.is_file():
        print(Fore.RED + f"Error: Archive does not exist: {archive_path}")
        return [], np.array([])

    if not zipfile.is_zipfile(archive_path):
        print(
            Fore.RED
            + f"Error: Invalid or unreadable ZIP archive: {archive_path}"
        )
        return [], np.array([])

    if use_cache:
        cached = load_cache(archive_path)

        if cached is not None:
            chunks, embeddings = cached
            print(
                Fore.GREEN
                + f"Loaded {len(chunks)} cached code chunks from "
                + archive_path.name
            )
            return chunks, embeddings

    all_chunks = []
    total_size = 0

    try:
        with zipfile.ZipFile(archive_path, "r") as archive:
            for member in sorted(
                archive.infolist(),
                key=lambda item: item.filename,
            ):
                if member.is_dir():
                    continue

                member_path = PurePosixPath(member.filename)

                # Reject absolute paths and path traversal.
                if member_path.is_absolute() or ".." in member_path.parts:
                    print(
                        Fore.YELLOW
                        + f"Skipping unsafe archive path: {member.filename}"
                    )
                    continue

                if not member_path.parts:
                    continue

                if any(
                    part in EXCLUDED_DIRS
                    for part in member_path.parts[:-1]
                ):
                    continue

                if member_path.suffix.lower() != ".py":
                    continue

                if member.file_size > MAX_ZIP_MEMBER_SIZE:
                    print(
                        Fore.YELLOW
                        + f"Skipping oversized Python file: {member.filename}"
                    )
                    continue

                if total_size + member.file_size > MAX_ZIP_TOTAL_SIZE:
                    print(
                        Fore.YELLOW
                        + "Archive indexing stopped at the uncompressed size limit."
                    )
                    break

                total_size += member.file_size

                try:
                    with archive.open(member, "r") as source_file:
                        source = source_file.read().decode("utf-8")
                except (
                    OSError,
                    RuntimeError,
                    UnicodeError,
                    zipfile.BadZipFile,
                ) as error:
                    print(
                        Fore.YELLOW
                        + f"Skipping unreadable file {member.filename}: {error}"
                    )
                    continue

                chunks = extract_chunks_from_source(
                    source,
                    member_path.as_posix(),
                )
                all_chunks.extend(chunks)

    except (OSError, zipfile.BadZipFile, NotImplementedError) as error:
        print(Fore.RED + f"Error reading ZIP archive: {error}")
        return [], np.array([])

    if not all_chunks:
        print(
            Fore.YELLOW
            + f"No Python code chunks found in {archive_path.name}."
        )
        return [], np.array([])

    chunks, embeddings = embed_chunks(all_chunks)

    if use_cache:
        save_cache(archive_path, chunks, embeddings)
        print(Fore.GREEN + "Saved ZIP index cache.")

    print(
        Fore.GREEN
        + f"Indexed {len(chunks)} code chunks from ZIP archive "
        + archive_path.name
    )

    return chunks, embeddings


def main():
    """Run interactive JCT semantic search on a folder or ZIP archive."""
    parser = argparse.ArgumentParser(
        description="Search Python code by meaning and behavioral intent."
    )

    parser.add_argument(
        "source",
        nargs="?",
        default="demo_codebase",
        help="Python project folder or ZIP archive (default: demo_codebase).",
    )

    parser.add_argument(
        "--min-score",
        type=float,
        default=0.5,
        help="Minimum search score required to display a result (default: 0.5).",
    )

    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Rebuild the index instead of using a saved cache.",
    )

    args = parser.parse_args()
    source_path = Path(args.source).expanduser()

    if source_path.suffix.lower() == ".zip":
        chunks, embeddings = index_zip(
            source_path,
            use_cache=not args.no_cache,
        )
    else:
        chunks, embeddings = index_folder(
            source_path,
            use_cache=not args.no_cache,
        )

    if not chunks:
        return

    print(
        Fore.YELLOW
        + "\nEnter queries to search semantically "
        + "(type 'quit' to exit)."
    )
    print(Fore.YELLOW + f"Minimum score: {args.min_score:.3f}")

    while True:
        try:
            query = input(
                Fore.CYAN + "\nQuery (or 'quit'): " + Style.RESET_ALL
            ).strip()
        except (EOFError, KeyboardInterrupt):
            print(Fore.YELLOW + "\nGoodbye!")
            break

        if query.lower() in {"quit", "q", "exit"}:
            print(Fore.YELLOW + "Goodbye!")
            break

        if not query:
            print(Fore.YELLOW + "Please enter a search query.")
            continue

        results = search(
            query,
            chunks,
            embeddings,
            top_k=5,
            min_score=args.min_score,
        )

        if not results:
            print(
                Fore.RED
                + "No relevant results found above threshold."
            )
            continue

        print(Fore.GREEN + f"\nTop results for '{query}':")

        for rank, result in enumerate(results, 1):
            print(
                Fore.CYAN
                + f"{rank}. Score: {result['score']:.3f} | "
                + f"{result['file']}:{result['start_line']} | "
                + f"{result['type'].capitalize()} {result['name']}"
            )

            print(Fore.YELLOW + "   Code snippet:")
            code = result["code"]
            indented_code = "   " + code.replace("\n", "\n   ")

            print(
                Fore.WHITE
                + (
                    indented_code[:500] + "..."
                    if len(code) > 500
                    else indented_code
                )
            )

            docstring = result.get("docstring", "")
            if docstring:
                print(Fore.MAGENTA + "   Docstring: " + docstring[:200])

            print("-" * 60)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = Path(f"results_{timestamp}.txt")

        with filename.open("w", encoding="utf-8") as output:
            output.write(f"Query: {query}\n")
            output.write(f"Source: {source_path.resolve()}\n")
            output.write(f"Minimum score: {args.min_score}\n\n")

            for rank, result in enumerate(results, 1):
                output.write(
                    f"{rank}. Score: {result['score']:.3f} | "
                    f"{result['file']}:{result['start_line']} | "
                    f"{result['type'].capitalize()} {result['name']}\n"
                )
                output.write("Code snippet:\n")
                output.write(result["code"][:500] + "\n")

                docstring = result.get("docstring", "")
                if docstring:
                    output.write(f"Docstring: {docstring[:200]}\n")

                output.write("-" * 60 + "\n")

        print(Fore.YELLOW + f"Results auto-saved to '{filename}'")


if __name__ == "__main__":
    main()
