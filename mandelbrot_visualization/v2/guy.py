"""
gui.py - Interactive Mandelbrot Explorer GUI (V2)

This module provides a Tkinter-based graphical interface for exploring
the Mandelbrot set interactively. Features include:
- Click to zoom in/out
- Drag to pan
- Real-time parameter adjustment
- Colormap selection
- Save current view

Usage:
    python gui.py
    
Or from main.py:
    python main.py --gui
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from PIL import Image, ImageTk
import logging
import threading
from typing import Optional, Tuple
import io

from core import (
    compute_mandelbrot,
    get_bounds,
    list_presets,
    get_preset_location,
    ComputeMethod
)
from visualization import list_colormap_names

logger = logging.getLogger(__name__)


class MandelbrotExplorer(tk.Tk):
    """
    Interactive Mandelbrot set explorer with Tkinter GUI.
    
    Features:
    - Left-click: Zoom in (2x) centered on click point
    - Right-click: Zoom out (0.5x)
    - Drag: Pan the view
    - Controls panel for parameters
    """
    
    def __init__(self):
        super().__init__()
        
        self.title("Mandelbrot Explorer")
        self.geometry("1000x700")
        
        # Current view state
        self.center_x = -0.5
        self.center_y = 0.0
        self.zoom = 1.0
        self.max_iter = 200
        self.colormap = "hot"
        self.smooth = True
        self.width = 600
        self.height = 600
        
        # Drag state
        self.drag_start = None
        self.drag_start_center = None
        
        # Current image data
        self.current_data = None
        self.photo_image = None
        
        # Computing flag
        self.computing = False
        
        self._create_widgets()
        self._bind_events()
        
        # Initial render
        self.after(100, self.render)
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Canvas
        canvas_frame = ttk.LabelFrame(main_frame, text="Mandelbrot Set")
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(
            canvas_frame,
            width=self.width,
            height=self.height,
            bg="black"
        )
        self.canvas.pack(padx=5, pady=5)
        
        # Right panel - Controls
        control_frame = ttk.LabelFrame(main_frame, text="Controls")
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(control_frame, textvariable=self.status_var)
        status_label.pack(pady=5)
        
        # Coordinates display
        coord_frame = ttk.LabelFrame(control_frame, text="Current View")
        coord_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.coord_var = tk.StringVar()
        self._update_coord_display()
        coord_label = ttk.Label(coord_frame, textvariable=self.coord_var, font=("Courier", 9))
        coord_label.pack(padx=5, pady=5)
        
        # Iterations slider
        iter_frame = ttk.LabelFrame(control_frame, text="Max Iterations")
        iter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.iter_var = tk.IntVar(value=self.max_iter)
        iter_slider = ttk.Scale(
            iter_frame,
            from_=50,
            to=1000,
            variable=self.iter_var,
            orient=tk.HORIZONTAL
        )
        iter_slider.pack(fill=tk.X, padx=5)
        
        iter_label = ttk.Label(iter_frame, textvariable=self.iter_var)
        iter_label.pack()
        
        # Colormap selector
        cmap_frame = ttk.LabelFrame(control_frame, text="Colormap")
        cmap_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.cmap_var = tk.StringVar(value=self.colormap)
        cmap_combo = ttk.Combobox(
            cmap_frame,
            textvariable=self.cmap_var,
            values=list_colormap_names(),
            state="readonly"
        )
        cmap_combo.pack(fill=tk.X, padx=5, pady=5)
        cmap_combo.bind("<<ComboboxSelected>>", lambda e: self.render())
        
        # Smooth coloring checkbox
        self.smooth_var = tk.BooleanVar(value=self.smooth)
        smooth_check = ttk.Checkbutton(
            control_frame,
            text="Smooth coloring",
            variable=self.smooth_var,
            command=self.render
        )
        smooth_check.pack(pady=5)
        
        # Preset locations
        preset_frame = ttk.LabelFrame(control_frame, text="Presets")
        preset_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.preset_var = tk.StringVar(value="default")
        preset_combo = ttk.Combobox(
            preset_frame,
            textvariable=self.preset_var,
            values=list_presets(),
            state="readonly"
        )
        preset_combo.pack(fill=tk.X, padx=5, pady=5)
        preset_combo.bind("<<ComboboxSelected>>", self._on_preset_selected)
        
        # Buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=10)
        
        render_btn = ttk.Button(btn_frame, text="Render", command=self.render)
        render_btn.pack(fill=tk.X, pady=2)
        
        reset_btn = ttk.Button(btn_frame, text="Reset View", command=self.reset_view)
        reset_btn.pack(fill=tk.X, pady=2)
        
        save_btn = ttk.Button(btn_frame, text="Save Image", command=self.save_image)
        save_btn.pack(fill=tk.X, pady=2)
        
        # Help text
        help_frame = ttk.LabelFrame(control_frame, text="Controls")
        help_frame.pack(fill=tk.X, padx=5, pady=5)
        
        help_text = """Left-click: Zoom in (2x)
