# src/jct/chunking.py
import ast
from pathlib import Path
from typing import List, Dict

def extract_chunks(file_path: Path | str) -> List[Dict]:
    """Extract functions and classes from a Python file using AST."""
    file_path = Path(file_path)
    if not file_path.is_file() or file_path.suffix != ".py":
        return []

    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        chunks = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start_line = node.lineno - 1
                end_line = node.end_lineno
                lines = source.splitlines(keepends=True)
                code = "".join(lines[start_line:end_line]).strip()

                docstring = ast.get_docstring(node) or ""
                text_for_embedding = code + "\n\n" + docstring if docstring else code

                chunks.append({
                    "file": file_path.name,
                    "name": node.name,
                    "type": "function" if "Function" in type(node).__name__ else "class",
                    "code": code,
                    "docstring": docstring,
                    "text": text_for_embedding,
                    "start_line": node.lineno
                })

        return chunks
    except Exception as e:
        print(f"Failed to parse {file_path}: {e}")
        return []