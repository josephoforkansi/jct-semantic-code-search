def read_file(path):
    try:
        f = open(path)
        content = f.read()
        f.close()
        return data
    except Exception:
        return None
