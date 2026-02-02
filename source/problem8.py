#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Instructions: Complete the code below by replacing the to-do's with working code. (10 pts)

##########################################################################

import math

def isInt(x):
    if getAbsoluteValue(math.cos(x*math.pi)) == 1:
        # TODO 1. Print the status including the integer's value
    else:
        # TODO 2. Print the alternative status including the integer's value
# end of isInt()

def getAbsoluteValue(value):
    """ A function to determine whether value is negative. If so, return a positive value. Otherwise return the unchanged value. """
    # TODO 3. Use an `if` and `else` block to determine whether a value is positive or negative.
    # Note: the use of Python's `abs()` function is not allowed. 
    # TODO 4. Send back a positive value. 
# end of getAbsoluteValue()

myVal = -3.414
print(f" Value: {myVal}; absolute value: {getAbsoluteValue(myVal)}")
isInt(myVal)

myVal = 3
print(f" Value: {myVal}; absolute value: {getAbsoluteValue(myVal)}")
isInt(myVal)
