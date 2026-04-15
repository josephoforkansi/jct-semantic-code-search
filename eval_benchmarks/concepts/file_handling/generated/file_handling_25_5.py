def read_file(filename):
    try:
        f = open(filename)
        return f.read()
    finally:
        f.close()
