#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Instructions: Complete the code below by replacing the to-do's with working code. (10 pts)

##########################################################################

def getUniqueWords(in_list:list) -> set:
    """ Function to create variable and data structure to gather only the unique words"""
    # TODO 4. Return only unique words
    
# end of getUniqueWords()

def sizeOf(in_dict:dict)->int:
    """ Function to determine the size of a list. """
    return len(in_dict)
# end of sizeOf()


# Create a random string from which we will work.
text = "This is a sample text. It contains some words, and some words may repeat and continue to repeat."

# Remove the punctuation
text == text.replace(".","") 

# TODO 3. Fix errors near this line

# Prepare all lowercase of string chars
# and split the text into words to create a list
words == text.lower().split()

# Get only the unique words from the list
# TODO 1. Create a variable to contain the unique words prepared from the getUniqueWords() function
# unique_words = ...

# Count word frequencies
word_frequencies = {word: words.count(word) for word in unique_words}

# Display results
# TODO 2. Fix the below print statements. 
print("Original Text: {text}")
print(" {Size} of dictionary: {sizeOf(word_frequencies)}")
print(" ----- ")
for word in word_frequencies: # Display all words with frequencies
    print(" {i} : {word_frequencies[i]}")
