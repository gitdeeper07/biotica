"""Geospatial utilities for BIOTICA."""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
import warnings
import math

try:
    from shapely.geometry import Point, Polygon, box, shape
    from shapely.ops import transform
    import pyproj
    from pyproj import Transformer, CRS
    GEO_AVAILABLE = True
except ImportError:
    GEO_AVAILABLE = False
    warnings.warn("Shapely/pyproj not available. Geospatial features disabled.")

try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False

@dataclass
class GeoPoint:
    """Geographic point with coordinates."""
    lat: float
    lon: float
    elevation: Optional[float] = None
    crs: str = 'EPSG:4326'
    
    def to_shapely(self) -> Optional[Any]:
        """Convert to shapely Point."""
        if GEO_AVAILABLE:
            return Point(self.lon, self.lat)
        return None
    
    def distance_to(self, other: 'GeoPoint') -> float:
        """
        Calculate great-circle distance to another point (km).
        
        Uses haversine formula.
        """
        R = 6371.0  # Earth radius in km
        
        lat1 = math.radians(self.lat)
        lon1 = math.radians(self.lon)
        lat2 = math.radians(other.lat)
        lon2 = math.radians(other.lon)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c

@dataclass
class GeoBounds:
    """Geographic bounds."""
    min_lat: float
    min_lon: float
    max_lat: float
    max_lon: float
    crs: str = 'EPSG:4326'
    
    @property
    def width(self) -> float:
        """Width in degrees."""
        return self.max_lon - self.min_lon
    
    @property
    def height(self) -> float:
        """Height in degrees."""
        return self.max_lat - self.min_lat
    
    @property
    def center(self) -> Tuple[float, float]:
        """Center point (lat, lon)."""
        return (
            (self.min_lat + self.max_lat) / 2,
            (self.min_lon + self.max_lon) / 2
        )
    
    def to_shapely(self) -> Optional[Any]:
        """Convert to shapely Polygon."""
        if GEO_AVAILABLE:
            return box(self.min_lon, self.min_lat, self.max_lon, self.max_lat)
        return None
    
    def contains(self, point: GeoPoint) -> bool:
        """Check if bounds contain point."""
        return (self.min_lat <= point.lat <= self.max_lat and
                self.min_lon <= point.lon <= self.max_lon)

class GeoTransformer:
    """Geospatial coordinate transformations."""
    
    # Common coordinate systems
    CRS_WGS84 = 'EPSG:4326'
    CRS_UTM = 'EPSG:32633'  # UTM zone 33N
    CRS_MERCATOR = 'EPSG:3857'  # Web Mercator
    
    def __init__(self):
        """Initialize transformer."""
        if not GEO_AVAILABLE:
            warnings.warn("Geospatial libraries not available. Transformations disabled.")
    
    def transform_point(self, 
                       point: GeoPoint,
                       target_crs: str) -> GeoPoint:
        """
        Transform point to different CRS.
        
        Args:
            point: Source point
            target_crs: Target CRS
            
        Returns:
            Transformed point
        """
        if not GEO_AVAILABLE:
            return point
        
        transformer = Transformer.from_crs(point.crs, target_crs, always_xy=True)
        x, y = transformer.transform(point.lon, point.lat)
        
        return GeoPoint(
            lat=y if '4326' in target_crs else y,
            lon=x if '4326' in target_crs else x,
            elevation=point.elevation,
            crs=target_crs
        )
    
    def transform_bounds(self,
                        bounds: GeoBounds,
                        target_crs: str) -> GeoBounds:
        """Transform bounds to different CRS."""
        if not GEO_AVAILABLE:
            return bounds
        
        # Transform corners
        corners = [
            GeoPoint(bounds.min_lat, bounds.min_lon, crs=bounds.crs),
            GeoPoint(bounds.min_lat, bounds.max_lon, crs=bounds.crs),
            GeoPoint(bounds.max_lat, bounds.min_lon, crs=bounds.crs),
            GeoPoint(bounds.max_lat, bounds.max_lon, crs=bounds.crs)
        ]
        
        transformed = [self.transform_point(p, target_crs) for p in corners]
        
        lats = [p.lat for p in transformed]
        lons = [p.lon for p in transformed]
        
        return GeoBounds(
            min_lat=min(lats),
            min_lon=min(lons),
            max_lat=max(lats),
            max_lon=max(lons),
            crs=target_crs
        )
    
    def get_utm_zone(self, lon: float, lat: float) -> str:
        """Get UTM zone EPSG code for location."""
        zone = int((lon + 180) / 6) + 1
        
        if lat >= 0:
            return f'EPSG:326{zone:02d}'  # Northern hemisphere
        else:
            return f'EPSG:327{zone:02d}'  # Southern hemisphere
    
    def calculate_area(self, 
                      bounds: GeoBounds,
                      target_crs: Optional[str] = None) -> float:
        """
        Calculate area in square kilometers.
        
        Args:
            bounds: Geographic bounds
            target_crs: CRS for area calculation (UTM recommended)
            
        Returns:
            Area in km²
        """
        if not GEO_AVAILABLE:
            # Approximate using spherical geometry
            R = 6371.0  # Earth radius in km
            lat_center = math.radians((bounds.min_lat + bounds.max_lat) / 2)
            
            width = bounds.width * math.pi * R * math.cos(lat_center) / 180
            height = bounds.height * math.pi * R / 180
            
            return width * height
        
        # Use appropriate CRS for accurate area
        if target_crs is None:
            center_lat, center_lon = bounds.center
            target_crs = self.get_utm_zone(center_lon, center_lat)
        
        # Transform to equal-area projection
        transformed = self.transform_bounds(bounds, target_crs)
        
        # Calculate area
        area_sq_m = (transformed.width * 1000) * (transformed.height * 1000)
        area_sq_km = area_sq_m / 1_000_000
        
        return area_sq_km

