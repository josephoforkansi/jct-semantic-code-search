def safe_read_file(path: str) -> str | None:
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
    except UnicodeDecodeError:
        print(f"Encoding error in '{path}'.")
        return None
    except Exception as e:
        print(f"Unexpected error reading '{path}': {e}")
        return None