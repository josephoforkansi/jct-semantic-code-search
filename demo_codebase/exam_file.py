# exam_file.py – Student assignment: Implement safe file reading + positive input validation

def read_file(filename):
    # Student attempt: missing error handling
    f = open(filename)
    data = f.read()
    f.close()
    return data

def get_positive_number():
    num = input("Enter a positive number: ")
    # Student attempt: no validation loop or try-except
    return int(num)

def main():
    file_data = read_file("data.txt")
    number = get_positive_number()
    print("Number:", number)

if __name__ == "__main__":
    main()