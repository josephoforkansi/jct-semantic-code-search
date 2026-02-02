#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Instructions: Complete the code below to allow it to execute. (10 pts)

##########################################################################

def cube_root_approximation(number, tolerance=1e-6):
    # Initial guess for the cube root
    # TODO 4. Find and fix the error to complete the function.
    myGuess = 5
    # Iterate until the approximation is within the specified tolerance
    while abs(guess**3 - number) > tolerance:
        # Update the guess using the approximation formula
        guess = (2 * guess + number / (guess**2)) / 3.0
        print(f" guess = {guess}")
    return guess
# end of cube_root_approximation

# Example: Calculate the cube root of 29791
input_number = 29791
# TODO 3. Fix an bug near this line.
cube_root_approximation(input_number)

# Display the result
    # TODO 1. print the input_number
    # TODO 2. print the resulting approximation
