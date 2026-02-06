def read_file(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        print("File not found!")
        return ""
