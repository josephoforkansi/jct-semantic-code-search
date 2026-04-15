def read_file(path):
    try:
        return open(path).read()
    except:
        print("error")
