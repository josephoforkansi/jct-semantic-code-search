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

---

## ⚡ Quick Start

Run JCT in under 1 minute:

```bash
git clone https://github.com/josephoforkansi/jct-semantic-code-search.git
cd jct-semantic-code-search
uv sync
uv run python src/jct/search.py
```

JCT uses uv for fast dependency management.

---

## 💻 Alternative Setup (pip)

```bash
python -m venv venv
source venv/bin/activate
pip install -e .
python src/jct/search.py
```

---

## ▶️ Usage

Run the interactive search:

```bash
uv run python src/jct/demo.py
```

Example interaction:

```text
Query:
safe file reading with error handling

Top Results:
file_handler.py      score: 0.92
```

---

## 🧪 Demonstration

JCT supports concept-based retrieval:

```text
Query:
validate user input until correct

Result:
input_validator.py   score: 0.88
```

This demonstrates that the system retrieves code based on behavior, not keywords.

---

## 📊 Experimental Support

JCT includes evaluation scripts and benchmark datasets:

```bash
uv run python src/jct/evaluate.py
```

Metrics include:

- Precision@K
- NDCG
- Success@1

These experiments support the findings described in the research report.

---

## 🛡 Error Handling

JCT includes validation for:

- empty queries
- invalid file paths
- AST parsing failures

Example:

```text
Error: Query cannot be empty
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

## ✅ Reproducibility

JCT has been tested on `macOS`, `linux` and `Windows` environments and can be installed and executed by users without prior setup.

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

📜 License

MIT License
