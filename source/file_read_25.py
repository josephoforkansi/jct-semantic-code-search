def get_content(fn):
    f = open(fn)  # no try-except, no encoding
    return f.read()  # might crash
