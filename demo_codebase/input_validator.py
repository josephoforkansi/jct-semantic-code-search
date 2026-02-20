def get_positive_number():
    """Get a positive integer from user input with validation."""
    while True:
        try:
            num = int(input("Enter a positive number: "))
            if num > 0:
                return num
            print("Number must be positive.")
        except ValueError:
            print("That's not a valid integer!")