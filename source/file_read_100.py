def read_file_safe(path: str) -> str | None:
    """Read file content safely with proper error handling."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{path}' not found.")
        return None
    except PermissionError:
        print(f"Error: Permission denied for '{path}'.")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
