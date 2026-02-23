"""Input/Output utilities for BIOTICA."""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
import json
import csv
import yaml
import warnings
from pathlib import Path
import pickle
from datetime import datetime
import hashlib

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    warnings.warn("pandas not available. CSV/Excel features disabled.")

try:
    import rasterio
    from rasterio.transform import from_origin
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False
    warnings.warn("rasterio not available. GeoTIFF features disabled.")

class FileIO:
    """File input/output utilities."""
    
    SUPPORTED_EXTENSIONS = {
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.csv': 'csv',
        '.txt': 'text',
        '.npy': 'numpy',
        '.npz': 'numpy_compressed',
        '.pkl': 'pickle',
        '.pickle': 'pickle',
        '.tif': 'geotiff',
        '.tiff': 'geotiff',
        '.nc': 'netcdf',
        '.h5': 'hdf5',
        '.hdf5': 'hdf5',
    }
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize FileIO.
        
        Args:
            base_dir: Base directory for file operations
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def read(self, filepath: Union[str, Path], **kwargs) -> Any:
        """
        Read file based on extension.
        
        Args:
            filepath: Path to file
            **kwargs: Additional arguments for specific readers
            
        Returns:
            File contents
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        ext = filepath.suffix.lower()
        
        if ext == '.json':
            return self.read_json(filepath, **kwargs)
        elif ext in ['.yaml', '.yml']:
            return self.read_yaml(filepath, **kwargs)
        elif ext == '.csv':
            return self.read_csv(filepath, **kwargs)
        elif ext == '.txt':
            return self.read_text(filepath, **kwargs)
        elif ext == '.npy':
            return self.read_numpy(filepath, **kwargs)
        elif ext == '.npz':
            return self.read_numpy_compressed(filepath, **kwargs)
        elif ext in ['.pkl', '.pickle']:
            return self.read_pickle(filepath, **kwargs)
        elif ext in ['.tif', '.tiff']:
            return self.read_geotiff(filepath, **kwargs)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
    
    def write(self, 
             data: Any, 
             filepath: Union[str, Path],
             mkdir: bool = True,
             **kwargs) -> Path:
        """
        Write data to file based on extension.
        
        Args:
            data: Data to write
            filepath: Output file path
            mkdir: Create parent directories
            **kwargs: Additional arguments for specific writers
            
        Returns:
            Path to written file
        """
        filepath = Path(filepath)
        
        if mkdir:
            filepath.parent.mkdir(parents=True, exist_ok=True)
        
        ext = filepath.suffix.lower()
        
        if ext == '.json':
            self.write_json(data, filepath, **kwargs)
        elif ext in ['.yaml', '.yml']:
            self.write_yaml(data, filepath, **kwargs)
        elif ext == '.csv':
            self.write_csv(data, filepath, **kwargs)
        elif ext == '.txt':
            self.write_text(data, filepath, **kwargs)
        elif ext == '.npy':
            self.write_numpy(data, filepath, **kwargs)
        elif ext == '.npz':
            self.write_numpy_compressed(data, filepath, **kwargs)
        elif ext in ['.pkl', '.pickle']:
            self.write_pickle(data, filepath, **kwargs)
        elif ext in ['.tif', '.tiff']:
            self.write_geotiff(data, filepath, **kwargs)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
        
        return filepath
    
    def read_json(self, filepath: Union[str, Path], **kwargs) -> Dict:
        """Read JSON file."""
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def write_json(self, 
                   data: Dict, 
                   filepath: Union[str, Path],
                   indent: int = 2,
                   **kwargs):
        """Write JSON file."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=indent, **kwargs)
    
    def read_yaml(self, filepath: Union[str, Path], **kwargs) -> Dict:
        """Read YAML file."""
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
    
    def write_yaml(self, 
                   data: Dict, 
                   filepath: Union[str, Path],
                   **kwargs):
        """Write YAML file."""
        with open(filepath, 'w') as f:
            yaml.dump(data, f, **kwargs)
    
    def read_csv(self, 
                filepath: Union[str, Path],
                as_dataframe: bool = True,
                **kwargs) -> Union[List[Dict], 'pd.DataFrame']:
        """Read CSV file."""
        if PANDAS_AVAILABLE and as_dataframe:
            return pd.read_csv(filepath, **kwargs)
        else:
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                return list(reader)
    
    def write_csv(self, 
                 data: Union[List[Dict], 'pd.DataFrame'],
                 filepath: Union[str, Path],
                 **kwargs):
        """Write CSV file."""
        if PANDAS_AVAILABLE and hasattr(data, 'to_csv'):
            data.to_csv(filepath, index=False, **kwargs)
        else:
            if not data:
                return
            
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
    
    def read_text(self, filepath: Union[str, Path], **kwargs) -> str:
        """Read text file."""
        with open(filepath, 'r') as f:
            return f.read()
    
    def write_text(self, 
                   data: str, 
                   filepath: Union[str, Path],
                   **kwargs):
        """Write text file."""
        with open(filepath, 'w') as f:
            f.write(data)
    
    def read_numpy(self, filepath: Union[str, Path], **kwargs) -> np.ndarray:
        """Read numpy array."""
        return np.load(filepath, **kwargs)
    
    def write_numpy(self, 
                    data: np.ndarray, 
                    filepath: Union[str, Path],
                    **kwargs):
        """Write numpy array."""
        np.save(filepath, data, **kwargs)
    
    def read_numpy_compressed(self, filepath: Union[str, Path], **kwargs) -> Dict:
        """Read compressed numpy array."""
        return np.load(filepath, **kwargs)
    
    def write_numpy_compressed(self, 
                              data: Dict[str, np.ndarray],
                              filepath: Union[str, Path],
                              **kwargs):
        """Write compressed numpy array."""
        np.savez_compressed(filepath, **data)
    
    def read_pickle(self, filepath: Union[str, Path], **kwargs) -> Any:
        """Read pickle file."""
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    
    def write_pickle(self, 
                     data: Any, 
                     filepath: Union[str, Path],
                     protocol: int = pickle.HIGHEST_PROTOCOL,
                     **kwargs):
        """Write pickle file."""
        with open(filepath, 'wb') as f:
            pickle.dump(data, f, protocol=protocol)
    
    def read_geotiff(self, 
                    filepath: Union[str, Path],
                    band: int = 1,
                    **kwargs) -> Dict:
        """Read GeoTIFF file."""
        if not RASTERIO_AVAILABLE:
            raise ImportError("rasterio required for GeoTIFF reading")
        
        with rasterio.open(filepath) as src:
            data = src.read(band)
            metadata = {
                'crs': str(src.crs),
                'transform': src.transform.to_gdal() if src.transform else None,
                'bounds': src.bounds,
                'shape': src.shape,
                'nodata': src.nodata,
                'bands': src.count
            }
        
        return {'data': data, 'metadata': metadata}
    
    def write_geotiff(self,
                     data: Dict[str, Any],
                     filepath: Union[str, Path],
                     **kwargs):
        """Write GeoTIFF file."""
        if not RASTERIO_AVAILABLE:
            raise ImportError("rasterio required for GeoTIFF writing")
        
        # Extract data and metadata
        array = data.get('data', data)  # Allow direct array input
        metadata = data.get('metadata', {})
        
        # Get transform
        transform = metadata.get('transform')
        if transform and isinstance(transform, (tuple, list)):
            transform = from_origin(*transform)
        
        with rasterio.open(
            filepath, 'w',
            driver='GTiff',
            height=array.shape[0],
            width=array.shape[1],
            count=1,
            dtype=array.dtype,
            crs=metadata.get('crs', 'EPSG:4326'),
            transform=transform,
            **kwargs
        ) as dst:
            dst.write(array, 1)
    
    def find_files(self, 
                  pattern: str,
                  directory: Optional[Union[str, Path]] = None,
                  recursive: bool = True) -> List[Path]:
        """Find files matching pattern."""
        search_dir = Path(directory) if directory else self.base_dir
        
        if recursive:
            return list(search_dir.rglob(pattern))
        else:
            return list(search_dir.glob(pattern))
    
    def get_file_info(self, filepath: Union[str, Path]) -> Dict[str, Any]:
        """Get file information."""
        filepath = Path(filepath)
        
        if not filepath.exists():
            return {}
        
        stat = filepath.stat()
        
        # Calculate file hash
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        
        return {
            'path': str(filepath),
            'name': filepath.name,
            'extension': filepath.suffix,
            'size': stat.st_size,
            'size_mb': stat.st_size / (1024 * 1024),
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'is_file': filepath.is_file(),
            'is_dir': filepath.is_dir(),
            'hash': sha256.hexdigest()
        }
    
    def backup(self, 
              filepath: Union[str, Path],
              backup_dir: Optional[Union[str, Path]] = None) -> Path:
        """Create backup of file."""
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        if backup_dir:
            backup_path = Path(backup_dir)
        else:
            backup_path = filepath.parent / 'backups'
        
        backup_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_path / f"{filepath.stem}_{timestamp}{filepath.suffix}"
        
        import shutil
        shutil.copy2(filepath, backup_file)
        
        return backup_file

