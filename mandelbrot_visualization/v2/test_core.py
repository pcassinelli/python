"""
test_core.py - Unit Tests for Mandelbrot Core Module

Run with: pytest tests/test_core.py -v
Or: python -m pytest tests/ -v
"""

import pytest
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import (
    escape_time,
    escape_time_smooth,
    validate_parameters,
    compute_mandelbrot,
    compute_mandelbrot_python,
    compute_mandelbrot_numpy,
    get_bounds,
    get_preset_location,
    list_presets,
    ComputeMethod
)


class TestEscapeTime:
    """Tests for the escape_time function."""
    
    def test_origin_in_set(self):
        """Origin (0,0) should be in the Mandelbrot set."""
        result = escape_time(complex(0, 0), 100)
        assert result == 100, "Origin should reach max iterations"
    
    def test_far_point_escapes(self):
        """Points far from origin should escape quickly."""
        result = escape_time(complex(10, 10), 100)
        assert result < 10, "Far point should escape very quickly"
    
    def test_minus_one_in_set(self):
        """Point -1 is in the Mandelbrot set (period-2 cycle)."""
        result = escape_time(complex(-1, 0), 100)
        assert result == 100, "-1 should be in the set"
    
    def test_point_two_escapes(self):
        """Point 2 should escape quickly."""
        result = escape_time(complex(2, 0), 100)
        assert result <= 2, "Point 2 should escape very quickly"
    
    def test_boundary_point(self):
        """Test a point clearly outside the set."""
        # Using a point that definitely escapes
        result = escape_time(complex(0.5, 0.5), 100)
        assert result < 100, "Point (0.5, 0.5) should escape"


class TestEscapeTimeSmooth:
    """Tests for the smooth escape time function."""
    
    def test_returns_float(self):
        """Smooth function should return float."""
        result = escape_time_smooth(complex(0.5, 0.5), 100)
        assert isinstance(result, float), "Should return float"
    
    def test_origin_returns_max_iter(self):
        """Origin should return max_iter."""
        result = escape_time_smooth(complex(0, 0), 100)
        assert result == 100, "Origin should return max iterations"
    
    def test_smooth_values_positive(self):
        """Smooth values should be non-negative."""
        for _ in range(20):
            x = np.random.uniform(-2, 2)
            y = np.random.uniform(-2, 2)
            result = escape_time_smooth(complex(x, y), 50)
            assert result >= 0, "Smooth value should be non-negative"


class TestValidateParameters:
    """Tests for parameter validation."""
    
    def test_valid_parameters(self):
        """Valid parameters should not raise."""
        validate_parameters(100, 100, 50, -2.0, 1.0, -1.5, 1.5)
    
    def test_negative_width(self):
        """Negative width should raise ValueError."""
        with pytest.raises(ValueError):
            validate_parameters(-100, 100, 50, -2.0, 1.0, -1.5, 1.5)
    
    def test_zero_height(self):
        """Zero height should raise ValueError."""
        with pytest.raises(ValueError):
            validate_parameters(100, 0, 50, -2.0, 1.0, -1.5, 1.5)
    
    def test_negative_max_iter(self):
        """Negative max_iter should raise ValueError."""
        with pytest.raises(ValueError):
            validate_parameters(100, 100, -50, -2.0, 1.0, -1.5, 1.5)
    
    def test_invalid_x_bounds(self):
        """x_min >= x_max should raise ValueError."""
        with pytest.raises(ValueError):
            validate_parameters(100, 100, 50, 1.0, -2.0, -1.5, 1.5)
    
    def test_invalid_y_bounds(self):
        """y_min >= y_max should raise ValueError."""
        with pytest.raises(ValueError):
            validate_parameters(100, 100, 50, -2.0, 1.0, 1.5, -1.5)
    
    def test_too_large_dimensions(self):
        """Dimensions > 10000 should raise ValueError."""
        with pytest.raises(ValueError):
            validate_parameters(20000, 100, 50, -2.0, 1.0, -1.5, 1.5)


