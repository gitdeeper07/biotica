"""Unit tests for remote sensing module."""

import pytest
import numpy as np
from biotica.remote_sensing.sentinel import Sentinel2Interface

class TestSentinelInterface:
    """Test Sentinel interface."""
    
    def test_initialization(self):
        """Test initialization."""
        sentinel = Sentinel2Interface()
        assert sentinel is not None
        assert hasattr(sentinel, 'BANDS')
        assert len(sentinel.BANDS) > 0
        assert 'B04' in sentinel.BANDS
        assert 'B08' in sentinel.BANDS
    
    def test_bands_info(self):
        """Test bands information."""
        sentinel = Sentinel2Interface()
        assert sentinel.BANDS['B04']['wavelength'] == 665
        assert sentinel.BANDS['B08']['resolution'] == 10
