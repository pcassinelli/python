"""
core.py - Mandelbrot Set Computation Module

This module provides the mathematical foundation for computing the Mandelbrot set.
"""

import numpy as np


def escape_time(c, max_iter):
    """
    Compute the escape time for a single complex number.
    """
    z = 0
    for i in range(max_iter):
        if abs(z) > 2:
            return i
        z = z * z + c
    return max_iter


def compute_mandelbrot(width, height, max_iter, x_min = -2.0, x_max = 1.0, y_min = -1.5, y_max = 1.5):
    """
    Generate a 2D array representing the Mandelbrot set.
    """
    # Create arrays of real and imaginary values
    real_values = np.linspace(x_min, x_max, width)
    imag_values = np.linspace(y_min, y_max, height)
    
    # Initialize result array
    result = np.zeros((height, width), dtype = np.int32)
    
    # Compute escape time for each point
    for row, y in enumerate(imag_values):
        for col, x in enumerate(real_values):
            c = complex(x, y)
            result[row, col] = escape_time(c, max_iter)
    
    return result
