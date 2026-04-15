def read_file(path):
    try:
        f = open(path, 'r')
        return f.read()
    finally:
        f.close()  # still crashes if open fails