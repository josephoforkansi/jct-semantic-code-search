#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Instructions: Complete the code below by replacing the to-do's with working code. (10 pts)

##########################################################################

# Explanation of code

# 1. The Monte Carlo Method:
# The Monte Carlo method is a statistical technique that uses random sampling to obtain numerical results. In this case, it is used to approximate the value of Pi (about 3.14).

# 2. Geometry Background:
# Consider a unit circle centered at the origin of a Cartesian coordinate system. The area of this unit circle is Pi.

# 3. Approximation Process:
# * The code generates random points within a square with side length 1, which circumscribes the unit circle.
# * For each point generated, the approximation algorithm checks whether the point value falls within the unit circle area or not.
# If the distance of the point from the origin (0, 0) is less than or equal to 1, then the point lies INSIDE the unit circle.

# Calculation of Pi Approximation:
# From our code, we have the following variables:

# * `inside_circle` is the number of points falling inside the unit circle.
# * `total` is the total number of random points generated.
# * Pi is calculated by the ratio of the area of the unit circle 
#   to the area of the square using the following equation,
#
#      Pi/4 = AreaOfcircle / AreaOfsquare
#           = [Pi*(r**2)] / [(2*r)**2] 
# * After iterating through a large number of points (num_samples), the code calculates the ratio of points inside the circle to the total number of points. Multiplying this ratio by 4 gives an approximation of π.


# In this Python code, we can estimate a value for Pi by dividing the `inside_circle` by `total` and then multiplying 4 to this value. 


def approximate_pi(n):
    """Approximate the value of pi using the Monte Carlo method."""
    import random

    inside_circle = 0
    total = 0

    for _ in range(n):
        x = random.random()
        y = random.random()

        distance = x**2 + y**2

        if distance <= 1:
            inside_circle += 1

        total += 1

    # TODO: 1. Calculate the approximation of pi using `inside_circle` and `total` variables. 
    # The equation is: (inside_circle divided by total) times 4
    # pi_approx = ...

    # TODO: 2. Return the calculated value of pi_approx.
    # return ...

# end of approximate_pi()

if __name__ == "__main__":
    num_samples = 1000000
    pi_value = approximate_pi(num_samples)
    print("Approximated value of pi:", pi_value)
