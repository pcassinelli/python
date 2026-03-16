#!/usr/bin/env python3
"""
main.py - Mandelbrot Set Generator Entry Point (V2)

This is the main entry point for the Mandelbrot set visualization program.
It provides both CLI and GUI modes for generating and exploring fractals.

V2 Features:
- All V1 features (CLI, zoom, presets, save)
- GUI mode with interactive exploration
- Performance benchmarking
- Multiple computation methods (Python vs NumPy)

Usage Examples:
    # Launch interactive GUI
    python main.py --gui
    
    # CLI with default settings
    python main.py
    
    # Benchmark computation methods
    python main.py --benchmark
    
    # High-quality render with smooth coloring
    python main.py --preset spiral -i 1000 --smooth -c magma -o spiral.png --dpi 300
"""

import argparse
import logging
import sys
import time
from typing import Optional

from core import (
    compute_mandelbrot,
    compute_with_timing,
    compare_methods,
    get_bounds,
    get_preset_location,
    list_presets,
    INTERESTING_LOCATIONS,
    ComputeMethod
)
from visualization import (
    plot_mandelbrot,
    show_plot,
    save_plot,
    list_colormap_names,
    get_available_colormaps
)


def setup_logging(verbosity: int) -> None:
    """Configure logging based on verbosity level."""
    if verbosity == 0:
        level = logging.WARNING
    elif verbosity == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Generate and visualize Mandelbrot sets.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Display with defaults
  %(prog)s --gui                        # Launch interactive GUI
  %(prog)s -o image.png                 # Save to file
  %(prog)s --preset seahorse -i 500     # Zoom to preset location
  %(prog)s --benchmark                  # Compare computation methods
        """
    )
    
    # Mode selection
    mode_group = parser.add_argument_group("Mode")
    mode_group.add_argument(
        "--gui",
        action="store_true",
        help="Launch interactive GUI explorer"
    )
    mode_group.add_argument(
        "--benchmark",
        action="store_true",
        help="Run performance benchmark and exit"
    )
    
    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "-o", "--output",
        type=str,
        metavar="FILE",
        help="Save to file instead of displaying (PNG, JPG, PDF, SVG)"
    )
    output_group.add_argument(
        "--dpi",
        type=int,
        default=150,
        metavar="N",
        help="Output resolution in DPI (default: 150)"
    )
    
    # Image dimensions
    size_group = parser.add_argument_group("Image Size")
    size_group.add_argument(
        "-W", "--width",
        type=int,
        default=800,
        metavar="N",
        help="Image width in pixels (default: 800)"
    )
    size_group.add_argument(
        "-H", "--height",
        type=int,
        default=800,
        metavar="N",
        help="Image height in pixels (default: 800)"
    )
    
    # Computation parameters
    compute_group = parser.add_argument_group("Computation")
    compute_group.add_argument(
        "-i", "--iterations",
        type=int,
        default=200,
        metavar="N",
        help="Maximum iterations (default: 200)"
    )
    compute_group.add_argument(
        "--smooth",
        action="store_true",
        help="Use smooth coloring algorithm"
    )
    compute_group.add_argument(
        "--method",
        type=str,
        choices=["python", "numpy"],
        default="numpy",
        help="Computation method (default: numpy)"
    )
    
    # View/position options
    view_group = parser.add_argument_group("View Position")
    view_group.add_argument(
        "-x", "--center-x",
        type=float,
        default=None,
        metavar="X",
        help="Center X coordinate (real axis)"
    )
    view_group.add_argument(
        "-y", "--center-y",
        type=float,
        default=None,
        metavar="Y",
        help="Center Y coordinate (imaginary axis)"
    )
    view_group.add_argument(
        "-z", "--zoom",
        type=float,
        default=1.0,
        metavar="N",
        help="Zoom level (default: 1.0)"
    )
    view_group.add_argument(
        "-p", "--preset",
        type=str,
        choices=list_presets(),
        metavar="NAME",
        help=f"Use preset location"
    )
    
    # Visualization options
    vis_group = parser.add_argument_group("Visualization")
    vis_group.add_argument(
        "-c", "--colormap",
        type=str,
        default="hot",
        metavar="NAME",
        help="Colormap name (default: hot)"
    )
    vis_group.add_argument(
        "--no-axes",
        action="store_true",
        help="Hide axes and labels"
    )
    vis_group.add_argument(
        "--no-colorbar",
        action="store_true",
        help="Hide the colorbar"
    )
    vis_group.add_argument(
        "-t", "--title",
        type=str,
        default=None,
        metavar="TEXT",
        help="Custom title for the plot"
    )
    vis_group.add_argument(
        "--equalize",
        action="store_true",
        help="Apply histogram equalization for better contrast"
    )
    
    # Information options
    info_group = parser.add_argument_group("Information")
    info_group.add_argument(
        "--list-presets",
        action="store_true",
        help="List available preset locations and exit"
    )
    info_group.add_argument(
        "--list-colormaps",
        action="store_true",
        help="List available colormaps and exit"
    )
    
    # Verbosity
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v for INFO, -vv for DEBUG)"
    )
    
    return parser


def handle_info_commands(args) -> bool:
    """Handle information commands (--list-*)."""
    if args.list_presets:
        print("Available Mandelbrot preset locations:")
        print("-" * 60)
        for name, loc in INTERESTING_LOCATIONS.items():
            print(f"  {name:12} center=({loc['center_x']:8.4f}, {loc['center_y']:8.4f}), zoom={loc['zoom']}")
        return True
    
    if args.list_colormaps:
        print("Available colormaps:")
        print("-" * 60)
        for name, desc in get_available_colormaps().items():
            print(f"  {name:12} {desc}")
        return True
    
    return False


def run_benchmark(args) -> int:
    """Run performance benchmark."""
    print("=" * 60)
    print("Mandelbrot Performance Benchmark")
    print("=" * 60)
    
    sizes = [(200, 200), (400, 400), (800, 800)]
    
    for width, height in sizes:
        print(f"\n{width}x{height} pixels, {args.iterations} iterations:")
        print("-" * 40)
        
        results = compare_methods(width, height, args.iterations)
        
        python_result = results["python"]
        numpy_result = results["numpy"]
        
        speedup = python_result.elapsed_time / numpy_result.elapsed_time
        
        print(f"  Python: {python_result.elapsed_time:8.3f}s "
              f"({python_result.points_per_second:,.0f} pts/sec)")
        print(f"  NumPy:  {numpy_result.elapsed_time:8.3f}s "
              f"({numpy_result.points_per_second:,.0f} pts/sec)")
        print(f"  Speedup: {speedup:.1f}x")
    
    return 0


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger("mandelbrot")
    
    # Handle info commands
    if handle_info_commands(args):
        return 0
    
    # Launch GUI if requested
    if args.gui:
        try:
            from gui import main as gui_main
            return gui_main()
        except ImportError as e:
            print(f"Error: Could not launch GUI: {e}")
            print("Make sure Pillow is installed: pip install Pillow")
            return 1
    
    # Run benchmark if requested
    if args.benchmark:
        return run_benchmark(args)
        
    # Determine center coordinates
    if args.preset:
        center_x, center_y, zoom = get_preset_location(args.preset)
        if args.zoom != 1.0:
            zoom = args.zoom
    else:
        center_x = args.center_x if args.center_x is not None else -0.5
        center_y = args.center_y if args.center_y is not None else 0.0
        zoom = args.zoom
        
    x_min, x_max, y_min, y_max = get_bounds(center_x, center_y, zoom)
    
    # Get computation method
    method = ComputeMethod.NUMPY if args.method == "numpy" else ComputeMethod.PYTHON
    
    # Print configuration
    print("=" * 60)
    print(f"Mandelbrot Set Generator - V2")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Resolution:    {args.width} x {args.height} pixels")
    print(f"  Iterations:    {args.iterations}")
    print(f"  Method:        {method.value}")
    print(f"  Center:        ({center_x}, {center_y})")
    print(f"  Zoom:          {zoom}x")
    print(f"  Colormap:      {args.colormap}")
    print(f"  Smooth:        {args.smooth}")
    if args.output:
        print(f"  Output:        {args.output} @ {args.dpi} DPI")
    
    # Compute
    print(f"\nComputing...")
    start_time = time.time()
    
    try:
        data = compute_mandelbrot(
            width=args.width,
            height=args.height,
            max_iter=args.iterations,
            x_min=x_min,
            x_max=x_max,
            y_min=y_min,
            y_max=y_max,
            smooth=args.smooth,
            method=method
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    elapsed = time.time() - start_time
    print(f"  Completed in {elapsed:.2f} seconds")
    print(f"  Points computed: {args.width * args.height:,}")
    print(f"  Speed: {args.width * args.height / elapsed:,.0f} points/sec")
    
    # Create visualization
    print("\nCreating visualization...")

    fig = plot_mandelbrot(
        data=data,
        x_min=x_min,
        x_max=x_max,
        y_min=y_min,
        y_max=y_max,
        colormap=args.colormap,
        title=args.title,
        show_axes=not args.no_axes,
        show_colorbar=not args.no_colorbar,
        equalize=args.equalize
    )
    
    # Output
    if args.output:
        save_plot(fig, args.output, dpi=args.dpi)
        print(f"\nSaved to: {args.output}")
    else:
        print("\nDisplaying (close window to exit)...")
        show_plot(fig)
    
    print("\nDone!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
