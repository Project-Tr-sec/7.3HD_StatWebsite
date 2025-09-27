"""
Math core module containing mathematical operations.
"""
import math

def log(x: float) -> float:
    """
    Calculate natural logarithm of a number.
    
    Args:
        x: Input number
        
    Returns:
        Natural logarithm of x
    """
    return math.log(x)

def sqrt(x: float) -> float:
    """
    Calculate square root of a number.
    
    Args:
        x: Input number
        
    Returns:
        Square root of x
    """
    return math.sqrt(x)

# Add more mathematical functions as needed
def add(a: float, b: float) -> float:
    return a + b

def subtract(a: float, b: float) -> float:
    return a - b

def multiply(a: float, b: float) -> float:
    return a * b

def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b