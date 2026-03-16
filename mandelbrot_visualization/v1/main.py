#!/usr/bin/env python3
"""
main.py - Mandelbrot Set Generator Entry Point (V1)

This is the main entry point for the Mandelbrot set visualization program.
It provides a full command-line interface for generating and exploring the Mandelbrot set.

V1 Features:
- Full CLI with argparse
- Configurable resolution, iterations, colormap
- Zoom and pan with center coordinates
- Preset locations for interesting areas
- Save to file with configurable DPI
- Smooth coloring option
- Logging with configurable verbosity
"""

import argparse
import logging
import sys
import time

from core import (compute_mandelbrot, get_bounds, get_preset_location, list_presets, INTERESTING_LOCATIONS)
from visualization import (plot_mandelbrot, show_plot, save_plot, list_colormap_names, get_available_colormaps)


def setup_logging(verbosity):
    """
    Configure logging based on verbosity level.
    """
    if verbosity == 0:
        level = logging.WARNING
    elif verbosity == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG
    
    logging.basicConfig(level = level, format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt = "%H:%M:%S")


def create_progress_logger(logger):
    """
    Create a progress callback that logs computation progress.
    """
    last_percent = [0]  # Use list to allow modification in nested function
    
    def log_progress(current, total):
        percent = int(100 * current / total)
        # Log every 10%
        if percent >= last_percent[0] + 10:
            logger.info(f"Progress: {percent}% ({current}/{total} rows)")
            last_percent[0] = percent
    
    return log_progress


def create_parser():
    """
    Create and configure the argument parser.
    """
    parser = argparse.ArgumentParser(description = "Generate and visualize the Mandelbrot set.")
    
    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument("-o", "--output", type = str, metavar = "FILE", help = "Save to file instead of displaying (PNG, JPG, PDF, SVG)")
    output_group.add_argument("--dpi", type = int, default = 150, metavar = "N", help = "Output resolution in DPI (default: 150)")
    
    # Image dimensions
    size_group = parser.add_argument_group("Image Size")
    size_group.add_argument("-W", "--width", type = int, default = 800, metavar = "N",help = "Image width in pixels (default: 800)")
    size_group.add_argument("-H", "--height", type = int, default = 800, metavar = "N", help = "Image height in pixels (default: 800)")
    
    # Computation parameters
    compute_group = parser.add_argument_group("Computation")
    compute_group.add_argument("-i", "--iterations", type = int, default = 200, metavar = "N", help = "Maximum iterations (default: 200, more = finer detail)")
    compute_group.add_argument("--smooth", action = "store_true", help = "Use smooth coloring algorithm (reduces banding)")
    
    # View/position options
    view_group = parser.add_argument_group("View Position")
    view_group.add_argument("-x", "--center-x", type = float, default = None, metavar = "X", help = "Center X coordinate (real axis)")
    view_group.add_argument("-y", "--center-y", type = float, default = None, metavar = "Y", help = "Center Y coordinate (imaginary axis)")
    view_group.add_argument("-z", "--zoom", type = float, default = 1.0, metavar = "N", help = "Zoom level (default: 1.0, higher = more zoom)")
    view_group.add_argument("-p", "--preset", type = str, choices = list_presets(), metavar = "NAME", help = f"Use preset location: {', '.join(list_presets())}")
    
    # Visualization options
    vis_group = parser.add_argument_group("Visualization")
    vis_group.add_argument("-c", "--colormap",type = str,default = "hot", metavar = "NAME", help = "Colormap name (default: hot)")
    vis_group.add_argument("--no-axes", action = "store_true", help = "Hide axes and labels")
    vis_group.add_argument("--no-colorbar", action = "store_true", help = "Hide the colorbar")
    vis_group.add_argument("-t", "--title", type = str, default = None, metavar = "TEXT", help = "Custom title for the plot")
    
    # Information options
    info_group = parser.add_argument_group("Information")
    info_group.add_argument("--list-presets", action = "store_true", help = "List available preset locations and exit")
    info_group.add_argument("--list-colormaps", action = "store_true", help = "List available colormaps and exit")
    
    # Verbosity
    parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity (-v for INFO, -vv for DEBUG)")
    
    return parser


def handle_info_commands(args):
    """
    Handle --list-presets and --list-colormaps commands.
    """
    if args.list_presets:
        print("Available preset locations:")
        print("-" * 50)
        for name, loc in INTERESTING_LOCATIONS.items():
            print(f"  {name: 12} center = ({loc['center_x']}, {loc['center_y']}), zoom = {loc['zoom']}")
        return True
    
    if args.list_colormaps:
        print("Available colormaps:")
        print("-" * 50)
        for name, desc in get_available_colormaps().items():
            print(f"  {name: 12} {desc}")
        return True
    
    return False


def main():
    """
    Main entry point.
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger("mandelbrot")
    
    # Handle info commands
    if handle_info_commands(args):
        return 0
    
    # Determine center coordinates
    if args.preset:
        center_x, center_y, zoom = get_preset_location(args.preset)
        logger.info(f"Using preset '{args.preset}'")
        # Allow zoom override even with preset
        if args.zoom != 1.0:
            zoom = args.zoom
    else:
        center_x = args.center_x if args.center_x is not None else -0.5
        center_y = args.center_y if args.center_y is not None else 0.0
        zoom = args.zoom
    
    # Calculate bounds
    x_min, x_max, y_min, y_max = get_bounds(center_x, center_y, zoom)
    
    # Print configuration
    print(f"\nConfiguration:")
    print(f"  Resolution:    {args.width} x {args.height} pixels")
    print(f"  Iterations:    {args.iterations}")
    print(f"  Center:        ({center_x}, {center_y})")
    print(f"  Zoom:          {zoom}x")
    print(f"  Colormap:      {args.colormap}")
    print(f"  Smooth:        {args.smooth}")
    if args.output:
        print(f"  Output:        {args.output} @ {args.dpi} DPI")
    else:
        print(f"  Output:        Display window")
    
    # Compute
    print(f"\nComputing Mandelbrot set...")
    start_time = time.time()
    
    progress_callback = create_progress_logger(logger) if args.verbose else None
    
    try:
        data = compute_mandelbrot(width = args.width, height = args.height, max_iter = args.iterations, x_min = x_min, x_max = x_max, y_min = y_min, y_max = y_max, smooth = args.smooth, progress_callback = progress_callback)
    except ValueError as e:
        print(f"Error: {e}", file = sys.stderr)
        return 1
    
    elapsed = time.time() - start_time
    print(f"  Completed in {elapsed: .2f} seconds")
    print(f"  Points computed: {args.width * args.height: ,}")
    
    # Create visualization
    print("\nCreating visualization...")
    
    fig = plot_mandelbrot(data = data, x_min = x_min, x_max = x_max, y_min = y_min, y_max = y_max, colormap = args.colormap, title = args.title, show_axes = not args.no_axes, show_colorbar = not args.no_colorbar)
    
    # Output
    if args.output:
        save_plot(fig, args.output, dpi = args.dpi)
        print(f"\nSaved to: {args.output}")
    else:
        print("\nDisplaying...")
        show_plot(fig)
    
    print("\nDone!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
