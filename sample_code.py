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

# Add a really complex function to test AI capabilities
def sample_function(data):
    # This function performs a series of complex transformations on the input data
    transformed = []
    for item in data:
        if isinstance(item, dict):
            # Perform some complex logic
            new_item = {k: v * 2 for k, v in item.items() if isinstance(v, int)}
            transformed.append(new_item)
    return transformed

# TODO: Add error handling
# TODO: Add input validation
# TODO: Optimize performance
