# jct_demo.py - Minimal prototype for JCT: Semantic Behavioral Code Search
# Run with: python jct_demo.py

import ast
import os
import numpy as np
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict

# Load a lightweight, fast embedding model (good for code + text)
# You can swap to 'microsoft/codebert-base' or 'jinaai/jina-embeddings-v2-base-code' later for better code understanding
model = SentenceTransformer('all-MiniLM-L6-v2')  # ~80MB, runs on CPU quickly

def extract_code_chunks(file_path: str) -> List[Dict]:
    """Parse Python file and extract functions/classes with docstrings as searchable chunks."""
    chunks = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                # Get code snippet (source lines)
                start = node.lineno - 1
                end = node.end_lineno
                # In real version, read exact lines from file
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                code_snippet = ''.join(lines[start:end]).strip()
                
                # Docstring if present
                docstring = ast.get_docstring(node) or ""
                
                # Combine for embedding: code + docstring gives better semantics
                text_for_embedding = f"{code_snippet}\n\n{docstring}".strip()
                
                chunks.append({
                    'file': os.path.basename(file_path),
                    'name': node.name,
                    'type': 'function' if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else 'class',
                    'code': code_snippet,
                    'docstring': docstring,
                    'text': text_for_embedding,
                    'start_line': node.lineno
                })
    except Exception as e:
        print(f"Skipping {file_path}: {e}")
    return chunks

def index_codebase(directory: str) -> tuple[List[Dict], np.ndarray]:
    """Index all .py files in a directory."""
    all_chunks = []
    texts = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                chunks = extract_code_chunks(path)
                all_chunks.extend(chunks)
                texts.extend([c['text'] for c in chunks])
    
    if not texts:
        raise ValueError("No code chunks found in directory.")
    
    # Generate embeddings once
    print("Generating embeddings...")
    embeddings = model.encode(texts, convert_to_tensor=True, show_progress_bar=True)
    embeddings = embeddings.cpu().numpy()  # for easier numpy ops
    
    return all_chunks, embeddings

def search(query: str, chunks: List[Dict], embeddings: np.ndarray, top_k: int = 5):
    """Search for behavioral concepts using semantic similarity."""
    query_emb = model.encode(query, convert_to_tensor=True).cpu().numpy()
    
    # Cosine similarity
    cos_scores = util.cos_sim(query_emb, embeddings)[0]
    top_results = np.argsort(cos_scores)[-top_k:][::-1]  # descending order
    
    print(f"\nTop {top_k} matches for query: '{query}'\n")
    for idx in top_results:
        score = cos_scores[idx].item()
        chunk = chunks[idx]
        print(f"Score: {score:.3f}")
        print(f"File: {chunk['file']} | {chunk['type'].capitalize()}: {chunk['name']}")
        print(f"Line {chunk['start_line']}")
        print(f"Code snippet:\n{chunk['code'][:300]}{'...' if len(chunk['code']) > 300 else ''}")
        if chunk['docstring']:
            print(f"Docstring: {chunk['docstring'][:150]}{'...' if len(chunk['docstring']) > 150 else ''}")
        print("-" * 60)

# --------------------- Demo Usage ---------------------
if __name__ == "__main__":
    # Point this to a small directory with your Python files (e.g., a student project or examples)
    # For testing: create a folder 'demo_codebase/' with a few .py files containing functions like:
    #   - file reading with try/except FileNotFoundError
    #   - sorting lists
    #   - recursion examples
    codebase_dir = "demo_codebase"  # CHANGE THIS to your test folder path
    
    print("Indexing codebase...")
    chunks, embeddings = index_codebase(codebase_dir)
    print(f"Indexed {len(chunks)} code chunks.")
    
    # Example queries a freshman might use
    queries = [
        "code that handles file not found errors",
        "implements bubble sort or any sorting algorithm",
        "uses recursion to traverse or calculate something",
        "validates user input with try-except",
        "opens and reads a file safely"
    ]
    
    for q in queries:
        search(q, chunks, embeddings, top_k=3)
