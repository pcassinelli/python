"""
main.py - Mandelbrot Set Generator Entry Point

This is the main entry point for the Mandelbrot set visualization program.
"""

from core import compute_mandelbrot
from visualization import plot_mandelbrot, show_plot


def main():
    """
    Main function to generate and display the Mandelbrot set.
    """
    # Image dimensions
    width = 800
    height = 800
    
    # Iteration limit
    max_iterations = 200
    
    # View bounds
    x_min, x_max = -2.0, 1.0
    y_min, y_max = -1.5, 1.5
    
    # Color scheme
    colormap = "hot"
    
    # Generate the fractal data
    data = compute_mandelbrot(width = width, height = height, max_iter = max_iterations, x_min = x_min, x_max = x_max, y_min = y_min, y_max = y_max)
    
    # Create the plot
    fig = plot_mandelbrot(data = data, x_min = x_min, x_max = x_max, y_min = y_min, y_max = y_max, colormap = colormap, title = f"Mandelbrot Set ({max_iterations} iterations)")
    
    # Show the plot
    show_plot(fig)


if __name__ == "__main__":
    main()