class RasterGrid:
    """Raster grid for spatial data."""
    
    def __init__(self,
                 bounds: GeoBounds,
                 resolution: float,
                 crs: str = 'EPSG:4326'):
        """
        Initialize raster grid.
        
        Args:
            bounds: Geographic bounds
            resolution: Grid resolution in degrees or meters
            crs: Coordinate reference system
        """
        self.bounds = bounds
        self.resolution = resolution
        self.crs = crs
        
        # Calculate grid dimensions
        self.nx = int(np.ceil(bounds.width / resolution))
        self.ny = int(np.ceil(bounds.height / resolution))
        
        # Create coordinate arrays
        self.lons = np.linspace(bounds.min_lon, bounds.max_lon, self.nx)
        self.lats = np.linspace(bounds.min_lat, bounds.max_lat, self.ny)
        
        self.lon_grid, self.lat_grid = np.meshgrid(self.lons, self.lats)
    
    def get_cell_bounds(self, i: int, j: int) -> GeoBounds:
        """Get bounds of grid cell."""
        return GeoBounds(
            min_lat=self.lats[i],
            min_lon=self.lons[j],
            max_lat=self.lats[i+1] if i+1 < self.ny else self.lats[i] + self.resolution,
            max_lon=self.lons[j+1] if j+1 < self.nx else self.lons[j] + self.resolution,
            crs=self.crs
        )
    
    def get_cell_center(self, i: int, j: int) -> GeoPoint:
        """Get center point of grid cell."""
        return GeoPoint(
            lat=(self.lats[i] + self.lats[i+1]) / 2 if i+1 < self.ny else self.lats[i] + self.resolution/2,
            lon=(self.lons[j] + self.lons[j+1]) / 2 if j+1 < self.nx else self.lons[j] + self.resolution/2,
            crs=self.crs
        )
    
    def point_to_index(self, point: GeoPoint) -> Tuple[int, int]:
        """Convert point to grid indices."""
        i = int((point.lat - self.bounds.min_lat) / self.resolution)
        j = int((point.lon - self.bounds.min_lon) / self.resolution)
        
        i = np.clip(i, 0, self.ny - 1)
        j = np.clip(j, 0, self.nx - 1)
        
        return i, j
    
    def create_array(self) -> np.ndarray:
        """Create empty array for grid."""
        return np.zeros((self.ny, self.nx))

class SpatialInterpolator:
    """Spatial interpolation utilities."""
    
    @staticmethod
    def idw(points: List[Tuple[float, float, float]],
            grid_lons: np.ndarray,
            grid_lats: np.ndarray,
            power: float = 2.0) -> np.ndarray:
        """
        Inverse Distance Weighting interpolation.
        
        Args:
            points: List of (lon, lat, value) tuples
            grid_lons: Longitude grid
            grid_lats: Latitude grid
            power: Power parameter for IDW
            
        Returns:
            Interpolated grid
        """
        result = np.zeros_like(grid_lons)
        weights_sum = np.zeros_like(grid_lons)
        
        for lon, lat, val in points:
            # Calculate distances
            dx = grid_lons - lon
            dy = grid_lats - lat
            
            # Distance in degrees (convert to km for better scaling)
            R = 6371.0
            dx_km = dx * np.pi * R * np.cos(np.radians(lat)) / 180
            dy_km = dy * np.pi * R / 180
            dist = np.sqrt(dx_km**2 + dy_km**2)
            
            # Avoid division by zero
            dist = np.maximum(dist, 0.001)
            
            # Calculate weights
            weights = 1.0 / (dist ** power)
            
            result += val * weights
            weights_sum += weights
        
        # Normalize
        valid = weights_sum > 0
        result[valid] /= weights_sum[valid]
        
        return result
    
    @staticmethod
    def nearest_neighbor(points: List[Tuple[float, float, float]],
                        grid_lons: np.ndarray,
                        grid_lats: np.ndarray) -> np.ndarray:
        """Nearest neighbor interpolation."""
        result = np.zeros_like(grid_lons)
        
        for i in range(grid_lons.shape[0]):
            for j in range(grid_lons.shape[1]):
                lon = grid_lons[i, j]
                lat = grid_lats[i, j]
                
                # Find nearest point
                min_dist = float('inf')
                nearest_val = 0
                
                for plon, plat, pval in points:
                    R = 6371.0
                    dlat = np.radians(plat - lat)
                    dlon = np.radians(plon - lon)
                    
                    a = (np.sin(dlat/2)**2 + 
                         np.cos(np.radians(lat)) * np.cos(np.radians(plat)) * 
                         np.sin(dlon/2)**2)
                    c = 2 * np.arcsin(np.sqrt(a))
                    dist = R * c
                    
                    if dist < min_dist:
                        min_dist = dist
                        nearest_val = pval
                
                result[i, j] = nearest_val
        
        return result

