def read_file(path):
    try:
        f = open(path)
        return f.read()
    finally:
        f.close()
