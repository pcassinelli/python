"""
core.py - Mandelbrot Set Computation Module (V2)

This module provides the mathematical foundation for computing the Mandelbrot set.

V2 Enhancements over V1:
- NumPy vectorized computation for speedup
- Performance comparison between methods
- Additional coloring algorithms

The Mandelbrot set is defined as the set of complex numbers c for which the
iteration z(n+1) = z(n)^2 + c does not diverge when starting with z(0) = 0.
"""

import numpy as np
import math
import logging
import time
from typing import Callable, Optional, Tuple, Dict
from dataclasses import dataclass
from enum import Enum

# Configure module logger
logger = logging.getLogger(__name__)


class ComputeMethod(Enum):
    """Available computation methods."""
    PYTHON = "python"      # Pure Python (slow but clear)
    NUMPY = "numpy"        # NumPy vectorized (fast)


@dataclass
class ComputeResult:
    """Result of a Mandelbrot computation with metadata."""
    data: np.ndarray
    elapsed_time: float
    method: ComputeMethod
    width: int
    height: int
    max_iter: int
    
    @property
    def points_per_second(self) -> float:
        """Calculate computation speed."""
        total_points = self.width * self.height
        return total_points / self.elapsed_time if self.elapsed_time > 0 else 0


def escape_time(c: complex, max_iter: int) -> int:
    """
    Compute the escape time for a single complex number.
    
    The escape time is the number of iterations before |z| > 2,
    which guarantees divergence. If the point never escapes within
    max_iter iterations, it is considered part of the Mandelbrot set.
    
    Args:
        c: The complex number to test.
        max_iter: Maximum number of iterations before assuming convergence.
    
    Returns:
        The iteration count at which |z| exceeded 2, or max_iter if it never did.
    """
    z = 0
    for iteration in range(max_iter):
        if abs(z) > 2:
            return iteration
        z = z * z + c
    return max_iter


def escape_time_smooth(c: complex, max_iter: int) -> float:
    """
    Compute smooth escape time for anti-aliased coloring.
    
    Uses the normalized iteration count algorithm to produce
    continuous (non-banded) coloring.
    
    Args:
        c: The complex number to test.
        max_iter: Maximum number of iterations.
    
    Returns:
        A float representing the smooth iteration count.
    """
    z = 0
    for iteration in range(max_iter):
        if abs(z) > 2:
            if abs(z) > 1:
                smooth_val = iteration + 1 - math.log(math.log(abs(z))) / math.log(2)
                return max(0, smooth_val)
            return iteration
        z = z * z + c
    return max_iter


def validate_parameters(
    width: int,
    height: int,
    max_iter: int,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float
) -> None:
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


