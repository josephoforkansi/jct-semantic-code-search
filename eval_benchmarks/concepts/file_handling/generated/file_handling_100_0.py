def safe_read_file(path):
    try:
        with open(path) as f:
            return f.read()
    except Exception:
        return None

# extra comment