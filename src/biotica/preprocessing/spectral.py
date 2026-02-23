"""Hyperspectral data preprocessing module."""

import numpy as np
from typing import Optional, Tuple, List, Dict, Any, Union
from dataclasses import dataclass, field
import warnings
import json

try:
    from scipy import ndimage, signal
    from scipy.interpolate import interp1d, CubicSpline
    from scipy.signal import savgol_filter
    from scipy.spatial import ConvexHull
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    warnings.warn("SciPy not available. Some preprocessing features disabled.")

@dataclass
class SpectralData:
    """Container for processed spectral data."""
    wavelengths: np.ndarray
    reflectance: np.ndarray
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate data after initialization."""
        if len(self.wavelengths) != len(self.reflectance):
            raise ValueError("Wavelengths and reflectance must have same length")
        
    def get_band(self, wavelength: float, tolerance: float = 5.0) -> float:
        """
        Get reflectance at specific wavelength.
        
        Args:
            wavelength: Target wavelength in nm
            tolerance: Acceptable tolerance in nm
            
        Returns:
            Reflectance value or NaN if not found
        """
        idx = np.argmin(np.abs(self.wavelengths - wavelength))
        if np.abs(self.wavelengths[idx] - wavelength) <= tolerance:
            return float(self.reflectance[idx])
        return np.nan
    
    def get_bands(self, wavelengths: List[float], tolerance: float = 5.0) -> Dict[str, float]:
        """
        Get reflectance at multiple wavelengths.
        
        Args:
            wavelengths: List of target wavelengths
            tolerance: Acceptable tolerance in nm
            
        Returns:
            Dictionary mapping wavelength to reflectance
        """
        return {str(wv): self.get_band(wv, tolerance) for wv in wavelengths}
    
    def get_indices(self, indices_dict: Dict[str, Tuple[float, float]]) -> Dict[str, float]:
        """
        Calculate multiple vegetation indices.
        
        Args:
            indices_dict: Dictionary mapping index name to wavelength pair
            
        Returns:
            Dictionary of calculated indices
        """
        results = {}
        for name, (wv1, wv2) in indices_dict.items():
            r1 = self.get_band(wv1)
            r2 = self.get_band(wv2)
            if not np.isnan(r1) and not np.isnan(r2):
                # Normalized Difference Index
                results[name] = float((r1 - r2) / (r1 + r2 + 1e-10))
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'wavelengths': self.wavelengths.tolist(),
            'reflectance': self.reflectance.tolist(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SpectralData':
        """Create from dictionary."""
        return cls(
            wavelengths=np.array(data['wavelengths']),
            reflectance=np.array(data['reflectance']),
            metadata=data.get('metadata', {})
        )
    
    def save(self, filepath: str):
        """Save to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> 'SpectralData':
        """Load from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

class SpectralPreprocessor:
    """
    Preprocess hyperspectral data for BIOTICA.
    
    Steps:
    1. Noise reduction (Savitzky-Golay filter)
    2. Continuum removal
    3. Band selection
    4. Normalization
    5. Derivative calculation
    """
    
    # Common vegetation indices (wavelengths in nm)
    VEGETATION_INDICES = {
        'NDVI': (680, 800),      # Normalized Difference Vegetation Index
        'EVI': (680, 800, 480),  # Enhanced Vegetation Index (special case)
        'NDWI': (857, 1241),     # Normalized Difference Water Index
        'PRI': (531, 570),       # Photochemical Reflectance Index
        'CHL': (550, 700),       # Chlorophyll Index
        'CAR': (510, 560),       # Carotenoid Index
        'ARI': (550, 700),       # Anthocyanin Reflectance Index
        'SIPI': (445, 680),      # Structure Insensitive Pigment Index
        'PSRI': (680, 500),      # Plant Senescence Reflectance Index
        'NDLI': (1754, 1680),    # Normalized Difference Lignin Index
        'NDNI': (1510, 1680),    # Normalized Difference Nitrogen Index
        'CAI': (2000, 2100),     # Cellulose Absorption Index
    }
    
    # Water absorption bands for masking
    WATER_BANDS = [(1350, 1450), (1800, 1950), (2400, 2500)]
    
    def __init__(self, 
                 window_length: int = 11,
                 polyorder: int = 3,
                 derivative_order: int = 0,
                 mask_water_bands: bool = True):
        """
        Initialize preprocessor.
        
        Args:
            window_length: Window length for Savitzky-Golay filter
            polyorder: Polynomial order for filter
            derivative_order: Derivative order (0 = reflectance, 1 = first derivative)
            mask_water_bands: Whether to mask atmospheric water absorption bands
        """
        self.window_length = window_length
        self.polyorder = polyorder
        self.derivative_order = derivative_order
        self.mask_water_bands = mask_water_bands
        
        if not SCIPY_AVAILABLE:
            warnings.warn("SciPy not available. Using fallback preprocessing.")
    
    def preprocess(self, 
                   wavelengths: np.ndarray,
                   reflectance: np.ndarray,
                   remove_noise: bool = True,
                   continuum_removal: bool = False,
                   normalize: bool = True,
                   calculate_derivative: bool = False) -> SpectralData:
        """
        Full preprocessing pipeline.
        
        Args:
            wavelengths: Array of wavelengths (nm)
            reflectance: Array of reflectance values
            remove_noise: Apply Savitzky-Golay filtering
            continuum_removal: Apply continuum removal
            normalize: Normalize to [0,1]
            calculate_derivative: Calculate derivative spectra
            
        Returns:
            Processed SpectralData object
        """
        # Convert to numpy arrays
        wavelengths = np.asarray(wavelengths)
        reflectance = np.asarray(reflectance)
        
        # Sort by wavelength
        sort_idx = np.argsort(wavelengths)
        wavelengths = wavelengths[sort_idx]
        reflectance = reflectance[sort_idx]
        
        # Remove negative values
        reflectance = np.maximum(reflectance, 0)
        
        # Mask water absorption bands
        if self.mask_water_bands and SCIPY_AVAILABLE:
            reflectance = self._mask_water_bands(wavelengths, reflectance)
        
        # Remove noise with Savitzky-Golay
        if remove_noise and SCIPY_AVAILABLE and len(reflectance) > self.window_length:
            try:
                reflectance = savgol_filter(
                    reflectance, 
                    self.window_length, 
                    self.polyorder,
                    deriv=self.derivative_order
                )
            except Exception as e:
                warnings.warn(f"Savitzky-Golay filtering failed: {e}")
        
        # Continuum removal
        if continuum_removal and SCIPY_AVAILABLE:
            reflectance = self._continuum_removal(wavelengths, reflectance)
        
        # Calculate derivative
        if calculate_derivative and SCIPY_AVAILABLE:
            derivative = self._calculate_derivative(wavelengths, reflectance)
            reflectance = derivative
        
        # Normalize
        if normalize:
            ref_min = reflectance.min()
            ref_max = reflectance.max()
            if ref_max > ref_min:
                reflectance = (reflectance - ref_min) / (ref_max - ref_min)
            else:
                reflectance = np.zeros_like(reflectance)
        
        # Handle any remaining NaN or inf
        reflectance = np.nan_to_num(reflectance, nan=0.0, posinf=1.0, neginf=0.0)
        
        metadata = {
            'window_length': self.window_length,
            'polyorder': self.polyorder,
            'derivative_order': self.derivative_order,
            'continuum_removal': continuum_removal,
            'normalized': normalize,
            'mask_water_bands': self.mask_water_bands,
            'calculate_derivative': calculate_derivative,
            'min_wavelength': float(wavelengths.min()),
            'max_wavelength': float(wavelengths.max()),
            'n_bands': len(wavelengths),
            'reflectance_min': float(reflectance.min()),
            'reflectance_max': float(reflectance.max()),
            'reflectance_mean': float(reflectance.mean())
        }
        
        return SpectralData(wavelengths, reflectance, metadata)
    
    def _mask_water_bands(self, wavelengths: np.ndarray, 
                          reflectance: np.ndarray) -> np.ndarray:
        """Mask atmospheric water absorption bands."""
        masked = reflectance.copy()
        
        for start, end in self.WATER_BANDS:
            mask = (wavelengths >= start) & (wavelengths <= end)
            if mask.any():
                # Interpolate over water bands
                valid = ~mask
                if valid.sum() > 1:
                    interp = interp1d(
                        wavelengths[valid],
                        reflectance[valid],
                        kind='linear',
                        bounds_error=False,
                        fill_value='extrapolate'
                    )
                    masked[mask] = interp(wavelengths[mask])
        
        return masked
    
    def _continuum_removal(self, wavelengths: np.ndarray, 
                          reflectance: np.ndarray) -> np.ndarray:
        """Apply continuum removal to spectra."""
        try:
            # Find convex hull for continuum
            points = np.column_stack([wavelengths, reflectance])
            hull = ConvexHull(points)
            
            # Get upper envelope
            upper_idx = hull.vertices
            upper_idx = upper_idx[np.argsort(wavelengths[upper_idx])]
            
            # Add endpoints if missing
            if wavelengths[upper_idx[0]] > wavelengths[0]:
                upper_idx = np.insert(upper_idx, 0, 0)
            if wavelengths[upper_idx[-1]] < wavelengths[-1]:
                upper_idx = np.append(upper_idx, len(wavelengths)-1)
            
            # Remove duplicates
            upper_idx = np.unique(upper_idx)
            
            # Interpolate continuum
            continuum_func = interp1d(
                wavelengths[upper_idx],
                reflectance[upper_idx],
                kind='linear',
                bounds_error=False,
                fill_value='extrapolate'
            )
            
            continuum = continuum_func(wavelengths)
            continuum = np.maximum(continuum, 1e-10)
            
            # Remove continuum
            result = reflectance / continuum
            
            # Clip to reasonable range
            result = np.clip(result, 0, 2)
            
            return result
            
        except Exception as e:
            warnings.warn(f"Continuum removal failed: {e}")
            return reflectance
    
    def _calculate_derivative(self, wavelengths: np.ndarray, 
                             reflectance: np.ndarray) -> np.ndarray:
        """Calculate first derivative of spectra."""
        try:
            # Use cubic spline for smooth derivative
            cs = CubicSpline(wavelengths, reflectance)
            derivative = cs.derivative()(wavelengths)
            
            # Normalize derivative
            derivative = derivative / (np.abs(derivative).max() + 1e-10)
            
            return derivative
            
        except Exception as e:
            warnings.warn(f"Derivative calculation failed: {e}")
            return reflectance
    
    def calculate_indices(self, 
                         spectral_data: SpectralData,
                         indices: Optional[List[str]] = None) -> Dict[str, float]:
        """
        Calculate vegetation indices.
        
        Args:
            spectral_data: Processed spectral data
            indices: List of index names to calculate
            
        Returns:
            Dictionary of index values
        """
        if indices is None:
            indices = list(self.VEGETATION_INDICES.keys())
        
        results = {}
        
        for index in indices:
            if index not in self.VEGETATION_INDICES:
                continue
                
            bands = self.VEGETATION_INDICES[index]
            
            if index == 'EVI':
                # EVI: 2.5 * ((NIR - RED) / (NIR + 6*RED - 7.5*BLUE + 1))
                nir = spectral_data.get_band(800)
                red = spectral_data.get_band(680)
                blue = spectral_data.get_band(480)
                
                if not any(np.isnan([nir, red, blue])):
                    evi = 2.5 * (nir - red) / (nir + 6*red - 7.5*blue + 1)
                    results[index] = float(np.clip(evi, -1, 1))
            else:
                if len(bands) == 2:
                    b1 = spectral_data.get_band(bands[0])
                    b2 = spectral_data.get_band(bands[1])
                    if not np.isnan(b1) and not np.isnan(b2):
                        ndi = (b1 - b2) / (b1 + b2 + 1e-10)
                        results[index] = float(np.clip(ndi, -1, 1))
        
        return results
    
    def resample(self, 
                spectral_data: SpectralData,
                target_wavelengths: np.ndarray,
                kind: str = 'cubic') -> SpectralData:
        """
        Resample spectra to target wavelengths.
        
        Args:
            spectral_data: Input spectral data
            target_wavelengths: Target wavelengths
            kind: Interpolation kind ('linear', 'cubic', 'quadratic')
            
        Returns:
            Resampled SpectralData
        """
        if not SCIPY_AVAILABLE:
            raise ImportError("SciPy required for resampling")
        
        # Remove any NaN values for interpolation
        valid_mask = ~np.isnan(spectral_data.reflectance)
        wavelengths_valid = spectral_data.wavelengths[valid_mask]
        reflectance_valid = spectral_data.reflectance[valid_mask]
        
        if len(wavelengths_valid) < 2:
            raise ValueError("Insufficient valid data points for resampling")
        
        # Create interpolation function
        if kind == 'linear':
            interp_func = interp1d(
                wavelengths_valid,
                reflectance_valid,
                kind='linear',
                bounds_error=False,
                fill_value='extrapolate'
            )
        else:
            try:
                interp_func = CubicSpline(
                    wavelengths_valid,
                    reflectance_valid,
                    extrapolate=True
                )
            except:
                interp_func = interp1d(
                    wavelengths_valid,
                    reflectance_valid,
                    kind=kind,
                    bounds_error=False,
                    fill_value='extrapolate'
                )
        
        # Interpolate
        new_reflectance = interp_func(target_wavelengths)
        
        # Handle any remaining issues
        new_reflectance = np.nan_to_num(new_reflectance, nan=0.0)
        new_reflectance = np.clip(new_reflectance, 0, 1)
        
        metadata = spectral_data.metadata.copy()
        metadata['resampled'] = True
        metadata['resample_kind'] = kind
        metadata['original_wavelengths'] = spectral_data.wavelengths.tolist()
        metadata['n_original'] = len(spectral_data.wavelengths)
        metadata['n_resampled'] = len(target_wavelengths)
        
        return SpectralData(target_wavelengths, new_reflectance, metadata)
    
    def extract_features(self, 
                        spectral_data: SpectralData,
                        feature_bands: Optional[List[Tuple[float, float]]] = None) -> np.ndarray:
        """
        Extract features for machine learning.
        
        Args:
            spectral_data: Processed spectral data
            feature_bands: List of (start, end) wavelength ranges
            
        Returns:
            Feature vector
        """
        if feature_bands is None:
            # Default: use all bands
            return spectral_data.reflectance
        
        features = []
        
        for start, end in feature_bands:
            mask = (spectral_data.wavelengths >= start) & (spectral_data.wavelengths <= end)
            if mask.any():
                band_values = spectral_data.reflectance[mask]
                features.extend([
                    np.mean(band_values),
                    np.std(band_values),
                    np.max(band_values),
                    np.min(band_values)
                ])
        
        return np.array(features)
    
    def detect_absorption_features(self, 
                                  spectral_data: SpectralData,
                                  prominence: float = 0.05) -> Dict[str, Any]:
        """
        Detect absorption features in spectra.
        
        Args:
            spectral_data: Processed spectral data
            prominence: Minimum prominence for peak detection
            
        Returns:
            Dictionary with absorption features
        """
        if not SCIPY_AVAILABLE:
            return {}
        
        from scipy.signal import find_peaks
        
        # Invert for absorption (peaks become valleys)
        inverted = 1 - spectral_data.reflectance
        
        # Find peaks in inverted spectrum
        peaks, properties = find_peaks(
            inverted,
            prominence=prominence,
            width=5
        )
        
        features = {
            'n_absorptions': len(peaks),
            'absorption_wavelengths': spectral_data.wavelengths[peaks].tolist(),
            'absorption_depths': inverted[peaks].tolist(),
            'absorption_widths': properties['widths'].tolist() if 'widths' in properties else []
        }
        
        return features

# Example usage
if __name__ == "__main__":
    # Create sample data
    wavelengths = np.linspace(400, 2500, 210)  # 210 bands
    reflectance = 0.3 + 0.2 * np.sin(wavelengths / 500) + 0.05 * np.random.randn(len(wavelengths))
    
    # Initialize preprocessor
    preprocessor = SpectralPreprocessor(window_length=11, polyorder=3)
    
    # Preprocess
    processed = preprocessor.preprocess(
        wavelengths, 
        reflectance,
        remove_noise=True,
        continuum_removal=True,
        normalize=True
    )
    
    print(f"Processed {processed.metadata['n_bands']} bands")
    print(f"Reflectance range: [{processed.metadata['reflectance_min']:.3f}, "
          f"{processed.metadata['reflectance_max']:.3f}]")
    
    # Calculate vegetation indices
    indices = preprocessor.calculate_indices(processed, ['NDVI', 'EVI', 'PRI'])
    print("\nVegetation indices:")
    for name, value in indices.items():
        print(f"  {name}: {value:.3f}")
    
    # Detect absorption features
    features = preprocessor.detect_absorption_features(processed)
    print(f"\nDetected {features.get('n_absorptions', 0)} absorption features")
