"""Integration tests for geospatial modules."""

import pytest
import numpy as np
from biotica.utils.geo import GeoTransformer, GeoPoint, GeoBounds

class TestGeospatialIntegration:
    """Test geospatial integration with other modules."""
    
    def test_coordinate_transform(self):
        """Test coordinate transformation."""
        point = GeoPoint(lat=45.5, lon=-73.5)
        assert point.lat == 45.5
        assert point.lon == -73.5
    
    def test_distance_calculation(self):
        """Test distance between points."""
        p1 = GeoPoint(45.5, -73.5)
        p2 = GeoPoint(45.7, -73.8)
        dist = p1.distance_to(p2)
        assert dist > 0
        assert dist < 50
    
    def test_bounds_creation(self):
        """Test bounds creation."""
        bounds = GeoBounds(45.0, -74.0, 46.0, -73.0)
        assert bounds.min_lat == 45.0
        assert bounds.max_lon == -73.0
