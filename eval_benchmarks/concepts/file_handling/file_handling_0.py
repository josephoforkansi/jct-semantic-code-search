def read_file(path):
    f = open(path)
    content = f.read()
    f.close()
    return content