class ZonalStats:
    """Zonal statistics for spatial data."""
    
    def __init__(self, zones: Optional[Any] = None):
        """
        Initialize zonal statistics.
        
        Args:
            zones: GeoDataFrame or shapely polygons
        """
        self.zones = zones
    
    def extract(self,
               raster_data: np.ndarray,
               raster_bounds: GeoBounds,
               zone_geometry: Any) -> Dict[str, float]:
        """
        Extract zonal statistics for a single zone.
        
        Args:
            raster_data: 2D raster array
            raster_bounds: Raster bounds
            zone_geometry: Shapely polygon
            
        Returns:
            Dictionary of statistics
        """
        if not GEO_AVAILABLE:
            return {}
        
        # Create raster grid
        ny, nx = raster_data.shape
        grid = RasterGrid(raster_bounds, 
                         (raster_bounds.width / nx),
                         raster_bounds.crs)
        
        # Collect values within zone
        values = []
        
        for i in range(ny):
            for j in range(nx):
                cell_center = grid.get_cell_center(i, j)
                point = cell_center.to_shapely()
                
                if point and zone_geometry.contains(point):
                    values.append(raster_data[i, j])
        
        if not values:
            return {}
        
        return {
            'count': len(values),
            'mean': float(np.mean(values)),
            'std': float(np.std(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'median': float(np.median(values)),
            'sum': float(np.sum(values))
        }
    
    def extract_all(self,
                   raster_data: np.ndarray,
                   raster_bounds: GeoBounds) -> List[Dict[str, Any]]:
        """Extract statistics for all zones."""
        results = []
        
        if GEOPANDAS_AVAILABLE and hasattr(self.zones, 'iterrows'):
            for idx, row in self.zones.iterrows():
                stats = self.extract(raster_data, raster_bounds, row.geometry)
                stats['zone_id'] = idx
                results.append(stats)
        
        return results

# Example usage
if __name__ == "__main__":
    # Create point
    point = GeoPoint(45.5, -73.5, elevation=100)
    print(f"Point: ({point.lat}, {point.lon})")
    
    # Create bounds
    bounds = GeoBounds(45.0, -74.0, 46.0, -73.0)
    print(f"Bounds: {bounds}")
    print(f"Center: {bounds.center}")
    print(f"Area: {bounds.width * bounds.height:.2f} deg²")
    
    # Calculate distance
    point2 = GeoPoint(45.7, -73.8)
    dist = point.distance_to(point2)
    print(f"Distance: {dist:.2f} km")
    
    # Initialize transformer
    transformer = GeoTransformer()
    
    # Transform to UTM
    utm_point = transformer.transform_point(point, 'EPSG:32618')
    print(f"UTM coordinates: ({utm_point.lat:.0f}, {utm_point.lon:.0f})")
    
    # Create raster grid
    grid = RasterGrid(bounds, resolution=0.01)
    print(f"Grid dimensions: {grid.nx} x {grid.ny}")
    
    # Get UTM zone
    zone = transformer.get_utm_zone(point.lon, point.lat)
    print(f"UTM zone: {zone}")
    
    # Calculate area in km²
    area = transformer.calculate_area(bounds, target_crs=zone)
    print(f"Area: {area:.2f} km²")
    
    # Create sample data for interpolation
    points = [
        (-73.5, 45.2, 100),
        (-73.8, 45.5, 150),
        (-73.2, 45.7, 80),
        (-73.6, 45.3, 120)
    ]
    
    # Interpolate
    grid_lons, grid_lats = np.meshgrid(grid.lons, grid.lats)
    
    interpolated = SpatialInterpolator.idw(points, grid_lons, grid_lats)
    print(f"Interpolated grid shape: {interpolated.shape}")
    print(f"Value range: [{interpolated.min():.1f}, {interpolated.max():.1f}]")
