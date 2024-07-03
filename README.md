# Elastic
A **Python-based / Pythonic** Programming Language (interpreter based).

# Description
This project was based on/inspired by:

- CodePulse's Make Your Own Programming Language Tutorial(s)
- Ruslan's Blog: Let's Make A Simple Interpreter

This project was made for fun out of interest. The Parser and Interpreter bases were created by CodePulse,
but I modified different parts to my liking and changed some functionality. I also added a variety of functions and data structures.

# Built-In Functions:
- print(param): Simple print statement
- input(param): Take in user input (String exclusive)
- input_int(param): Takes in user input (Integer exclusive)
- clear() / cls(): Clears the terminal
- is_number(param): Checks if the argument is a number data type.
- is_string(param): Checks if the argument is a string data type.
- is_list(param): Checks if the argument is a list data type.
- is_function(param): Checks if an argument is a function data type.
- append(list, item): Adds an item to a list.
- remove(list, index): Removes an item from a list.
- extend(list, list): Extends a list with new list inputs.
- length(list): Returns the length of a list.
- run(file): Runs a file. Used in the terminal. File must have a .el extension.
- abs(number): Returns the absolute value of a number.
- sqrt(number): Returns the square root of a number.
- sin(number): Returns the sine value of a number.
- cos(number): Returns the cosine value of a number.
- tan(number): Returns the tangent value of a number.
- substring(param, start_index, end_index): Returns the substring of a string.
- contains(list, item): Checks if a specified item is in a list.
- index_of(list, item): Returns index of an item in a specified list, otherwise returns -1.
- to_upper(string): Returns a string in all uppercase.
- to_lower(string): Returns a string in all lowercase.

**Constants:** Pi (pi), Euler's Number (euler), Tau (tau)


# List Operations:
- Addition: [1,2,3] + 4 = [1,2,3,4]
- Conjunction: [1,2,3] * [4,5,6] = [1,2,3,4,5,6]
- Removal: [1,2,3] - 1 (index, not value) = [1,3]
- Retrieval: [1,2,3] / 0 (index, not value) = 1

# Special Notes
- Files must have a .el extension
- Run the shell file first before using the run command in your terminal.
- A blank document with only comments WILL throw an error.

