# demo.py
from jct.chunking import extract_chunks
from jct.embedding import embed_texts
from jct.search import search
from pathlib import Path
import numpy as np
from colorama import Fore, Style, init
from datetime import datetime

# Initialize colorama for Windows compatibility
init(autoreset=True)

def index_folder(folder: str):
    folder_path = Path(folder)
    all_chunks = []

    for py_file in folder_path.rglob("*.py"):
        chunks = extract_chunks(py_file)
        all_chunks.extend(chunks)

    if not all_chunks:
        print(Fore.RED + "No code chunks found.")
        return [], np.array([])

    texts = [c["text"] for c in all_chunks]
    embeddings = embed_texts(texts)

    print(Fore.GREEN + f"Indexed {len(all_chunks)} chunks from {folder}")
    return all_chunks, embeddings

if __name__ == "__main__":
    # Change this to switch between demo and graded benchmarks
    codebase = "demo_codebase"  # or "eval_benchmarks/concepts/file_handling"

    chunks, embeddings = index_folder(codebase)

    print(Fore.YELLOW + "\nEnter queries to search semantically (type 'quit' to exit).")

    while True:
        q = input(Fore.CYAN + "\nQuery (or 'quit'): " + Style.RESET_ALL).strip()  # ← Fixed prompt here
        if q.lower() in ["quit", "q", "exit"]:
            print(Fore.YELLOW + "Goodbye!")
            break
        if not q:
            continue

        results = search(q, chunks, embeddings, top_k=5)

        if not results:
            print(Fore.RED + "No relevant results found above threshold.")
        else:
            print(Fore.GREEN + f"\nTop results for '{q}':")
            for i, r in enumerate(results, 1):
                # Colored score & file info
                print(Fore.CYAN + f"{i}. Score: {r['score']:.3f} | {r['file']}:{r['start_line']} | {r['type'].capitalize()} {r['name']}")
                
                # Code snippet with yellow highlight
                print(Fore.YELLOW + "   Code snippet:")
                indented_code = "   " + r['code'].replace('\n', '\n   ')
                print(Fore.WHITE + (indented_code[:500] + "..." if len(r['code']) > 500 else indented_code))
                
                # Docstring in magenta
                if r['docstring']:
                    print(Fore.MAGENTA + "   Docstring: " + r['docstring'][:200] + "...")
                
                print("-" * 60)

            # Auto-save results to timestamped file
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"results_{timestamp}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"Query: {q}\n\n")
                for i, r in enumerate(results, 1):
                    f.write(f"{i}. Score: {r['score']:.3f} | {r['file']}:{r['start_line']} | {r['type'].capitalize()} {r['name']}\n")
                    f.write("Code snippet:\n")
                    indented_code = "   " + r['code'].replace('\n', '\n   ')
                    f.write(indented_code[:500] + "..." if len(r['code']) > 500 else indented_code)
                    f.write("\n")
                    if r['docstring']:
                        f.write(f"Docstring: {r['docstring'][:200]}...\n")
                    f.write("-" * 60 + "\n")
            print(Fore.YELLOW + f"Results auto-saved to '{filename}'")