# src/jct/generate_dataset.py
from pathlib import Path
import random

# 🔥 IMPORTANT: using generated/ folder (clean separation)
OUTPUT_DIR = Path("eval_benchmarks/concepts/file_handling/generated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =========================
# 🔧 CODE TEMPLATES
# =========================

BAD_TEMPLATES = [
    """def read_file(path):
    f = open(path)
    data = f.read()
    f.close()
    return data
""",
    """def read_file(path):
    return open(path).read()
"""
]

PARTIAL_25_TEMPLATES = [
    """def read_file(path):
    try:
        f = open(path)
        return f.read()
    finally:
        f.close()
""",
    """def read_file(path):
    try:
        return open(path).read()
    except:
        print("error")
"""
]

PARTIAL_50_TEMPLATES = [
    """def read_file(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ""
""",
    """def read_file(path):
    try:
        f = open(path)
        data = f.read()
        f.close()
        return data
    except Exception:
        return None
"""
]

GOOD_100_TEMPLATES = [
    """def safe_read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None
    except PermissionError:
        return None
""",
    """def safe_read_file(path):
    try:
        with open(path) as f:
            return f.read()
    except Exception:
        return None
"""
]


# =========================
# 🎲 SAFE VARIATION ENGINE
# =========================

def add_noise(code: str) -> str:
    """
    Safe variations that DO NOT break Python syntax.
    Only modifies variable names in controlled ways.
    """

    variations = [
        lambda c: c.replace("f = open", "file = open"),
        lambda c: c.replace("data =", "content ="),
        lambda c: c.replace("return data", "return content"),
        lambda c: c.replace("path", "filename"),
        lambda c: c + "\n# extra comment"
    ]

    for _ in range(random.randint(1, 2)):
        code = random.choice(variations)(code)

    return code


# =========================
# 🏗️ GENERATION FUNCTION
# =========================

def generate_files(label: int, templates: list, count: int):
    for i in range(count):
        base_code = random.choice(templates)
        varied_code = add_noise(base_code)

        filename = f"file_handling_{label}_{i}.py"
        path = OUTPUT_DIR / filename

        path.write_text(varied_code)


# =========================
# 🚀 MAIN GENERATOR
# =========================

def generate_dataset():
    print("Generating dataset...")

    generate_files(0, BAD_TEMPLATES, 10)
    generate_files(25, PARTIAL_25_TEMPLATES, 10)
    generate_files(50, PARTIAL_50_TEMPLATES, 10)
    generate_files(100, GOOD_100_TEMPLATES, 10)

    print(f"✅ Dataset created at: {OUTPUT_DIR}")


if __name__ == "__main__":
    generate_dataset()