def compute_mandelbrot_python(
    width: int,
    height: int,
    max_iter: int,
    x_min: float = -2.0,
    x_max: float = 1.0,
    y_min: float = -1.5,
    y_max: float = 1.5,
    smooth: bool = False,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> np.ndarray:
    """
    Generate Mandelbrot set using pure Python (reference implementation).
    
    This is the original V0/V1 algorithm - clear but slow.
    Use compute_mandelbrot_numpy() for better performance.
    """
    real_values = np.linspace(x_min, x_max, width)
    imag_values = np.linspace(y_min, y_max, height)
    
    dtype = np.float64 if smooth else np.int32
    result = np.zeros((height, width), dtype=dtype)
    
    escape_func = escape_time_smooth if smooth else escape_time
    
    for row, y in enumerate(imag_values):
        for col, x in enumerate(real_values):
            c = complex(x, y)
            result[row, col] = escape_func(c, max_iter)
        
        if progress_callback is not None:
            progress_callback(row + 1, height)
    
    return result


def compute_mandelbrot_numpy(
    width: int,
    height: int,
    max_iter: int,
    x_min: float = -2.0,
    x_max: float = 1.0,
    y_min: float = -1.5,
    y_max: float = 1.5,
    smooth: bool = False,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> np.ndarray:
    """
    Generate Mandelbrot set using NumPy vectorization (optimized).
    
    This is faster than the pure Python version,
    typically 10-50x speedup depending on parameters.
    """
    # Create coordinate grids
    real = np.linspace(x_min, x_max, width)
    imag = np.linspace(y_min, y_max, height)
    real_grid, imag_grid = np.meshgrid(real, imag)
    c = real_grid + 1j * imag_grid
    
    # Initialize arrays
    z = np.zeros_like(c)
    result = np.zeros(c.shape, dtype=np.float64)
    
    # Track which points haven't escaped yet
    mask = np.ones(c.shape, dtype=bool)
    
    # Iterate
    for iteration in range(max_iter):
        # Update z for points that haven't escaped
        z[mask] = z[mask] ** 2 + c[mask]
        
        # Find newly escaped points
        escaped = mask & (np.abs(z) > 2)
        
        if smooth:
            # Smooth coloring for escaped points
            abs_z = np.abs(z[escaped])
            safe_abs = np.maximum(abs_z, 1.001)
            smooth_val = iteration + 1 - np.log(np.log(safe_abs)) / np.log(2)
            result[escaped] = np.maximum(0, smooth_val)
        else:
            result[escaped] = iteration
        
        # Update mask to exclude escaped points
        mask[escaped] = False
        
        # Progress callback every 10 iterations
        if progress_callback is not None and iteration % 10 == 0:
            progress_callback(iteration, max_iter)
    
    # Points that never escaped get max_iter
    result[mask] = max_iter
    
    if progress_callback is not None:
        progress_callback(max_iter, max_iter)
    
    return result if smooth else result.astype(np.int32)


def compute_mandelbrot(
    width: int,
    height: int,
    max_iter: int,
    x_min: float = -2.0,
    x_max: float = 1.0,
    y_min: float = -1.5,
    y_max: float = 1.5,
    smooth: bool = False,
    method: ComputeMethod = ComputeMethod.NUMPY,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> np.ndarray:
    """
    Generate a 2D array representing the Mandelbrot set.
    
    This is the main entry point that dispatches to the appropriate
    computation method.
    """
    validate_parameters(width, height, max_iter, x_min, x_max, y_min, y_max)
    
    logger.info(f"Computing Mandelbrot: {width}x{height}, iter={max_iter}, method={method.value}")
    
    if method == ComputeMethod.PYTHON:
        return compute_mandelbrot_python(
            width, height, max_iter, x_min, x_max, y_min, y_max,
            smooth, progress_callback
        )
    else:
        return compute_mandelbrot_numpy(
            width, height, max_iter, x_min, x_max, y_min, y_max,
            smooth, progress_callback
        )


def compute_with_timing(
    width: int,
    height: int,
    max_iter: int,
    x_min: float = -2.0,
    x_max: float = 1.0,
    y_min: float = -1.5,
    y_max: float = 1.5,
    smooth: bool = False,
    method: ComputeMethod = ComputeMethod.NUMPY
) -> ComputeResult:
    """Compute Mandelbrot set and return result with timing metadata."""
    start_time = time.perf_counter()
    
    data = compute_mandelbrot(
        width, height, max_iter,
        x_min, x_max, y_min, y_max,
        smooth, method
    )
    
    elapsed = time.perf_counter() - start_time
    
    return ComputeResult(
        data=data,
        elapsed_time=elapsed,
        method=method,
        width=width,
        height=height,
        max_iter=max_iter
    )


def compare_methods(
    width: int = 400,
    height: int = 400,
    max_iter: int = 100
) -> Dict[str, ComputeResult]:
    """Compare performance of different computation methods."""
    results = {}
    
    for method in ComputeMethod:
        logger.info(f"Benchmarking {method.value}...")
        result = compute_with_timing(width, height, max_iter, method=method)
        results[method.value] = result
        logger.info(f"  {method.value}: {result.elapsed_time:.3f}s "
                   f"({result.points_per_second:.0f} points/sec)")
    
    return results


def get_bounds(
    center_x: float = -0.5,
    center_y: float = 0.0,
    zoom: float = 1.0
) -> Tuple[float, float, float, float]:
    """Calculate view bounds from center point and zoom level."""
    if zoom <= 0:
        raise ValueError(f"Zoom must be positive: got {zoom}")
    
    base_width = 3.0 / zoom
    base_height = 3.0 / zoom
    
    x_min = center_x - base_width / 2
    x_max = center_x + base_width / 2
    y_min = center_y - base_height / 2
    y_max = center_y + base_height / 2
    
    return (x_min, x_max, y_min, y_max)


# Predefined interesting locations
INTERESTING_LOCATIONS = {
    "default": {"center_x": -0.5, "center_y": 0.0, "zoom": 1.0},
    "seahorse": {"center_x": -0.75, "center_y": 0.1, "zoom": 20.0},
    "spiral": {"center_x": -0.761574, "center_y": -0.0847596, "zoom": 50.0},
    "elephant": {"center_x": 0.275, "center_y": 0.0, "zoom": 10.0},
    "lightning": {"center_x": -1.315, "center_y": 0.0, "zoom": 30.0},
    "mini": {"center_x": -1.768, "center_y": 0.001, "zoom": 100.0},
}


def get_preset_location(name: str) -> Tuple[float, float, float]:
    """Get coordinates for a predefined interesting location."""
    if name not in INTERESTING_LOCATIONS:
        available = ", ".join(INTERESTING_LOCATIONS.keys())
        raise KeyError(f"Unknown preset '{name}'. Available: {available}")
    
    loc = INTERESTING_LOCATIONS[name]
    return (loc["center_x"], loc["center_y"], loc["zoom"])


def list_presets() -> list:
    """Return a list of available preset location names."""
    return list(INTERESTING_LOCATIONS.keys())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Testing core.py (V2)...")
    
    data = compute_mandelbrot(100, 100, 50)
    assert data.shape == (100, 100), "Shape mismatch"
    print("  compute_mandelbrot: OK")
    
    print("\nPerformance comparison (200x200, 100 iterations):")
    results = compare_methods(200, 200, 100)
    
    python_time = results["python"].elapsed_time
    numpy_time = results["numpy"].elapsed_time
    speedup = python_time / numpy_time if numpy_time > 0 else 0
    
    print(f"\n  Python: {python_time:.3f}s")
    print(f"  NumPy:  {numpy_time:.3f}s")
    print(f"  Speedup: {speedup:.1f}x")
    
    print("\nAll tests passed!")
