# Mandelbrot Set Explorer - V2 (Final Version)

## Overview

V2 is the final, polished version of the Mandelbrot Set Explorer. It builds on V0 and V1 with enhancements including an interactive GUI, performance optimizations, and comprehensive unit tests.

## New Features in V2

| Feature | Description |
|---------|-------------|
| **Interactive GUI** | Tkinter-based explorer with click-to-zoom |
| **NumPy Optimization** | 10-50x faster computation via vectorization |
| **Performance Benchmarking** | Compare Python vs NumPy speeds |
| **Unit Tests** | Comprehensive pytest test suite |
| **Histogram Equalization** | Enhanced contrast coloring option |

## Requirements

```bash
pip install numpy matplotlib pillow
# Optional for tests:
pip install pytest
```

## Quick Start

### Interactive GUI
```bash
python main.py --gui
```

### Command Line
```bash
# Basic Mandelbrot
python main.py

# High-quality render
python main.py --preset spiral -i 1000 --smooth -c magma -o spiral.png --dpi 300

# Performance benchmark
python main.py --benchmark
```

## GUI Controls

| Action | Result |
|--------|--------|
| **Left-click** | Zoom in 2x centered on click |
| **Right-click** | Zoom out 0.5x |
| **Drag** | Pan the view |
| **Mouse wheel** | Zoom in/out |

The GUI also provides:
- Iteration slider (50-1000)
- Colormap selector (12 options)
- Smooth coloring toggle
- Preset location dropdown
- Save image button (1920x1920 PNG)

## Command-Line Options

### Modes
| Option | Description |
|--------|-------------|
| `--gui` | Launch interactive GUI |
| `--benchmark` | Run performance benchmark |

### Computation
| Option | Description |
|--------|-------------|
| `--method {python,numpy}` | Computation method (default: numpy) |
| `-i, --iterations N` | Maximum iterations (default: 200) |
| `--smooth` | Use smooth coloring |
| `--equalize` | Apply histogram equalization |

### View Position
| Option | Description |
|--------|-------------|
| `-x, --center-x X` | Center X coordinate |
| `-y, --center-y Y` | Center Y coordinate |
| `-z, --zoom N` | Zoom level |
| `-p, --preset NAME` | Use preset location |

## Performance

The NumPy-vectorized computation is faster than pure Python:

```
200x200, 100 iterations:
  Python: 0.650s (61,538 pts/sec)
  NumPy:  0.032s (1,250,000 pts/sec)
  Speedup: 20x

800x800, 200 iterations:
  Python: 12.4s (51,613 pts/sec)
  NumPy:  0.41s (1,560,976 pts/sec)
  Speedup: 30x
```

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=.

# Run specific test class
python -m pytest tests/test_core.py::TestEscapeTime -v
```

### Test Coverage

The test suite covers:
- `escape_time()` - Point escape calculation
- `escape_time_smooth()` - Smooth coloring algorithm
- `validate_parameters()` - Input validation
- `compute_mandelbrot()` - Main computation (both methods)
- `get_bounds()` - Coordinate calculation
- Preset location

## Module Structure

```
v2/
├── main.py           # CLI entry point (400 lines)
├── core.py           # Computation module (370 lines)
├── visualization.py  # Plotting module (230 lines)
├── gui.py            # Tkinter GUI (480 lines)
├── test_core.py      # Unit tests (250 lines)
└── README.md
```

**Total: ~1730 lines**

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   main.py   │────▶│   core.py    │────▶│ visualization.py│
│  (CLI/args) │     │ (computation)│     │   (plotting)    │
└─────────────┘     └──────────────┘     └─────────────────┘
       │                   │
       ▼                   ▼
┌─────────────┐     ┌──────────────┐
│   gui.py    │────▶│   PIL/Tk     │
│ (Tkinter)   │     │  (display)   │
└─────────────┘     └──────────────┘
```

## Changes from V1

### core.py
- Added `ComputeMethod` enum for algorithm selection
- Added `compute_mandelbrot_numpy()` - vectorized computation
- Added `ComputeResult` dataclass with timing metadata
- Added `compute_with_timing()` and `compare_methods()`

### visualization.py
- Added `apply_histogram_equalization()`
- Added `plot_comparison()` for side-by-side views
- Added `equalize` parameter to `plot_mandelbrot()`

### main.py
- Added `--gui` mode launcher
- Added `--benchmark` mode
- Added `--method` selection
- Added `--equalize` option

### New: gui.py
- Complete Tkinter application
- Interactive zoom/pan
- Real-time parameter adjustment
- High-resolution save

### New: tests/test_core.py
- 25+ unit tests with pytest
- Tests for all core functions
- Edge case validation

## Example Gallery

```bash
# Classic Mandelbrot
python main.py -o gallery/mandelbrot.png

# Seahorse valley (zoomed)
python main.py --preset seahorse -i 500 --smooth -c inferno -o gallery/seahorse.png

# Ultra high quality
python main.py -W 3840 -H 2160 -i 2000 --smooth --preset mini -c magma -o gallery/4k.png --dpi 300
```

## Known Limitations

- GUI requires Pillow (`pip install Pillow`)
- Very deep zooms (>10^14) may show numerical artifacts
- Large images (>4K) may be slow even with NumPy
- No GPU acceleration (could add with numba/CUDA in future)

## Future Improvements (Beyond V2)

- GPU acceleration with Numba or CuPy
- Animated zoom videos
- More fractal types (Burning Ship, Tricorn)
- Web interface with Flask/Streamlit
- Parallel computation with multiprocessing

## Authors

Paola CASSINELLI, Shanmukha Reddy GANGULA, Ketan PRUNET

## License

MIT License - Educational use
