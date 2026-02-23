"""Pytest configuration and fixtures."""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import shutil

from biotica import BIOTICACore
from biotica.biome.registry import BiomeRegistry, BiomeType

@pytest.fixture
def biotica_core():
    """Create BIOTICA core instance for testing."""
    return BIOTICACore()

@pytest.fixture
def biome_registry():
    """Create biome registry for testing."""
    return BiomeRegistry()

@pytest.fixture
def sample_parameters():
    """Sample parameter values for testing."""
    return {
        'VCA': 0.85,
        'MDI': 0.78,
        'PTS': 0.82,
        'HFI': 0.71,
        'BNC': 0.68,
        'SGH': 0.73,
        'AES': 0.88,
        'TMI': 0.79,
        'RRC': 0.65
    }

@pytest.fixture
def sample_timeseries():
    """Sample time series data for testing."""
    np.random.seed(42)
    n_points = 200
    t = np.linspace(0, 10, n_points)
    # Create series with increasing variance
    noise = np.random.randn(n_points) * (1 + 0.1 * t)
    x = np.zeros(n_points)
    x[0] = noise[0]
    for i in range(1, n_points):
        x[i] = 0.7 * x[i-1] + noise[i] * (1 + 0.02 * i)
    return x + 0.01 * t

@pytest.fixture
def sample_spectral_data():
    """Sample hyperspectral data for testing."""
    wavelengths = np.linspace(400, 2500, 210)
    # Create synthetic reflectance spectrum
    reflectance = 0.3 + 0.2 * np.sin(wavelengths / 500) + 0.05 * np.random.randn(len(wavelengths))
    return wavelengths, reflectance

@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_plot_data():
    """Sample plot data for testing."""
    return {
        'plot_id': 'TEST_001',
        'biome': BiomeType.TROPICAL_RAINFOREST,
        'ndvi': 0.75,
        'lai': 5.2,
        'gpp': 1800,
        'shannon': 3.2,
        'chao1': 150,
        'otus': 120,
        'greenup_doy': 120,
        'historical_greenup': [115, 118, 122, 119, 116],
        'precipitation': 800,
        'evapotranspiration': 750,
        'soil_moisture': 65,
        'runoff': 50,
        'nitrogen': 0.45,
        'phosphorus': 0.04,
        'potassium': 0.35,
        'organic_matter': 4.5,
        'heterozygosity': 0.65,
        'allele_richness': 45,
        'fst': 0.12,
        'population_size': 350,
        'human_footprint': 25,
        'fragmentation': 0.15,
        'pollution_index': 0.08,
        'distance_to_disturbance': 12.5
    }
