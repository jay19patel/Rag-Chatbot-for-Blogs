from langchain_core.tools import tool
from typing import List

@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers together.

    Args:
        a: First number to add
        b: Second number to add

    Returns:
        Sum of the two numbers
    """
    return a + b

@tool
def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers together.

    Args:
        a: First number to multiply
        b: Second number to multiply

    Returns:
        Product of the two numbers
    """
    return a * b

@tool
def divide_numbers(a: float, b: float) -> float:
    """Divide first number by second number.

    Args:
        a: Number to be divided (numerator)
        b: Number to divide by (denominator)

    Returns:
        Result of division

    Raises:
        ValueError: If trying to divide by zero
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

@tool
def calculate_average(numbers: List[float]) -> float:
    """Calculate the average of a list of numbers.

    Args:
        numbers: List of numbers to average

    Returns:
        Average of all numbers

    Raises:
        ValueError: If the list is empty
    """
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)

@tool
def find_maximum(numbers: List[float]) -> float:
    """Find the maximum number in a list.

    Args:
        numbers: List of numbers to search

    Returns:
        Maximum number from the list

    Raises:
        ValueError: If the list is empty
    """
    if not numbers:
        raise ValueError("Cannot find maximum of empty list")
    return max(numbers)

@tool
def power_calculation(base: float, exponent: float) -> float:
    """Calculate base raised to the power of exponent.

    Args:
        base: Base number
        exponent: Power to raise the base to

    Returns:
        Result of base^exponent
    """
    return base ** exponent

# List of all available tools
all_tools = [
    add_numbers,
    multiply_numbers,
    divide_numbers,
    calculate_average,
    find_maximum,
    power_calculation
]

def main():
    """Demo function to test all tools"""
    print("=== Math Tools Demo ===")

    # Test add_numbers
    print(f"Add 5 + 3 = {add_numbers.invoke({'a': 5, 'b': 3})}")

    # Test multiply_numbers
    print(f"Multiply 4 * 6 = {multiply_numbers.invoke({'a': 4, 'b': 6})}")

    # Test divide_numbers
    print(f"Divide 10 / 2 = {divide_numbers.invoke({'a': 10, 'b': 2})}")

    # Test calculate_average
    numbers = [1, 2, 3, 4, 5]
    print(f"Average of {numbers} = {calculate_average.invoke({'numbers': numbers})}")

    # Test find_maximum
    print(f"Maximum of {numbers} = {find_maximum.invoke({'numbers': numbers})}")

    # Test power_calculation
    print(f"Power 2^3 = {power_calculation.invoke({'base': 2, 'exponent': 3})}")

if __name__ == "__main__":
    main()