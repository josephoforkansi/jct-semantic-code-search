def read_file(path):
    try:
        file = open(path)
        return f.read()
    finally:
        f.close()
