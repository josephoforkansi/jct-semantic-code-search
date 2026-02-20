# demo.py
from src.jct.chunking import extract_chunks
from src.jct.embedding import embed_texts
from src.jct.search import search
from pathlib import Path

def index_folder(folder: str):
    folder_path = Path(folder)
    all_chunks = []

    for py_file in folder_path.rglob("*.py"):
        chunks = extract_chunks(py_file)
        all_chunks.extend(chunks)

    if not all_chunks:
        print("No code chunks found.")
        return [], np.array([])

    texts = [c["text"] for c in all_chunks]
    embeddings = embed_texts(texts)

    print(f"Indexed {len(all_chunks)} chunks from {folder}")
    return all_chunks, embeddings

if __name__ == "__main__":
    # Change this to your test folder
    codebase = "demo_codebase"  # or "eval_benchmarks/concepts/file_handling"

    chunks, embeddings = index_folder(codebase)

    while True:
        q = input("\nQuery (or 'quit'): ").strip()
        if q.lower() in ["quit", "q", "exit"]:
            break
        if q:
            results = search(q, chunks, embeddings, top_k=5)
            if not results:
                print("No matches above threshold.")
            else:
                for r in results:
                    print(f"\n[{r['score']:.3f}] {r['file']}:{r['start_line']} {r['type']} {r['name']}")
                    print(r["code"][:180] + "..." if len(r["code"]) > 180 else r["code"])
                    if r["docstring"]:
                        print(f"Doc: {r['docstring'][:120]}...")