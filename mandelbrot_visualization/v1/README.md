# Mandelbrot Set Generator - V1 (Extended Functionality)

## Overview

V1 builds on the V0 foundation by adding a complete command-line interface,
configurable parameters, and additional features for exploring the Mandelbrot set.

## New Features in V1

| Feature | Description |
|---------|-------------|
| **CLI with argparse** | Full command-line control over all parameters |
| **Zoom & Pan** | Explore any region with `--center-x`, `--center-y`, `--zoom` |
| **Preset Locations** | Quick access to interesting areas with `--preset` |
| **Smooth Coloring** | Anti-aliased rendering with `--smooth` |
| **File Output** | Save to PNG, JPG, PDF, SVG with `--output` |
| **Logging** | Debug info with `-v` or `-vv` |
| **Input Validation** | Helpful error messages for invalid parameters |

## Requirements

```bash
pip install numpy matplotlib
```

## Quick Start

```bash
# Display with default settings
python main.py

# Save a high-resolution image
python main.py --output mandelbrot.png --width 1920 --height 1080 --dpi 300

# Explore the seahorse valley
python main.py --preset seahorse --iterations 500 --smooth

# Custom location
python main.py --center-x -0.75 --center-y 0.1 --zoom 50 --colormap inferno
```

## Command-Line Options

### Output Options
| Option | Description |
|--------|-------------|
| `-o, --output FILE` | Save to file instead of displaying |
| `--dpi N` | Resolution for saved images (default: 150) |

### Image Size
| Option | Description |
|--------|-------------|
| `-W, --width N` | Width in pixels (default: 800) |
| `-H, --height N` | Height in pixels (default: 800) |

### Computation
| Option | Description |
|--------|-------------|
| `-i, --iterations N` | Max iterations (default: 200) |
| `--smooth` | Use smooth coloring algorithm |

### View Position
| Option | Description |
|--------|-------------|
| `-x, --center-x X` | Center X coordinate |
| `-y, --center-y Y` | Center Y coordinate |
| `-z, --zoom N` | Zoom level (default: 1.0) |
| `-p, --preset NAME` | Use a preset location |

### Visualization
| Option | Description |
|--------|-------------|
| `-c, --colormap NAME` | Color scheme (default: hot) |
| `--no-axes` | Hide axes and labels |
| `--no-colorbar` | Hide the colorbar |
| `-t, --title TEXT` | Custom title |

### Information
| Option | Description |
|--------|-------------|
| `--list-presets` | Show available presets |
| `--list-colormaps` | Show available colormaps |
| `-v, --verbose` | Increase verbosity |

## Preset Locations

View all presets with `python main.py --list-presets`:

| Name | Description |
|------|-------------|
| `default` | Full Mandelbrot set view |
| `seahorse` | Seahorse valley - intricate spirals |
| `spiral` | Deep spiral structure |
| `elephant` | Elephant valley |
| `lightning` | Lightning-like patterns |

## Available Colormaps

View all with `python main.py --list-colormaps`:

- `hot` - Classic warm colors
- `inferno` - Perceptually uniform, warm
- `magma` - Purple to orange
- `plasma` - Purple to yellow
- `viridis` - Green to yellow
- `twilight` - Cyclic, good for structure
- `cubehelix` - Shows detail uniformly
- `Blues` - Cool blue tones

## Examples

### Generate a poster-quality image
```bash
python main.py -W 3840 -H 2160 -i 1000 --smooth -c magma -o poster.png --dpi 300
```

### Explore deep zoom
```bash
python main.py -x -0.761574 -y -0.0847596 -z 1000 -i 2000 --smooth
```

### Verbose mode for debugging
```bash
python main.py -vv --preset spiral
```

## Module Structure

| File | Lines | Purpose |
|------|-------|---------|
| `core.py` | ~150 | Computation, validation, presets |
| `visualization.py` | ~100 | Plotting, colormaps, saving |
| `main.py` | ~200 | CLI parsing and orchestration |

**Total: ~450 lines**

## Changes from V0

### core.py
- Added `escape_time_smooth()` for anti-aliased coloring
- Added `validate_parameters()` for input checking
- Added `progress_callback` parameter to `compute_mandelbrot()`
- Added `INTERESTING_LOCATIONS` dictionary
- Added `get_preset_location()` and `list_presets()`
- Added logging throughout

### visualization.py
- Extended `COLORMAPS` dictionary with descriptions
- Added `show_axes` and `show_colorbar` parameters
- Added `figsize` parameter
- Added logging

### main.py
- Complete rewrite with argparse
- Modular argument groups
- Progress logging with callback
- Timing information
- Info commands (--list-presets, --list-colormaps)

## V2 Preview

The final version will add:
- Interactive zoom (click to explore)
- GUI with Tkinter
- Unit tests with pytest
