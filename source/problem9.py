#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
from typing import Tuple, Union

# Instructions: Complete the code below by replacing the to-do's with working code. (20 pts)

##########################################################################


from typing import Tuple
from typing import Union


def calculate_quadratic_equation_roots(
    a: float, b: float, c: float
) -> Tuple[Union[float, complex], Union[float, complex]]:
    """Calculate the roots of a quadratic equation."""
    D = (b * b - 4 * a * c) ** 0.5
    # TODO 4. x_one = quantity (`b` plus `D`) divided by quantity (2 times `a`)
    # TODO 5. x_two =  quantity (`b` minus `D`) divided by quantity (2 times `a`)
    # TODO 6. Fix another error near this line
# end of calculate_quadratic_equation_roots()


# Define parameters
a = 1
b = -2
c = 2

print("Calculating the roots of a quadratic equation with:")
# TODO 1. Print out the values a, b and c

# TODO 2: perform the calculation of the two roots for the quadratic equation

# TODO 3. print the output values from running the calculation of the quadratic
# equation's roots with the calculate_quadratic_equation_roots() function
print()
print(":star: Finished computing the roots of the equation as:")
print(f"   x_one = {x_one}")
print(f"   x_two = {x_two}")