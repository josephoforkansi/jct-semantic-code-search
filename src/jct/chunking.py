# src/jct/chunking.py
import ast
from pathlib import Path
from typing import List, Dict

def detect_concepts(code: str) -> List[str]:
    """Lightweight rule-based concept detection."""
    code_lower = code.lower()
    concepts = []

    if "open(" in code_lower:
        concepts.append("file_handling")

    if "try:" in code_lower or "except" in code_lower:
        concepts.append("error_handling")

    if "input(" in code_lower:
        concepts.append("user_input")

    if "while true" in code_lower:
        concepts.append("loop_validation")

    if "factorial" in code_lower or "return n * factorial" in code_lower:
        concepts.append("recursion")

    if "," in code_lower and "=" in code_lower and "return" in code_lower:
        concepts.append("swap")

    return list(set(concepts))  # remove duplicates


def extract_chunks(file_path: Path | str) -> List[Dict]:
    """Extract functions/classes and enrich with concepts."""
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

                # 🔥 NEW: detect concepts
                concepts = detect_concepts(code)

                # 🔥 NEW: enrich embedding text
                concept_text = " ".join(concepts)
                text_for_embedding = code + "\n\n" + docstring + "\n\n" + concept_text

                chunks.append({
                    "file": file_path.name,
                    "name": node.name,
                    "type": "function" if "Function" in type(node).__name__ else "class",
                    "code": code,
                    "docstring": docstring,
                    "concepts": concepts,
                    "text": text_for_embedding,
                    "start_line": node.lineno
                })

        return chunks

    except Exception as e:
        print(f"Failed to parse {file_path}: {e}")
        return []