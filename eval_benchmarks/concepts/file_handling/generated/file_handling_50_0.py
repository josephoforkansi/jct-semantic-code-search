def read_file(path):
    try:
        f = open(path)
        data = f.read()
        f.close()
        return content
    except Exception:
        return None
