"""Unit tests for preprocessing module."""

import pytest
import numpy as np
from biotica.preprocessing.spectral import SpectralPreprocessor, SpectralData

# Skip tests if SciPy not available
pytest.importorskip("scipy")

class TestSpectralPreprocessor:
    """Test spectral preprocessor."""
    
    def test_initialization(self):
        """Test preprocessor initialization."""
        preprocessor = SpectralPreprocessor(
            window_length=11,
            polyorder=3,
            derivative_order=0
        )
        
        assert preprocessor.window_length == 11
        assert preprocessor.polyorder == 3
        assert preprocessor.derivative_order == 0
    
    def test_preprocess(self, sample_spectral_data):
        """Test preprocessing pipeline."""
        wavelengths, reflectance = sample_spectral_data
        
        preprocessor = SpectralPreprocessor()
        result = preprocessor.preprocess(
            wavelengths, reflectance,
            remove_noise=True,
            continuum_removal=True,
            normalize=True
        )
        
        assert isinstance(result, SpectralData)
        assert len(result.wavelengths) == len(wavelengths)
        assert len(result.reflectance) == len(reflectance)
        assert 0 <= result.reflectance.min() <= result.reflectance.max() <= 1
        assert 'normalized' in result.metadata
    
    def test_preprocess_no_normalize(self, sample_spectral_data):
        """Test preprocessing without normalization."""
        wavelengths, reflectance = sample_spectral_data
        
        preprocessor = SpectralPreprocessor()
        result = preprocessor.preprocess(
            wavelengths, reflectance,
            remove_noise=True,
            normalize=False
        )
        
        # Should maintain original scale
        assert result.reflectance.min() < 0 or result.reflectance.max() > 1
    
    def test_calculate_indices(self, sample_spectral_data):
        """Test vegetation index calculation."""
        wavelengths, reflectance = sample_spectral_data
        
        preprocessor = SpectralPreprocessor()
        spectral_data = preprocessor.preprocess(wavelengths, reflectance)
        
        indices = preprocessor.calculate_indices(
            spectral_data,
            indices=['NDVI', 'EVI', 'PRI']
        )
        
        assert isinstance(indices, dict)
        assert len(indices) > 0
        for value in indices.values():
            assert -1 <= value <= 1
    
    def test_resample(self, sample_spectral_data):
        """Test spectral resampling."""
        wavelengths, reflectance = sample_spectral_data
        
        preprocessor = SpectralPreprocessor()
        spectral_data = preprocessor.preprocess(wavelengths, reflectance)
        
        # Resample to fewer bands
        target_wavelengths = np.linspace(500, 2000, 100)
        resampled = preprocessor.resample(spectral_data, target_wavelengths)
        
        assert len(resampled.wavelengths) == 100
        assert len(resampled.reflectance) == 100
        assert resampled.metadata['resampled'] is True
    
    def test_extract_features(self, sample_spectral_data):
        """Test feature extraction."""
        wavelengths, reflectance = sample_spectral_data
        
        preprocessor = SpectralPreprocessor()
        spectral_data = preprocessor.preprocess(wavelengths, reflectance)
        
        # Extract features from specific bands
        feature_bands = [(500, 600), (600, 700), (700, 800)]
        features = preprocessor.extract_features(spectral_data, feature_bands)
        
        # Each band contributes 4 features (mean, std, max, min)
        expected_length = len(feature_bands) * 4
        assert len(features) == expected_length
    
    def test_detect_absorption_features(self, sample_spectral_data):
        """Test absorption feature detection."""
        wavelengths, reflectance = sample_spectral_data
        
        preprocessor = SpectralPreprocessor()
        spectral_data = preprocessor.preprocess(wavelengths, reflectance)
        
        features = preprocessor.detect_absorption_features(spectral_data)
        
        assert isinstance(features, dict)
        assert 'n_absorptions' in features
        assert 'absorption_wavelengths' in features

class TestSpectralData:
    """Test SpectralData container."""
    
    def test_creation(self):
        """Test SpectralData creation."""
        wavelengths = np.array([400, 500, 600])
        reflectance = np.array([0.1, 0.2, 0.3])
        
        data = SpectralData(wavelengths, reflectance)
        
        assert np.array_equal(data.wavelengths, wavelengths)
        assert np.array_equal(data.reflectance, reflectance)
    
    def test_get_band(self):
        """Test band retrieval."""
        wavelengths = np.array([400, 500, 600, 700, 800])
        reflectance = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        
        data = SpectralData(wavelengths, reflectance)
        
        # Exact wavelength
        assert data.get_band(500) == 0.2
        
        # Within tolerance
        assert data.get_band(505, tolerance=10) == 0.2
        
        # Outside tolerance
        assert np.isnan(data.get_band(900, tolerance=10))
    
    def test_get_bands(self):
        """Test multiple band retrieval."""
        wavelengths = np.array([400, 500, 600, 700, 800])
        reflectance = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        
        data = SpectralData(wavelengths, reflectance)
        
        bands = data.get_bands([500, 700])
        assert bands['500'] == 0.2
        assert bands['700'] == 0.4
    
    def test_get_indices(self):
        """Test index calculation."""
        wavelengths = np.array([400, 500, 600, 700, 800])
        reflectance = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        
        data = SpectralData(wavelengths, reflectance)
        
        indices = data.get_indices({
            'NDVI': (680, 800),
            'NDWI': (857, 1241)
        })
        
        # NDVI should use closest available bands
        assert 'NDVI' in indices
        assert -1 <= indices['NDVI'] <= 1
    
    def test_serialization(self, temp_dir):
        """Test serialization."""
        wavelengths = np.array([400, 500, 600])
        reflectance = np.array([0.1, 0.2, 0.3])
        metadata = {'test': True}
        
        data = SpectralData(wavelengths, reflectance, metadata)
        
        # Save
        filepath = temp_dir / "spectral.json"
        data.save(filepath)
        assert filepath.exists()
        
        # Load
        loaded = SpectralData.load(filepath)
        assert np.array_equal(loaded.wavelengths, wavelengths)
        assert np.array_equal(loaded.reflectance, reflectance)
        assert loaded.metadata['test'] is True
