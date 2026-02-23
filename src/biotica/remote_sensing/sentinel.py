"""Sentinel-2 satellite data interface."""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
import warnings
import json
from datetime import datetime, timedelta
import os
from pathlib import Path

try:
    import rasterio
    from rasterio.transform import from_origin
    from rasterio.warp import reproject, Resampling
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False
    warnings.warn("rasterio not available. Sentinel-2 processing disabled.")

try:
    import geopandas as gpd
    from shapely.geometry import box, Point, Polygon
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False
    warnings.warn("geopandas not available. Spatial operations disabled.")

@dataclass
class SentinelBand:
    """Sentinel-2 band data."""
    name: str
    wavelength: float
    resolution: int
    data: np.ndarray
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate after initialization."""
        if self.data is not None and len(self.data.shape) != 2:
            raise ValueError(f"Band data must be 2D, got shape {self.data.shape}")

@dataclass
class SentinelScene:
    """Complete Sentinel-2 scene."""
    scene_id: str
    acquisition_time: datetime
    bands: Dict[str, SentinelBand]
    bounds: Tuple[float, float, float, float]  # (minx, miny, maxx, maxy)
    crs: str
    cloud_cover: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_band(self, band_name: str) -> Optional[SentinelBand]:
        """Get band by name."""
        return self.bands.get(band_name)
    
    def calculate_index(self, 
                       index_name: str,
                       band1: str,
                       band2: str,
                       band3: Optional[str] = None) -> np.ndarray:
        """
        Calculate vegetation index.
        
        Args:
            index_name: Name of index
            band1: First band name
            band2: Second band name
            band3: Third band name (optional)
            
        Returns:
            Index array
        """
        b1 = self.bands[band1].data.astype(float)
        b2 = self.bands[band2].data.astype(float)
        
        # Normalized Difference Index
        if index_name in ['NDVI', 'NDWI', 'NDBI']:
            result = (b1 - b2) / (b1 + b2 + 1e-10)
            
        # Enhanced Vegetation Index
        elif index_name == 'EVI' and band3:
            b3 = self.bands[band3].data.astype(float)
            result = 2.5 * (b1 - b2) / (b1 + 6*b2 - 7.5*b3 + 1)
            
        # Soil Adjusted Vegetation Index
        elif index_name == 'SAVI':
            L = 0.5  # Soil adjustment factor
            result = (b1 - b2) / (b1 + b2 + L) * (1 + L)
            
        else:
            raise ValueError(f"Unknown index: {index_name}")
        
        return np.clip(result, -1, 1)
    
    def resample(self, target_resolution: int = 10) -> 'SentinelScene':
        """Resample all bands to target resolution."""
        if not RASTERIO_AVAILABLE:
            raise ImportError("rasterio required for resampling")
        
        # Find reference band at target resolution
        target_bands = {}
        reference_band = None
        
        for name, band in self.bands.items():
            if band.resolution == target_resolution:
                reference_band = band
                break
        
        if reference_band is None:
            # Use highest resolution band as reference
            min_res = min(b.resolution for b in self.bands.values())
            reference_band = next(b for b in self.bands.values() if b.resolution == min_res)
        
        ref_shape = reference_band.data.shape
        ref_transform = from_origin(self.bounds[0], self.bounds[3], 
                                   target_resolution, target_resolution)
        
        for name, band in self.bands.items():
            if band.resolution == target_resolution:
                target_bands[name] = band
            else:
                # Reproject to target resolution
                dest = np.zeros(ref_shape, dtype=np.float32)
                
                src_transform = from_origin(self.bounds[0], self.bounds[3],
                                           band.resolution, band.resolution)
                
                reproject(
                    source=band.data,
                    destination=dest,
                    src_transform=src_transform,
                    src_crs=self.crs,
                    dst_transform=ref_transform,
                    dst_crs=self.crs,
                    resampling=Resampling.bilinear
                )
                
                target_bands[name] = SentinelBand(
                    name=band.name,
                    wavelength=band.wavelength,
                    resolution=target_resolution,
                    data=dest,
                    metadata=band.metadata
                )
        
        return SentinelScene(
            scene_id=self.scene_id,
            acquisition_time=self.acquisition_time,
            bands=target_bands,
            bounds=self.bounds,
            crs=self.crs,
            cloud_cover=self.cloud_cover,
            metadata=self.metadata
        )
    
    def clip(self, bounds: Tuple[float, float, float, float]) -> 'SentinelScene':
        """Clip scene to bounds."""
        if not RASTERIO_AVAILABLE:
            raise ImportError("rasterio required for clipping")
        
        from rasterio.mask import mask
        
        # Create geometry
        bbox = box(*bounds)
        geoms = [bbox.__geo_interface__]
        
        clipped_bands = {}
        
        for name, band in self.bands.items():
            with rasterio.open(
                f'temp_{name}.tif', 'w',
                driver='GTiff',
                height=band.data.shape[0],
                width=band.data.shape[1],
                count=1,
                dtype=band.data.dtype,
                crs=self.crs,
                transform=from_origin(self.bounds[0], self.bounds[3],
                                     band.resolution, band.resolution)
            ) as src:
                src.write(band.data, 1)
                
                out_image, out_transform = mask(src, geoms, crop=True)
                
            clipped_bands[name] = SentinelBand(
                name=band.name,
                wavelength=band.wavelength,
                resolution=band.resolution,
                data=out_image[0],
                metadata=band.metadata
            )
        
        return SentinelScene(
            scene_id=f"{self.scene_id}_clipped",
            acquisition_time=self.acquisition_time,
            bands=clipped_bands,
            bounds=bounds,
            crs=self.crs,
            cloud_cover=self.cloud_cover,
            metadata=self.metadata
        )

class Sentinel2Interface:
    """
    Interface for Sentinel-2 satellite data.
    
    Provides methods for:
    - Downloading scenes
    - Preprocessing
    - Vegetation indices calculation
    - Time series analysis
    """
    
    # Sentinel-2 band information
    BANDS = {
        'B01': {'wavelength': 443, 'resolution': 60},   # Coastal aerosol
        'B02': {'wavelength': 490, 'resolution': 10},   # Blue
        'B03': {'wavelength': 560, 'resolution': 10},   # Green
        'B04': {'wavelength': 665, 'resolution': 10},   # Red
        'B05': {'wavelength': 705, 'resolution': 20},   # Red Edge 1
        'B06': {'wavelength': 740, 'resolution': 20},   # Red Edge 2
        'B07': {'wavelength': 783, 'resolution': 20},   # Red Edge 3
        'B08': {'wavelength': 842, 'resolution': 10},   # NIR
        'B8A': {'wavelength': 865, 'resolution': 20},   # Red Edge 4
        'B09': {'wavelength': 940, 'resolution': 60},   # Water vapor
        'B10': {'wavelength': 1375, 'resolution': 60},  # Cirrus
        'B11': {'wavelength': 1610, 'resolution': 20},  # SWIR 1
        'B12': {'wavelength': 2190, 'resolution': 20},  # SWIR 2
    }
    
    # Vegetation indices formulas
    INDICES = {
        'NDVI': {'bands': ['B08', 'B04'], 'formula': 'nd'},
        'EVI': {'bands': ['B08', 'B04', 'B02'], 'formula': 'evi'},
        'NDWI': {'bands': ['B03', 'B08'], 'formula': 'nd'},
        'NDBI': {'bands': ['B11', 'B08'], 'formula': 'nd'},
        'SAVI': {'bands': ['B08', 'B04'], 'formula': 'savi'},
        'MSAVI': {'bands': ['B08', 'B04'], 'formula': 'msavi'},
        'NDRE': {'bands': ['B08', 'B05'], 'formula': 'nd'},
        'CIG': {'bands': ['B08', 'B03'], 'formula': 'ci'},
        'CIRE': {'bands': ['B08', 'B05'], 'formula': 'ci'},
    }
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize Sentinel-2 interface.
        
        Args:
            data_dir: Directory for storing downloaded data
        """
        self.data_dir = Path(data_dir) if data_dir else Path.home() / 'sentinel_data'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.scenes = {}
    
    def load_scene(self, 
                  scene_id: str,
                  band_files: Dict[str, str],
                  acquisition_time: datetime,
                  bounds: Tuple[float, float, float, float],
                  crs: str = 'EPSG:32633',
                  cloud_cover: float = 0.0) -> SentinelScene:
        """
        Load Sentinel-2 scene from files.
        
        Args:
            scene_id: Scene identifier
            band_files: Dictionary mapping band names to file paths
            acquisition_time: Acquisition datetime
            bounds: Scene bounds (minx, miny, maxx, maxy)
            crs: Coordinate reference system
            cloud_cover: Cloud cover percentage
            
        Returns:
            SentinelScene object
        """
        if not RASTERIO_AVAILABLE:
            raise ImportError("rasterio required for loading scenes")
        
        bands = {}
        
        for band_name, filepath in band_files.items():
            if band_name not in self.BANDS:
                warnings.warn(f"Unknown band: {band_name}")
                continue
            
            with rasterio.open(filepath) as src:
                data = src.read(1)
                
                bands[band_name] = SentinelBand(
                    name=band_name,
                    wavelength=self.BANDS[band_name]['wavelength'],
                    resolution=self.BANDS[band_name]['resolution'],
                    data=data,
                    metadata={
                        'file': filepath,
                        'shape': data.shape,
                        'dtype': str(data.dtype),
                        'nodata': src.nodata
                    }
                )
        
        scene = SentinelScene(
            scene_id=scene_id,
            acquisition_time=acquisition_time,
            bands=bands,
            bounds=bounds,
            crs=crs,
            cloud_cover=cloud_cover,
            metadata={'band_files': band_files}
        )
        
        self.scenes[scene_id] = scene
        return scene
    
    def create_composite(self, 
                        scene_ids: List[str],
                        method: str = 'median') -> SentinelScene:
        """
        Create composite from multiple scenes.
        
        Args:
            scene_ids: List of scene IDs
            method: Composite method ('median', 'mean', 'max', 'min')
            
        Returns:
            Composite scene
        """
        scenes = [self.scenes[sid] for sid in scene_ids if sid in self.scenes]
        
        if not scenes:
            raise ValueError("No valid scenes found")
        
        # Use first scene as reference
        ref_scene = scenes[0]
        
        # Stack data for each band
        composite_bands = {}
        
        for band_name in ref_scene.bands:
            band_data = []
            
            for scene in scenes:
                if band_name in scene.bands:
                    band_data.append(scene.bands[band_name].data)
            
            if band_data:
                stack = np.stack(band_data)
                
                if method == 'median':
                    composite = np.median(stack, axis=0)
                elif method == 'mean':
                    composite = np.mean(stack, axis=0)
                elif method == 'max':
                    composite = np.max(stack, axis=0)
                elif method == 'min':
                    composite = np.min(stack, axis=0)
                else:
                    raise ValueError(f"Unknown method: {method}")
                
                composite_bands[band_name] = SentinelBand(
                    name=band_name,
                    wavelength=ref_scene.bands[band_name].wavelength,
                    resolution=ref_scene.bands[band_name].resolution,
                    data=composite,
                    metadata={'method': method, 'n_scenes': len(band_data)}
                )
        
        return SentinelScene(
            scene_id=f"composite_{method}_{len(scene_ids)}scenes",
            acquisition_time=datetime.now(),
            bands=composite_bands,
            bounds=ref_scene.bounds,
            crs=ref_scene.crs,
            cloud_cover=np.mean([s.cloud_cover for s in scenes]),
            metadata={'source_scenes': scene_ids, 'method': method}
        )
    
    def extract_timeseries(self,
                          scene_ids: List[str],
                          geometry: Union[Point, Polygon],
                          band_name: str = 'NDVI') -> Dict[str, Any]:
        """
        Extract timeseries for a specific location.
        
        Args:
            scene_ids: List of scene IDs (sorted by time)
            geometry: Point or polygon for extraction
            band_name: Band or index name
            
        Returns:
            Timeseries data
        """
        if not GEOPANDAS_AVAILABLE:
            raise ImportError("geopandas required for timeseries extraction")
        
        times = []
        values = []
        
        for scene_id in scene_ids:
            if scene_id not in self.scenes:
                continue
            
            scene = self.scenes[scene_id]
            
            # Calculate index if needed
            if band_name in self.INDICES:
                info = self.INDICES[band_name]
                bands = info['bands']
                
                if len(bands) == 2:
                    b1 = scene.bands[bands[0]].data
                    b2 = scene.bands[bands[1]].data
                    
                    if info['formula'] == 'nd':
                        value = (b1 - b2) / (b1 + b2 + 1e-10)
                    elif info['formula'] == 'savi':
                        L = 0.5
                        value = (b1 - b2) / (b1 + b2 + L) * (1 + L)
                    else:
                        continue
                else:
                    continue
            else:
                # Use raw band
                value = scene.bands[band_name].data
            
            # Extract value at geometry
            if isinstance(geometry, Point):
                # Point extraction
                # Convert geometry to pixel coordinates
                # This is simplified - needs proper geotransform
                row = int((geometry.y - scene.bounds[1]) / 10)
                col = int((geometry.x - scene.bounds[0]) / 10)
                
                if 0 <= row < value.shape[0] and 0 <= col < value.shape[1]:
                    val = value[row, col]
                    if not np.isnan(val):
                        times.append(scene.acquisition_time)
                        values.append(val)
            
            elif isinstance(geometry, Polygon):
                # Polygon extraction - use zonal statistics
                # This is simplified
                val = np.nanmean(value)
                if not np.isnan(val):
                    times.append(scene.acquisition_time)
                    values.append(val)
        
        return {
            'times': times,
            'values': values,
            'band': band_name,
            'n_scenes': len(values)
        }
    
    def cloud_mask(self, scene: SentinelScene, threshold: float = 0.2) -> np.ndarray:
        """
        Create cloud mask for scene.
        
        Args:
            scene: Sentinel scene
            threshold: Cloud probability threshold
            
        Returns:
            Boolean mask (True = cloud)
        """
        # Use B10 (cirrus) for cloud detection
        if 'B10' in scene.bands:
            cirrus = scene.bands['B10'].data
            mask = cirrus > threshold
        else:
            # Fallback: use blue band brightness
            if 'B02' in scene.bands:
                blue = scene.bands['B02'].data
                mask = blue > 0.2
            else:
                mask = np.zeros_like(next(iter(scene.bands.values())).data, dtype=bool)
        
        return mask
    
    def save_scene(self, scene: SentinelScene, output_dir: Optional[str] = None):
        """Save scene to files."""
        if not RASTERIO_AVAILABLE:
            raise ImportError("rasterio required for saving scenes")
        
        out_dir = Path(output_dir) if output_dir else self.data_dir / scene.scene_id
        out_dir.mkdir(parents=True, exist_ok=True)
        
        for band_name, band in scene.bands.items():
            out_path = out_dir / f"{band_name}.tif"
            
            transform = from_origin(scene.bounds[0], scene.bounds[3],
                                   band.resolution, band.resolution)
            
            with rasterio.open(
                out_path, 'w',
                driver='GTiff',
                height=band.data.shape[0],
                width=band.data.shape[1],
                count=1,
                dtype=band.data.dtype,
                crs=scene.crs,
                transform=transform
            ) as dst:
                dst.write(band.data, 1)
        
        # Save metadata
        metadata = {
            'scene_id': scene.scene_id,
            'acquisition_time': scene.acquisition_time.isoformat(),
            'bounds': scene.bounds,
            'crs': scene.crs,
            'cloud_cover': scene.cloud_cover,
            'bands': list(scene.bands.keys())
        }
        
        with open(out_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Scene saved to {out_dir}")

# Example usage
if __name__ == "__main__":
    # Initialize interface
    sentinel = Sentinel2Interface(data_dir='./sentinel_data')
    
    # Example: Load a scene (would need actual files)
    print("Sentinel-2 Interface initialized")
    print(f"Data directory: {sentinel.data_dir}")
    print(f"Available bands: {list(Sentinel2Interface.BANDS.keys())}")
    print(f"Available indices: {list(Sentinel2Interface.INDICES.keys())}")
    
    # Example NDVI calculation
    print("\nNDVI formula: (NIR - RED) / (NIR + RED)")
    print("Uses bands: B08 (NIR) and B04 (RED)")
