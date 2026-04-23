# 🚀 JCT: Semantic Code Search Engine for Python

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

## 🧠 Core Idea

JCT converts both:

- Python code
- Functions
- Classes
- Natural-language search queries

into **vector embeddings** inside a shared semantic space.

This means code and user queries can be compared by meaning.

Example:

```text id="e8t6vd"
Query:
safe file reading with error handling
```
