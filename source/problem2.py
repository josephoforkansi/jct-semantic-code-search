#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Instructions: Complete the code below by replacing the to-do's with working code. (10 pts)

##########################################################################

# Explanation of code: Newton's Law of Cooling
# Mathematical Ref: https://stemjock.com/STEM%20Books/Boyce%20ODEs%2010e/Chapter%202/Section%203/BoyceODEch2s3p16.pdf

# Newton's Law of Cooling states that the rate of change of the temperature of an object is proportional to the difference between its temperature and the ambient temperature. Mathematically, it can be represented as:

# Python Variables

# * `initial_temp` is the initial temperature of the object.
# * `ambient_temp` is the ambient temperature of the surroundings.
# * `cooling_coefficient`: is the cooling coefficient indicating the rate of cooling.
# * `time` is the Time elapsed.

# Python Code Execution:

# * The program defines a function newtons_law_of_cooling that takes the initial temperature, ambient temperature, cooling coefficient, and time as inputs.
# * We calculate the temperature of the object after the given time using an equation, and return the value.
# * We note that the value is the temperature of the object at a specific time based on the given parameters.

import math

def newtons_law_of_cooling(initial_temp, ambient_temp, cooling_coefficient, time):
    """Calculate the temperature using Newton's Law of Cooling."""
    # Calculate the temperature using the formula
    temperature = ambient_temp + (initial_temp - ambient_temp) * math.exp(-cooling_coefficient * time)
    # TODO 4. Find and fix the error to complete the function.
# end of newtons_law_of_cooling()

if __name__ == "__main__":
    initial_temp = 200.0  # Initial temperature (C) of the object
    ambient_temp = 70  # Ambient temperature (C) of the surroundings
    cooling_coefficient = 0.0800  # Cooling coefficient
    time = 6.07 # Time elapsed
    # TODO 1. Calculate the final temperature using the newtons_law_of_cooling() function.
    # final_temp = ...

    # TODO 2. Print the final temperature.
    # print(...)

    # TODO 3. Print the difference between the final and initial temperatures.
    # print(...)
