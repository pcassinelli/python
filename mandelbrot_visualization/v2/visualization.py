"""
visualization.py - Mandelbrot Set Visualization Module (V2)

This module handles all plotting and display functionality for the
Mandelbrot set.

V2 Enhancements:
- Histogram equalization coloring option
- Side-by-side comparison plots
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.colors import Normalize
import logging
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)


# Available colormaps with descriptions
COLORMAPS = {
    "hot": "Classic warm (black -> red -> yellow -> white)",
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


def get_available_colormaps() -> dict:
    """Return available colormaps with their descriptions."""
    return COLORMAPS.copy()


def list_colormap_names() -> list:
    """Return just the names of available colormaps."""
    return list(COLORMAPS.keys())


def apply_histogram_equalization(data: np.ndarray) -> np.ndarray:
    """
    Apply histogram equalization to enhance contrast.
    
    This redistributes the iteration counts to use the full
    color range more evenly, revealing more detail.
    
    Args:
        data: 2D array of iteration counts.
    
    Returns:
        Equalized data array (float, 0-1 range).
    """
    flat = data.flatten()
    
    # Get histogram
    hist, bin_edges = np.histogram(flat, bins=256, density=True)
    
    # Compute CDF
    cdf = hist.cumsum()
    cdf = cdf / cdf[-1]  # Normalize
    
    # Interpolate to get equalized values
    equalized = np.interp(flat, bin_edges[:-1], cdf)
    
    return equalized.reshape(data.shape)


def plot_mandelbrot(
    data: np.ndarray,
    x_min: float = -2.0,
    x_max: float = 1.0,
    y_min: float = -1.5,
    y_max: float = 1.5,
    colormap: str = "hot",
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 10),
    show_axes: bool = True,
    show_colorbar: bool = True,
    equalize: bool = False
) -> Figure:
    """
    Create a matplotlib figure of the Mandelbrot set.
    
    Args:
        data: 2D numpy array of iteration counts.
        x_min, x_max, y_min, y_max: Coordinate bounds for axis labels.
        colormap: Matplotlib colormap name.
        title: Title for the plot. If None, generates automatic title.
        figsize: Figure size as (width, height) in inches.
        show_axes: Whether to display axis labels and ticks.
        show_colorbar: Whether to display the colorbar.
        equalize: If True, apply histogram equalization.
    
    Returns:
        The matplotlib Figure object.
    """
    logger.info(f"Creating plot with colormap '{colormap}'")
    
    if colormap not in plt.colormaps():
        logger.warning(f"Unknown colormap '{colormap}', falling back to 'hot'")
        colormap = "hot"
    
    # Apply equalization if requested
    plot_data = apply_histogram_equalization(data) if equalize else data
    
    fig, ax = plt.subplots(figsize=figsize)
    
    image = ax.imshow(
        plot_data,
        extent=(x_min, x_max, y_min, y_max),
        cmap=colormap,
        origin="lower",
        aspect="equal"
    )
    
    if show_colorbar:
        colorbar = fig.colorbar(image, ax=ax, shrink=0.8)
        label = "Normalized" if equalize else "Iterations to escape"
        colorbar.set_label(label, fontsize=10)
    
    if show_axes:
        ax.set_xlabel("Real (Re)", fontsize=12)
        ax.set_ylabel("Imaginary (Im)", fontsize=12)
    else:
        ax.axis("off")
    
    if title is None:
        max_iter = int(data.max())
        title = f"Mandelbrot Set ({max_iter} iterations)"
    ax.set_title(title, fontsize=14)
    
    plt.tight_layout()
    return fig


def plot_comparison(
    data_list: List[np.ndarray],
    titles: List[str],
    x_min: float = -2.0,
    x_max: float = 1.0,
    y_min: float = -1.5,
    y_max: float = 1.5,
    colormap: str = "hot"
) -> Figure:
    """
    Create a side-by-side comparison of multiple datasets.
    
    Args:
        data_list: List of 2D arrays to compare.
        titles: List of titles for each subplot.
        x_min, x_max, y_min, y_max: Coordinate bounds.
        colormap: Colormap to use for all plots.
    
    Returns:
        Figure with subplots.
    """
    n = len(data_list)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 5))
    
    if n == 1:
        axes = [axes]
    
    for ax, data, title in zip(axes, data_list, titles):
        im = ax.imshow(
            data,
            extent=(x_min, x_max, y_min, y_max),
            cmap=colormap,
            origin="lower",
            aspect="equal"
        )
        ax.set_title(title, fontsize=12)
        ax.axis("off")
    
    plt.tight_layout()
    return fig


def show_plot(fig: Figure = None) -> None:
    """Display the current matplotlib figure."""
    logger.info("Displaying plot")
    plt.show()


def save_plot(
    fig: Figure,
    filename: str,
    dpi: int = 150,
    transparent: bool = False
) -> str:
    """
    Save a matplotlib figure to a file.
    
    Args:
        fig: The Figure object to save.
        filename: Output filename.
        dpi: Resolution in dots per inch.
        transparent: Whether to use transparent background.
    
    Returns:
        The filename that was saved.
    """
    logger.info(f"Saving plot to '{filename}' at {dpi} DPI")
    fig.savefig(filename, dpi=dpi, bbox_inches="tight", transparent=transparent)
    logger.info(f"Successfully saved: {filename}")
    return filename


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    print("Testing visualization.py (V2)...")
    
    print(f"\nAvailable colormaps: {len(COLORMAPS)}")
    
    # Test with dummy data
    test_data = np.random.randint(0, 100, size=(100, 100))
    
    fig = plot_mandelbrot(test_data, title="Test Plot")
    print("  plot_mandelbrot: OK")
    
    fig_eq = plot_mandelbrot(test_data, equalize=True, title="Equalized")
    print("  plot_mandelbrot (equalized): OK")
    
    plt.close("all")
    print("\nAll tests passed!")