class DataCache:
    """Simple caching system for processed data."""
    
    def __init__(self, cache_dir: Optional[Union[str, Path]] = None):
        """
        Initialize cache.
        
        Args:
            cache_dir: Directory for cache files
        """
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / '.biotica_cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.io = FileIO(self.cache_dir)
    
    def _get_cache_key(self, key: str) -> str:
        """Generate cache filename from key."""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path."""
        return self.cache_dir / f"{self._get_cache_key(key)}.pkl"
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        cache_path = self._get_cache_path(key)
        
        if cache_path.exists():
            try:
                data = self.io.read_pickle(cache_path)
                # Check if expired
                if 'expires' in data:
                    if datetime.now() < datetime.fromisoformat(data['expires']):
                        return data['value']
                else:
                    return data
            except Exception:
                pass
        
        return None
    
    def set(self, 
           key: str, 
           value: Any, 
           ttl: Optional[int] = None):
        """
        Set item in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        cache_path = self._get_cache_path(key)
        
        if ttl:
            data = {
                'value': value,
                'expires': (datetime.now() + timedelta(seconds=ttl)).isoformat()
            }
        else:
            data = value
        
        self.io.write_pickle(data, cache_path)
    
    def clear(self, key: Optional[str] = None):
        """Clear cache."""
        if key:
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
        else:
            for cache_file in self.cache_dir.glob('*.pkl'):
                cache_file.unlink()
    
    def contains(self, key: str) -> bool:
        """Check if key exists in cache."""
        return self._get_cache_path(key).exists()

# Example usage
if __name__ == "__main__":
    # Initialize IO
    io = FileIO('./test_data')
    
    # Write JSON
    data = {'name': 'BIOTICA', 'version': '1.0.0', 'parameters': ['VCA', 'MDI']}
    io.write(data, 'config.json')
    
    # Read JSON
    loaded = io.read('config.json')
    print(f"Loaded JSON: {loaded}")
    
    # Write CSV
    csv_data = [
        {'id': 1, 'value': 0.85},
        {'id': 2, 'value': 0.92},
        {'id': 3, 'value': 0.78}
    ]
    io.write(csv_data, 'results.csv')
    
    # Get file info
    info = io.get_file_info('config.json')
    print(f"\nFile info: {info}")
    
    # Initialize cache
    cache = DataCache('./cache')
    cache.set('test_key', {'result': 42}, ttl=3600)
    cached = cache.get('test_key')
    print(f"\nCached value: {cached}")
    
    cache.clear()
