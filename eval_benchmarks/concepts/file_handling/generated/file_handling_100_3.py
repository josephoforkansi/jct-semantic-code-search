def safe_read_file(filename):
    try:
        with open(filename) as f:
            return f.read()
    except Exception:
        return None