class TestComputeMandelbrot:
    """Tests for Mandelbrot computation functions."""
    
    def test_output_shape(self):
        """Output should have correct shape."""
        data = compute_mandelbrot(100, 80, 50)
        assert data.shape == (80, 100), "Shape should be (height, width)"
    
    def test_output_dtype_integer(self):
        """Non-smooth output should be integer."""
        data = compute_mandelbrot(50, 50, 30, smooth=False)
        assert np.issubdtype(data.dtype, np.integer), "Should be integer type"
    
    def test_output_dtype_float_smooth(self):
        """Smooth output should be float."""
        data = compute_mandelbrot(50, 50, 30, smooth=True)
        assert np.issubdtype(data.dtype, np.floating), "Smooth should be float"
    
    def test_values_in_range(self):
        """Values should be between 0 and max_iter."""
        max_iter = 50
        data = compute_mandelbrot(100, 100, max_iter)
        assert data.min() >= 0, "Min should be >= 0"
        assert data.max() <= max_iter, "Max should be <= max_iter"
    
    def test_python_numpy_similar(self):
        """Python and NumPy methods should produce similar results."""
        params = dict(
            width=50, height=50, max_iter=30,
            x_min=-2.0, x_max=1.0, y_min=-1.5, y_max=1.5
        )
        
        python_result = compute_mandelbrot_python(**params)
        numpy_result = compute_mandelbrot_numpy(**params)
        
        diff = np.abs(python_result.astype(float) - numpy_result.astype(float))
        assert diff.max() <= 1, "Python and NumPy results should be similar"
    
    def test_method_selection(self):
        """Method parameter should select correct algorithm."""
        compute_mandelbrot(30, 30, 20, method=ComputeMethod.PYTHON)
        compute_mandelbrot(30, 30, 20, method=ComputeMethod.NUMPY)
    
    def test_progress_callback(self):
        """Progress callback should be called."""
        progress_calls = []
        
        def callback(current, total):
            progress_calls.append((current, total))
        
        compute_mandelbrot_python(30, 30, 20, progress_callback=callback)
        
        assert len(progress_calls) == 30, "Should call callback for each row"
        assert progress_calls[-1] == (30, 30), "Last call should be complete"


class TestGetBounds:
    """Tests for coordinate bounds calculation."""
    
    def test_default_bounds(self):
        """Default bounds should be standard Mandelbrot view."""
        x_min, x_max, y_min, y_max = get_bounds(-0.5, 0.0, 1.0)
        assert x_min == -2.0
        assert x_max == 1.0
        assert y_min == -1.5
        assert y_max == 1.5
    
    def test_zoom_reduces_range(self):
        """Higher zoom should reduce coordinate range."""
        bounds_1x = get_bounds(-0.5, 0.0, 1.0)
        bounds_2x = get_bounds(-0.5, 0.0, 2.0)
        
        range_1x = bounds_1x[1] - bounds_1x[0]
        range_2x = bounds_2x[1] - bounds_2x[0]
        
        assert range_2x < range_1x, "2x zoom should have smaller range"
    
    def test_center_changes_bounds(self):
        """Different center should shift bounds."""
        bounds_default = get_bounds(-0.5, 0.0, 1.0)
        bounds_shifted = get_bounds(0.0, 0.5, 1.0)
        
        assert bounds_shifted[0] != bounds_default[0]
    
    def test_negative_zoom_raises(self):
        """Negative zoom should raise ValueError."""
        with pytest.raises(ValueError):
            get_bounds(0, 0, -1.0)
    
    def test_zero_zoom_raises(self):
        """Zero zoom should raise ValueError."""
        with pytest.raises(ValueError):
            get_bounds(0, 0, 0.0)


class TestPresets:
    """Tests for preset locations."""
    
    def test_list_presets_not_empty(self):
        """Should have some presets defined."""
        presets = list_presets()
        assert len(presets) > 0
    
    def test_default_preset_exists(self):
        """Default preset should exist."""
        assert "default" in list_presets()
    
    def test_get_preset_returns_tuple(self):
        """get_preset_location should return 3-tuple."""
        result = get_preset_location("default")
        assert len(result) == 3
    
    def test_unknown_preset_raises(self):
        """Unknown preset should raise KeyError."""
        with pytest.raises(KeyError):
            get_preset_location("nonexistent_preset")
    
    def test_all_presets_valid(self):
        """All presets should be retrievable."""
        for name in list_presets():
            cx, cy, zoom = get_preset_location(name)
            assert isinstance(cx, (int, float))
            assert isinstance(cy, (int, float))
            assert zoom > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
