def swap_values(a, b):
    """Swap two values without a temporary variable."""
    a, b = b, a
    return a, b

def factorial(n):
    """Calculate factorial using recursion."""
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)