def read_file(path):
    try:
        f = open(path, 'r')
        content = f.read()
        f.close()
        return content
    except FileNotFoundError:
        print("File not found!")
        return ""