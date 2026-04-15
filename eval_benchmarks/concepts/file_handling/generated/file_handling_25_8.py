def read_file(filename):
    try:
        return open(filename).read()
    except:
        print("error")
