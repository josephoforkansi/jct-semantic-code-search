#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Instructions: Complete the code below by replacing the to-do's with working code. (10 pts)

##########################################################################


def cube_root_approximation(number, tolerance=1e-6):
    """ A function to calculate the cube root"""
    # Initial guess for the cube root
    # guess = number / 2.0 # one way to start
    guess = 5
    # Iterate until the approximation is within the specified tolerance
    while abs(guess**3 - number) > tolerance:
        # Update the guess using the approximation formula
        guess = (2 * guess + number / (guess**2)) / 3.0
        print(f" guess = {guess}")
    # TODO 3. Find and fix the error to complete the function.

# end of cube_root_approximation()

# Example: Calculate the cube root of 29791
input_number = 29791

# TODO 1. Calculate the approximation by using the cube_root_approximation() function.
    # result = ...
# TODO 2. Print the approximated value.
    # print(...)
