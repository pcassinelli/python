"""
visualization.py - Mandelbrot Set Visualization Module

This module handles all plotting and display functionality for the Mandelbrot set.
"""

import matplotlib.pyplot as plt


def plot_mandelbrot(data, x_min = -2.0, x_max = 1.0, y_min = -1.5, y_max = 1.5, colormap = "hot", title = "Mandelbrot Set"):
    """
    Create a matplotlib figure of the Mandelbrot set.
    """
    # Create figure with appropriate size
    fig, ax = plt.subplots(figsize = (10, 10))
    
    # Display the data as an image
    image = ax.imshow(data, extent = (x_min, x_max, y_min, y_max), cmap = colormap, origin = "lower", aspect = "equal")
    
    # Add colorbar to show iteration count scale
    colorbar = fig.colorbar(image, ax = ax, shrink = 0.8)
    colorbar.set_label("Iterations to escape", fontsize = 10)
    
    # Labels and title
    ax.set_xlabel("Real (Re)", fontsize = 12)
    ax.set_ylabel("Imaginary (Im)", fontsize = 12)
    ax.set_title(title, fontsize = 14)
    
    return fig


def show_plot(fig = None):
    """
    Display the current matplotlib figure.
    """
    plt.show()


def save_plot(fig, filename, dpi = 150):
    """
    Save a matplotlib figure to a file.
    """
    fig.savefig(filename, dpi = dpi, bbox_inches = "tight")
    print(f"Saved plot to: {filename}")
