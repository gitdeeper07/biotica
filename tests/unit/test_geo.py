"""Unit tests for geospatial utilities."""

import pytest
import numpy as np
from biotica.utils.geo import GeoPoint, GeoBounds

class TestGeoPoint:
    """Test GeoPoint class."""
    
    def test_create_point(self):
        """Test point creation."""
        p = GeoPoint(45.5, -73.5)
        assert p.lat == 45.5
        assert p.lon == -73.5
        assert p.crs == 'EPSG:4326'
    
    def test_point_with_elevation(self):
        """Test point with elevation."""
        p = GeoPoint(45.5, -73.5, elevation=100)
        assert p.elevation == 100
    
    def test_distance(self):
        """Test distance calculation."""
        p1 = GeoPoint(45.5, -73.5)
        p2 = GeoPoint(45.7, -73.8)
        d = p1.distance_to(p2)
        assert d > 0
        assert d < 50  # Should be ~35 km
    
    def test_distance_same_point(self):
        """Test distance to same point."""
        p1 = GeoPoint(45.5, -73.5)
        p2 = GeoPoint(45.5, -73.5)
        d = p1.distance_to(p2)
        assert d == 0

class TestGeoBounds:
    """Test GeoBounds class."""
    
    def test_create_bounds(self):
        """Test bounds creation."""
        b = GeoBounds(45.0, -74.0, 46.0, -73.0)
        assert b.min_lat == 45.0
        assert b.min_lon == -74.0
        assert b.max_lat == 46.0
        assert b.max_lon == -73.0
    
    def test_properties(self):
        """Test bounds properties."""
        b = GeoBounds(45.0, -74.0, 46.0, -73.0)
        assert b.width == 1.0
        assert b.height == 1.0
        assert b.center == (45.5, -73.5)
    
    def test_contains(self):
        """Test contains point."""
        b = GeoBounds(45.0, -74.0, 46.0, -73.0)
        p1 = GeoPoint(45.5, -73.5)
        p2 = GeoPoint(47.0, -70.0)
        assert b.contains(p1) is True
        assert b.contains(p2) is False
