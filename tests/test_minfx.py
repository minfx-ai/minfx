import pytest
import minfx

def test_import():
    """Test that the package can be imported."""
    assert minfx is not None


def test_version():
    """Test that version is defined."""
    assert hasattr(minfx, "__version__")
    assert isinstance(minfx.__version__, str)
