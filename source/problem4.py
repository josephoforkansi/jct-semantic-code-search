#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Instructions: Complete the code below by replacing the to-do's with working code. (10 pts)

##########################################################################

class Monoid:
    def __init__(self, null, typeify, operator):
        # __init__ allows class variables to be defined 
        # when the class is initiated
        self.null = null
        self.typeify = typeify
        self.operator = operator

    def __call__(self, *args): 
        # __call__ method enables classes for which 
        # the instances behave like functions and 
        # can be called as such 
        result = self.null
        for arg in args:
            arg = self.typeify(arg)
            result = self.operator(result, arg)
        return result
    # end of __call__()
# end of Monoid class()
    

def sizeOf(in_list:list)->int:
    """ Function to determine the size of a list. """
    # TODO 3. Fix the function to determine the size of the in_list variable
    # TODO 4. Send this integer back to the code that called this function
# end of sizeOf()

def cartesian_prod(a_list:list,b_list:list) -> list:
    # print(f"my a_list and my b_list : {a_list} && {b_list}")
    # input()
    c = []
    for a in a_list:
        for b in b_list:
            c.append(a+b)
    return c
# end of cartesian_prod()



if __name__ == "__main__":
    cartesian_product_monoid  = Monoid([''],  lambda x: x, cartesian_prod) # define class

    base_list = ["1","2","3","4"]

    print("Length 2 cartesian products")
    # TODO 1. Create a variable for the output from the cartesian_prod() function. Print these values below.
    cartesian_product_monoid(base_list, base_list)
    print(f"\t [+] Length 2 Permutations_list : ")
    # TODO 2: Determine the number of permutations that were created. Print this value below.
    print(f"\t [+] Number of permutations : ")

