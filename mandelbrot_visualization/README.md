# Mandelbrot Set Explorer

A Python project that generates and visualizes the Mandelbrot set using matplotlib for graphical representation. This project demonstrates complex number computations and fractal geometry.

## Project Overview

This project implements an interactive Mandelbrot set explorer, developed in three stages:

| Version | Description | Status |
|---------|-------------|--------|
| **V0** | Minimal viable product - basic generation and display |
| **V1** | Extended functionality - CLI, zoom, save to file |
| **V2** | Final version - interactive GUI, multiple algorithms |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the latest version
cd v2
python main.py
```

## Project Structure

```
mandelbrot_project/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── v0/                    # Minimal viable product
│   ├── README.md
│   ├── core.py           # Computation module
│   ├── visualization.py  # Plotting module
│   └── main.py           # Entry point
├── v1/                    # Extended functionality
│   ├── README.md
│   ├── core.py           # Computation module
│   ├── visualization.py  # Plotting module
│   └── main.py           # Entry point
├── v2/                    # Final version
│   ├── README.md
│   ├── core.py           # Computation module
│   ├── visualization.py  # Plotting module
│   └── main.py           # Entry point
│   └── gui.py            # Tkinter GUI
│   └── test_core.py      # Unit tests
```

## The Mandelbrot Set

The Mandelbrot set is defined as the set of complex numbers `c` for which the sequence:

```
z₀ = 0
zₙ₊₁ = zₙ² + c
```

remains bounded. In practice, if |z| > 2, the sequence will diverge to infinity.

### Why This Project?

1. **Mathematical Beauty**: Fractals demonstrate infinite complexity from simple rules
2. **Computational Concepts**: Iteration, complex numbers, convergence
3. **Python Skills**: NumPy arrays, matplotlib visualization, modular design
4. **Software Engineering**: Clean architecture, documentation, staged development

## Development Stages

### V0: Minimal Viable Product
- Core computation algorithm
- Basic matplotlib visualization  
- Hardcoded parameters

### V1: Extended Functionality
- `argparse` for command-line control
- Configurable resolution, iterations, bounds
- Zoom to specific coordinates
- Save output to PNG file
- `logging` for progress tracking

### V2: Final Version
- Interactive zoom (click to explore)
- Multiple coloring algorithms (smooth, histogram equalization)
- Performance comparison (pure Python vs. vectorized NumPy)
- Simple GUI with Tkinter
- Unit tests with pytest
- Input validation and error handling

## Authors

Paola CASSINELLI, Shanmukha Reddy GANGULA, Ketan PRUNET

## Course

Introduction to Python Programming - Final Project

## License

MIT License - Educational use
