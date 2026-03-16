"""
core.py - Mandelbrot Set Computation Module (V1)

This module provides the mathematical foundation for computing the Mandelbrot set.

V1 Enhancements over V0:
- Progress callback support for logging/UI updates
- Smooth coloring algorithm for better visualization
- Input validation
- Predefined interesting locations
"""

import numpy as np
import math
import logging

# Configure module logger
logger = logging.getLogger(__name__)


def escape_time(c, max_iter):
    """
    Compute the escape time for a single complex number.
    """
    z = 0
    for iteration in range(max_iter):
        if abs(z) > 2:
            return iteration
        z = z * z + c
    return max_iter


def escape_time_smooth(c, max_iter):
    """
    Compute smooth escape time for anti-aliased coloring.
    """
    z = 0
    for i in range(max_iter):
        if abs(z) > 2:
            # Smooth coloring formula
            if abs(z) > 1:
                smooth_val = i + 1 - math.log(math.log(abs(z))) / math.log(2)
                return max(0, smooth_val)  # Ensure non-negative
            return i
        z = z * z + c
    return max_iter


def validate_parameters(width, height, max_iter, x_min, x_max, y_min, y_max):
    """
    Validate computation parameters and raise ValueError if invalid.
    """
    if width <= 0 or height <= 0:
        raise ValueError(f"Dimensions must be positive: got {width}x{height}")
    if max_iter <= 0:
        raise ValueError(f"max_iter must be positive: got {max_iter}")
    if x_min >= x_max:
        raise ValueError(f"x_min must be less than x_max: got [{x_min}, {x_max}]")
    if y_min >= y_max:
        raise ValueError(f"y_min must be less than y_max: got [{y_min}, {y_max}]")
    if width > 10000 or height > 10000:
        raise ValueError(f"Dimensions too large (max 10000): got {width}x{height}")
    if max_iter > 10000:
        raise ValueError(f"max_iter too large (max 10000): got {max_iter}")


def compute_mandelbrot(width, height, max_iter, x_min = -2.0, x_max = 1.0, y_min = -1.5, y_max = 1.5, smooth = False, progress_callback = None):
    """
    Generate a 2D array representing the Mandelbrot set.
    """
    # Validate inputs
    validate_parameters(width, height, max_iter, x_min, x_max, y_min, y_max)
    
    logger.info(f"Computing Mandelbrot set: {width}x{height}, max_iter={max_iter}")
    logger.debug(f"Bounds: x = [{x_min}, {x_max}], y = [{y_min}, {y_max}]")
    logger.debug(f"Smooth coloring: {smooth}")
    
    # Create arrays of real and imaginary values
    real_values = np.linspace(x_min, x_max, width)
    imag_values = np.linspace(y_min, y_max, height)
    
    # Initialize result array (float if smooth, int otherwise)
    dtype = np.float64 if smooth else np.int32
    result = np.zeros((height, width), dtype = dtype)
    
    # Select escape time function
    escape_func = escape_time_smooth if smooth else escape_time
    
    # Compute escape time for each point
    for row, y in enumerate(imag_values):
        for col, x in enumerate(real_values):
            c = complex(x, y)
            result[row, col] = escape_func(c, max_iter)
        
        # Report progress
        if progress_callback is not None:
            progress_callback(row + 1, height)
    
    logger.info("Computation complete")
    return result


def get_bounds(center_x = -0.5, center_y = 0.0, zoom = 1.0):
    """
    Calculate view bounds from center point and zoom level.
    """
    if zoom <= 0:
        raise ValueError(f"Zoom must be positive: got {zoom}")
    
    # Default view spans 3 units on x-axis, 3 units on y-axis
    base_width = 3.0 / zoom
    base_height = 3.0 / zoom
    
    x_min = center_x - base_width / 2
    x_max = center_x + base_width / 2
    y_min = center_y - base_height / 2
    y_max = center_y + base_height / 2
    
    logger.debug(f"Bounds for center = ({center_x}, {center_y}), zoom = {zoom}: "
                 f"x = [{x_min}, {x_max}], y = [{y_min}, {y_max}]")
    
    return (x_min, x_max, y_min, y_max)


# Predefined interesting locations for exploration
INTERESTING_LOCATIONS = {
    "default": {"center_x": -0.5, "center_y": 0.0, "zoom": 1.0},
    "seahorse": {"center_x": -0.75, "center_y": 0.1, "zoom": 20.0},
    "spiral": {"center_x": -0.761574, "center_y": -0.0847596, "zoom": 50.0},
    "elephant": {"center_x": 0.275, "center_y": 0.0, "zoom": 10.0},
    "lightning": {"center_x": -1.315, "center_y": 0.0, "zoom": 30.0},
}


def get_preset_location(name):
    """
    Get coordinates for a predefined interesting location.
    """
    if name not in INTERESTING_LOCATIONS:
        available = ", ".join(INTERESTING_LOCATIONS.keys())
        raise KeyError(f"Unknown preset '{name}'. Available: {available}")
    
    loc = INTERESTING_LOCATIONS[name]
    return (loc["center_x"], loc["center_y"], loc["zoom"])


def list_presets():
    """
    Return a list of available preset location names.
    """
    return list(INTERESTING_LOCATIONS.keys())
