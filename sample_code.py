"""
Sample code for testing PR review.
This file contains intentional issues for the AI to find.
"""

def calculate_average(numbers):
    # BUG: No check for empty list
    return sum(numbers) / len(numbers)

def process_user_input(user_input):
    # SECURITY: No input validation
    exec(user_input)  # Dangerous!
    
def slow_function(data):
    # PERFORMANCE: Inefficient nested loops
    result = []
    for i in data:
        for j in data:
            if i == j:
                result.append(i)
    return result

# Add a badly implemented function to demonstrate the AI review
def badly_implemented_function(data):
    # BUG: No return statement
    for item in data:
        print(item)

# TODO: Add error handling
# TODO: Add input validation
# TODO: Optimize performance
