# Mandelbrot Set Generator - V0 (Minimal Viable Product)

## Overview

This is V0 of the Mandelbrot Set visualization project. It provides a basic working implementation with:

- **core.py**: Mathematical computation of the Mandelbrot set
- **visualization.py**: Matplotlib-based plotting functions
- **main.py**: Entry point that ties everything together

## What is the Mandelbrot Set?

The Mandelbrot set is a famous fractal defined as the set of complex numbers `c` for which the iteration:

```
z(n+1) = z(n)² + c
```

starting with `z(0) = 0` does not diverge to infinity. Points that don't escape are colored based on how many iterations they survive.

## Requirements

- Python 3.8+
- NumPy
- Matplotlib

Install dependencies:
```bash
pip install numpy matplotlib
```

## Usage

Run the program:
```bash
python main.py
```

This will:
1. Compute the Mandelbrot set on an 800×800 grid
2. Display the result in a matplotlib window
3. Close the window to exit

## Module Structure

| File | Purpose |
|------|---------|
| `core.py` | Pure computation (no visualization) |
| `visualization.py` | All matplotlib code |
| `main.py` | Configuration and orchestration |

## V0 Limitations

This minimal version has hardcoded parameters. Future versions will add:

- **V1**: Command-line arguments, zoom, save to file
- **V2**: Interactive exploration, multiple coloring algorithms, GUI

## Example Output

The default view shows the full Mandelbrot set with the characteristic cardioid shape and circular bulb, colored by escape time using the "hot" colormap.
