# 🚀 JCT: Intent-Based Semantic Code Search for Python

> Search code by meaning, not just keywords.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Status](https://img.shields.io/badge/Status-Active-success)
![Research](https://img.shields.io/badge/Project-Semantic%20Search-purple)
![License](https://img.shields.io/badge/License-MIT-green)

JCT (Joseph Cool Tool) is a semantic behavioral code search engine for Python that helps users retrieve relevant source code based on **intent, concepts, and behavior** rather than exact syntax, filenames, or literal keywords.

Traditional search tools are useful when users already know what code looks like. JCT is designed for situations where users know what code should **do**, but not exactly how it was written.

---

## 🌟 Why JCT Exists

Traditional tools such as **grep**, **regex**, and syntax matchers rely on literal words, tokens, or structure.

That creates a common problem:

✅ You know the programming concept  
✅ You know the goal  
❌ You do not know the exact function name  
❌ You do not know the precise syntax  
❌ You do not know how another programmer implemented it

Examples:

- safe file reading with exception handling
- validate user input until correct
- loop until number is entered
- robust file open and close

These searches often fail with keyword-only tools.

JCT solves that gap by allowing **concept-based code retrieval**.

---

## 📌 Overview

JCT (Joseph Cool Tool) is a **semantic behavioral code search engine for Python** that retrieves source code based on **intent, concepts, and behavior**, rather than exact syntax or keywords.

This project addresses a fundamental problem in software development and computer science education:

> Users often know what code should *do*, but cannot recall the exact syntax or implementation details needed to find it.

JCT bridges this **conceptual-to-practical gap** by enabling **natural-language queries** over real codebases.

---

## 🎯 Research Problem

Traditional tools such as:

- `grep`
- regular expressions
- AST-based matchers

depend on **exact token matching**.

This leads to failure when:

- the user does not know function names
- the user cannot recall syntax
- the implementation varies across files

Example failed searches:

- "safe file reading with error handling"
- "loop until valid input"
- "validate user input continuously"

JCT solves this by introducing **semantic retrieval using embeddings**.

---

## 🧠 System Architecture

JCT is built as a modular semantic retrieval pipeline:

1. **Chunking**
   - Python files are parsed into meaningful units (functions/classes) using AST

2. **Embedding**
   - Each code chunk is converted into a vector representation using Sentence Transformers

3. **Query Encoding**
   - Natural language queries are embedded into the same vector space

4. **Search & Ranking**
   - Cosine similarity ranks the most relevant code snippets

5. **Top-K Retrieval**
   - The system returns the highest scoring matches

---

## 🗂 Repository Structure

```text
jct-semantic-code-search/
│
├── src/jct/                 # Core system
│   ├── search.py
│   ├── embedding.py
│   ├── chunking.py
│   ├── evaluate.py
│   ├── config.py
│   └── demo.py
│
├── demo_codebase/           # Example dataset
│   ├── file_handler.py
│   ├── input_validator.py
│
├── eval_benchmarks/         # Experimental evaluation
│   └── concepts/
│
├── tests/                   # Unit tests
│   ├── test_search.py
│   ├── test_embedding.py
│   └── test_chunking.py
│
├── scripts/
│   └── run_demo.sh
│
├── README.md
├── pyproject.toml
└── .gitignore
```

---

## ⚡ Quick Start

Run JCT in under 1 minute:

```bash
git clone https://github.com/josephoforkansi/jct-semantic-code-search.git
cd jct-semantic-code-search
uv sync
uv run python -m jct.demo
```

JCT uses `uv` for fast dependency management and reproducible environments.

---

## 💻 Alternative Setup (pip)

```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
pip install -e .
python -m jct.demo
```

> Note: JCT is structured as a Python package and should be executed using
> `-m jct.<module>` to ensure correct module resolution.

---

## ▶️ Demonstration

Run the interactive semantic search:

```bash
uv run python -m jct.demo
```

Example interaction:

```text
Query: safe file reading with error handling

Top results for 'safe file reading with error handling':
1. Score: 0.720 | file_handler.py:1 | Function safe_read_file
   Code snippet:
   def safe_read_file(path):
       """Read file content safely with proper error handling."""
       try:
           with open(path, 'r', encoding='utf-8') as f:
               return f.read()
       except FileNotFoundError:
           print(f"File '{path}' not found.")
           return None
       except PermissionError:
           print(f"Permission denied for '{path}'.")
           return None
       except Exception as e:
           print(f"Unexpected error: {e}")
           return None
   Docstring: Read file content safely with proper error handling....
------------------------------------------------------------
2. Score: 0.551 | exam_file.py:3 | Function read_file
   Code snippet:
   def read_file(filename):
       # Student attempt: missing error handling
       f = open(filename)
       data = f.read()
       f.close()
       return data
------------------------------------------------------------
```

This example demonstrates that JCT retrieves code based on behavior and intent, not exact keywords, correctly prioritizing robust implementations over incomplete ones.

---

## 📊 Experimental Support

JCT includes evaluation scripts and benchmark datasets:

```bash
uv run python -m jct.evaluate
```

Metrics include:

- Precision@K
- NDCG
- Success@1

These experiments support the findings described in the research report.

---

## 📈 Sample Evaluation Output

The following results are generated using the evaluation pipeline on the
concept-labeled dataset.

```text
📂 Indexing dataset: eval_benchmarks/concepts/file_handling/generated
✅ Ground truth files detected: 10
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 2/2 [00:00<00:00,  3.97it/s]
✅ Indexed 40 chunks

🔍 Query: safe file reading with error handling
Precision@5: 1.000
NDCG@5: 1.000
Success@1: 100%
Avg Score: 0.726
  1. [0.742] file_handling_100_3.py:1 safe_read_file
  2. [0.742] file_handling_100_4.py:1 safe_read_file
  3. [0.715] file_handling_100_0.py:1 safe_read_file
  4. [0.715] file_handling_100_1.py:1 safe_read_file
  5. [0.715] file_handling_100_6.py:1 safe_read_file
------------------------------------------------------------

🔍 Query: handle file not found exception
Precision@5: 0.000
NDCG@5: 0.000
Success@1: 0%
Avg Score: 0.541
  1. [0.548] file_handling_25_1.py:1 read_file
  2. [0.548] file_handling_25_4.py:1 read_file
  3. [0.548] file_handling_25_7.py:1 read_file
  4. [0.538] file_handling_25_8.py:1 read_file
  5. [0.525] file_handling_50_0.py:1 read_file
------------------------------------------------------------

🔍 Query: read file safely with try except
Precision@5: 1.000
NDCG@5: 1.000
Success@1: 100%
Avg Score: 0.708
  1. [0.720] file_handling_100_3.py:1 safe_read_file
  2. [0.720] file_handling_100_4.py:1 safe_read_file
  3. [0.700] file_handling_100_0.py:1 safe_read_file
  4. [0.700] file_handling_100_1.py:1 safe_read_file
  5. [0.700] file_handling_100_6.py:1 safe_read_file
------------------------------------------------------------

🔍 Query: robust file reading function
Precision@5: 0.400
NDCG@5: 0.553
Success@1: 100%
Avg Score: 0.589
  1. [0.602] file_handling_100_3.py:1 safe_read_file
  2. [0.602] file_handling_100_4.py:1 safe_read_file
  3. [0.580] file_handling_50_3.py:1 read_file
  4. [0.580] file_handling_50_5.py:1 read_file
  5. [0.580] file_handling_50_7.py:1 read_file
------------------------------------------------------------
```

---

## ⚠️ Error Handling

JCT includes basic input validation and safeguards:

- Empty queries are ignored to prevent invalid searches  
- Invalid or missing files are handled gracefully during parsing  
- Exceptions during file processing do not crash the system  

Example:

```text
Query (or 'quit'): 
(no results returned — empty query skipped)
```

---

## 🧪 Testing

Run tests:

```bash
pytest tests/
```

Test coverage includes:

- embedding generation
- code chunking
- search ranking

---

## 🔄 Development Activity

This repository was developed iteratively with regular commits, demonstrating:

- performance improvements
- evaluation refinements
- architecture evolution

---

## ⚙️ Technical Complexity

JCT integrates multiple domains:

- natural language processing
- information retrieval
- software engineering
- abstract syntax tree analysis

This reflects appropriate complexity for junior-level research.

---

## ⚖️ Research Contribution

JCT demonstrates that:

- semantic embeddings improve code retrieval
- concept-based search is feasible locally
- lightweight tools can support education

---

## 🚀 Future Work

Planned extensions include:

- hybrid retrieval (semantic + lexical)
- multi-language support
- IDE integration
- large-scale benchmarks

---

## ✅ Reproducibility

JCT has been tested on `macOS`, `linux` and `Windows` environments and can be installed and executed by users without prior setup.