Right-click: Zoom out (0.5x)
Drag: Pan view
Scroll: Zoom in/out"""
        help_label = ttk.Label(help_frame, text=help_text, font=("Arial", 9))
        help_label.pack(padx=5, pady=5)
    
    def _bind_events(self):
        """Bind mouse and keyboard events."""
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<Button-3>", self._on_right_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_drag_end)
        self.canvas.bind("<MouseWheel>", self._on_scroll)
        # Linux scroll
        self.canvas.bind("<Button-4>", lambda e: self._on_scroll_linux(e, 1))
        self.canvas.bind("<Button-5>", lambda e: self._on_scroll_linux(e, -1))
    
    def _update_coord_display(self):
        """Update the coordinate display."""
        x_min, x_max, y_min, y_max = get_bounds(self.center_x, self.center_y, self.zoom)
        self.coord_var.set(
            f"Center: ({self.center_x:.6f}, {self.center_y:.6f})\n"
            f"Zoom: {self.zoom:.1f}x\n"
            f"X: [{x_min:.4f}, {x_max:.4f}]\n"
            f"Y: [{y_min:.4f}, {y_max:.4f}]"
        )
    
    def _canvas_to_complex(self, canvas_x: int, canvas_y: int) -> Tuple[float, float]:
        """Convert canvas coordinates to complex plane coordinates."""
        x_min, x_max, y_min, y_max = get_bounds(self.center_x, self.center_y, self.zoom)
        
        real = x_min + (canvas_x / self.width) * (x_max - x_min)
        # Y is flipped (canvas 0 is top, complex plane 0 is bottom)
        imag = y_max - (canvas_y / self.height) * (y_max - y_min)
        
        return real, imag
    
    def _on_left_click(self, event):
        """Handle left click - start drag or zoom in."""
        self.drag_start = (event.x, event.y)
        self.drag_start_center = (self.center_x, self.center_y)
    
    def _on_drag(self, event):
        """Handle drag - pan the view."""
        if self.drag_start is None:
            return
        
        # Calculate drag distance in complex plane coordinates
        dx_pixels = event.x - self.drag_start[0]
        dy_pixels = event.y - self.drag_start[1]
        
        x_min, x_max, y_min, y_max = get_bounds(
            self.drag_start_center[0],
            self.drag_start_center[1],
            self.zoom
        )
        
        # Convert pixel distance to complex plane distance
        dx_complex = -dx_pixels / self.width * (x_max - x_min)
        dy_complex = dy_pixels / self.height * (y_max - y_min)
        
        self.center_x = self.drag_start_center[0] + dx_complex
        self.center_y = self.drag_start_center[1] + dy_complex
        
        self._update_coord_display()
    
    def _on_drag_end(self, event):
        """Handle drag end - render if we moved considerably."""
        if self.drag_start is None:
            return
        
        dx = abs(event.x - self.drag_start[0])
        dy = abs(event.y - self.drag_start[1])
        
        if dx > 5 or dy > 5:
            # Considerable drag - render new view
            self.render()
        else:
            # Click - zoom in
            real, imag = self._canvas_to_complex(event.x, event.y)
            self.center_x = real
            self.center_y = imag
            self.zoom *= 2
            self._update_coord_display()
            self.render()
        
        self.drag_start = None
        self.drag_start_center = None
    
    def _on_right_click(self, event):
        """Handle right click - zoom out."""
        real, imag = self._canvas_to_complex(event.x, event.y)
        self.center_x = real
        self.center_y = imag
        self.zoom = max(0.1, self.zoom / 2)
        self._update_coord_display()
        self.render()
    
    def _on_scroll(self, event):
        """Handle mouse wheel scroll - zoom."""
        if event.delta > 0:
            self.zoom *= 1.2
        else:
            self.zoom = max(0.1, self.zoom / 1.2)
        self._update_coord_display()
        self.render()
    
    def _on_scroll_linux(self, event, direction):
        """Handle Linux scroll events."""
        if direction > 0:
            self.zoom *= 1.2
        else:
            self.zoom = max(0.1, self.zoom / 1.2)
        self._update_coord_display()
        self.render()
    
    def _on_preset_selected(self, event):
        """Handle preset location selection."""
        preset_name = self.preset_var.get()
        self.center_x, self.center_y, self.zoom = get_preset_location(preset_name)
        self._update_coord_display()
        self.render()
    
    def render(self):
        """Render the current view."""
        if self.computing:
            return
        
        self.computing = True
        self.status_var.set("Computing...")
        self.update()
        
        # Run computation in thread to keep GUI responsive
        thread = threading.Thread(target=self._render_thread)
        thread.start()
    
    def _render_thread(self):
        """Render in background thread."""
        try:
            self.max_iter = self.iter_var.get()
            self.colormap = self.cmap_var.get()
            self.smooth = self.smooth_var.get()
            
            x_min, x_max, y_min, y_max = get_bounds(
                self.center_x, self.center_y, self.zoom
            )
            
            data = compute_mandelbrot(
                self.width, self.height, self.max_iter,
                x_min, x_max, y_min, y_max,
                smooth=self.smooth,
                method=ComputeMethod.NUMPY
            )
            
            self.current_data = data
            
            # Convert to image
            self.after(0, lambda: self._display_data(data))
            
        except Exception as e:
            logger.error(f"Render error: {e}")
            self.after(0, lambda: self.status_var.set(f"Error: {e}"))
        finally:
            self.computing = False
    
    def _display_data(self, data: np.ndarray):
        """Display computed data on canvas."""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.cm as cm
            
            # Normalize data
            norm_data = data.astype(float)
            if norm_data.max() > norm_data.min():
                norm_data = (norm_data - norm_data.min()) / (norm_data.max() - norm_data.min())
            
            # Apply colormap
            cmap = plt.get_cmap(self.colormap)
            colored = cmap(norm_data)
            
            # Convert to 8-bit RGB
            rgb = (colored[:, :, :3] * 255).astype(np.uint8)
            
            # Flip vertically for correct orientation
            rgb = np.flipud(rgb)
            
            # Create PIL image
            pil_image = Image.fromarray(rgb)
            
            # Convert to Tkinter-compatible image
            self.photo_image = ImageTk.PhotoImage(pil_image)
            
            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
            
            self.status_var.set("Ready")
            self._update_coord_display()
            
        except Exception as e:
            logger.error(f"Display error: {e}")
            self.status_var.set(f"Display error: {e}")
    
    def reset_view(self):
        """Reset to default view."""
        self.center_x = -0.5
        self.center_y = 0.0
        self.zoom = 1.0
        self._update_coord_display()
        self.render()
    
    def save_image(self):
        """Save current view to file."""
        if self.current_data is None:
            messagebox.showwarning("Warning", "No image to save. Render first.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            try:
                import matplotlib.pyplot as plt
                import matplotlib.cm as cm
                
                # High-resolution render
                self.status_var.set("Rendering high-res...")
                self.update()
                
                hi_res_width = 1920
                hi_res_height = 1920
                
                x_min, x_max, y_min, y_max = get_bounds(
                    self.center_x, self.center_y, self.zoom
                )
                
                data = compute_mandelbrot(
                    hi_res_width, hi_res_height, self.max_iter,
                    x_min, x_max, y_min, y_max,
                    smooth=self.smooth,
                    method=ComputeMethod.NUMPY
                )
                
                # Apply colormap
                norm_data = data.astype(float)
                if norm_data.max() > norm_data.min():
                    norm_data = (norm_data - norm_data.min()) / (norm_data.max() - norm_data.min())
                
                cmap = plt.get_cmap(self.colormap)
                colored = cmap(norm_data)
                rgb = (colored[:, :, :3] * 255).astype(np.uint8)
                rgb = np.flipud(rgb)
                
                # Save
                pil_image = Image.fromarray(rgb)
                pil_image.save(filename)
                
                self.status_var.set(f"Saved: {filename}")
                messagebox.showinfo("Success", f"Image saved to:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")
                self.status_var.set("Save failed")


def main():
    """Launch the GUI application."""
    logging.basicConfig(level=logging.INFO)
    
    # Check for required packages
    try:
        from PIL import Image, ImageTk
    except ImportError:
        print("Error: PIL/Pillow is required for the GUI.")
        print("Install with: pip install Pillow")
        return 1
    
    app = MandelbrotExplorer()
    app.mainloop()
    return 0


if __name__ == "__main__":
    exit(main())
