"""
visualization.py - Mandelbrot Set Visualization Module (V1)

This module handles all plotting and display functionality for the Mandelbrot set.

V1 Enhancements over V0:
- More colormap options with descriptions
- Better save functionality with format detection
- Figure size configuration
- Optional axis display
"""

import numpy as np
import matplotlib.pyplot as plt
import logging

# Configure module logger
logger = logging.getLogger(__name__)


# Available colormaps with descriptions
COLORMAPS = {
    "hot": "Classic warm (black → red → yellow → white)",
    "inferno": "Perceptually uniform, warm tones",
    "magma": "Perceptually uniform, purple-orange",
    "plasma": "Perceptually uniform, purple-yellow",
    "viridis": "Perceptually uniform, green-blue-yellow",
    "twilight": "Cyclic, good for highlighting structure",
    "cubehelix": "Designed to show detail uniformly",
    "Blues": "Cool blue tones",
    "Spectral": "Diverging, rainbow-like",
    "ocean": "Deep blue ocean colors",
    "terrain": "Earth-like colors",
    "gnuplot2": "Classic scientific visualization",
}


def get_available_colormaps():
    """
    Return available colormaps with their descriptions.
    """
    return COLORMAPS.copy()


def list_colormap_names():
    """
    Return just the names of available colormaps.
    """
    return list(COLORMAPS.keys())


def plot_mandelbrot(data, x_min = -2.0, x_max = 1.0, y_min = -1.5, y_max = 1.5, colormap = "hot", title = None, figsize = (10, 10), show_axes = True, show_colorbar = True):
    """
    Create a matplotlib figure of the Mandelbrot set.
    """
    logger.info(f"Creating plot with colormap '{colormap}'")
    
    # Validate colormap
    if colormap not in plt.colormaps():
        logger.warning(f"Unknown colormap '{colormap}', falling back to 'hot'")
        colormap = "hot"
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Display the data as an image
    image = ax.imshow(data, extent = (x_min, x_max, y_min, y_max), cmap = colormap, origin = "lower", aspect = "equal")
    
    # Colorbar
    if show_colorbar:
        colorbar = fig.colorbar(image, ax = ax, shrink = 0.8)
        colorbar.set_label("Iterations to escape", fontsize = 10)
    
    # Axes
    if show_axes:
        ax.set_xlabel("Real (Re)", fontsize = 12)
        ax.set_ylabel("Imaginary (Im)", fontsize = 12)
    else:
        ax.axis("off")
    
    # Title
    if title is None:
        max_iter = int(data.max())
        title = f"Mandelbrot Set ({max_iter} iterations)"
    ax.set_title(title, fontsize = 14)
    
    plt.tight_layout()
    
    return fig


def show_plot(fig = None):
    """
    Display the current matplotlib figure.
    """
    logger.info("Displaying plot")
    plt.show()


def save_plot(fig, filename, dpi = 150, transparent = False):
    """
    Save a matplotlib figure to a file.
    """
    logger.info(f"Saving plot to '{filename}' at {dpi} DPI")
    
    fig.savefig(filename, dpi = dpi, bbox_inches = "tight", transparent = transparent)
    
    logger.info(f"Successfully saved: {filename}")
    return filename
