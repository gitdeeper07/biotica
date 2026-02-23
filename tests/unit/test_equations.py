"""Unit tests for equations module."""

import pytest
import numpy as np
from biotica.equations import BIOTICACore, ParameterResult, IBRClass

class TestBIOTICACore:
    """Test BIOTICA core functionality."""
    
    def test_initialization(self):
        """Test core initialization."""
        core = BIOTICACore()
        assert core is not None
        assert hasattr(core, 'IBR_WEIGHTS')
        assert len(core.IBR_WEIGHTS) == 9
    
    def test_compute_vca(self, biotica_core):
        """Test VCA computation."""
        result = biotica_core.compute_vca(ndvi=0.75, lai=5.2, gpp=1800)
        
        assert isinstance(result, ParameterResult)
        assert 0 <= result.value <= 1
        assert 0 <= result.uncertainty <= 1
        assert 0 <= result.confidence <= 1
        assert 'ndvi_norm' in result.metadata
    
    def test_compute_mdi(self, biotica_core):
        """Test MDI computation."""
        result = biotica_core.compute_mdi(
            shannon_index=3.2,
            chao1=150,
            observed_otus=120
        )
        
        assert isinstance(result, ParameterResult)
        assert 0 <= result.value <= 1
    
    def test_compute_pts(self, biotica_core):
        """Test PTS computation."""
        historical = [115, 118, 122, 119, 116]
        result = biotica_core.compute_pts(
            greenup_doy=120,
            senescence_doy=280,
            historical_greenup=historical
        )
        
        assert isinstance(result, ParameterResult)
        assert 0 <= result.value <= 1
    
    def test_compute_hfi(self, biotica_core):
        """Test HFI computation."""
        result = biotica_core.compute_hfi(
            precipitation=800,
            evapotranspiration=750,
            soil_moisture=65,
            runoff=50
        )
        
        assert isinstance(result, ParameterResult)
        assert 0 <= result.value <= 1
    
    def test_compute_bnc(self, biotica_core):
        """Test BNC computation."""
        result = biotica_core.compute_bnc(
            nitrogen=0.45,
            phosphorus=0.04,
            potassium=0.35,
            organic_matter=4.5
        )
        
        assert isinstance(result, ParameterResult)
        assert 0 <= result.value <= 1
    
    def test_compute_sgh(self, biotica_core):
        """Test SGH computation."""
        result = biotica_core.compute_sgh(
            heterozygosity=0.65,
            allele_richness=45,
            fst=0.12,
            population_size=350
        )
        
        assert isinstance(result, ParameterResult)
        assert 0 <= result.value <= 1
    
    def test_compute_aes(self, biotica_core):
        """Test AES computation."""
        result = biotica_core.compute_aes(
            human_footprint=25,
            fragmentation=0.15,
            pollution_index=0.08,
            distance_to_disturbance=12.5
        )
        
        assert isinstance(result, ParameterResult)
        assert 0 <= result.value <= 1
    
    def test_compute_tmi(self, biotica_core):
        """Test TMI computation."""
        result = biotica_core.compute_tmi(
            connectance=0.25,
            modularity=0.55,
            trophic_levels=4,
            omnivory=0.3
        )
        
        assert isinstance(result, ParameterResult)
        assert 0 <= result.value <= 1
    
    def test_compute_rrc(self, biotica_core):
        """Test RRC computation."""
        result = biotica_core.compute_rrc(
            recovery_rate=0.35,
            resilience=0.65,
            seed_bank=5000,
            soil_organic_carbon=3.5
        )
        
        assert isinstance(result, ParameterResult)
        assert 0 <= result.value <= 1
    
    def test_compute_ibr(self, biotica_core, sample_parameters):
        """Test IBR computation."""
        result = biotica_core.compute_ibr(sample_parameters)
        
        assert isinstance(result, dict)
        assert 'score' in result
        assert 'classification' in result
        assert 'contributions' in result
        assert 'uncertainty' in result
        assert 'confidence' in result
        
        assert 0 <= result['score'] <= 1
        assert result['classification'] in [c.value for c in IBRClass]
        assert len(result['contributions']) == 9
    
    def test_ibr_classification(self, biotica_core):
        """Test IBR classification thresholds."""
        test_cases = [
            (0.92, IBRClass.PRISTINE),
            (0.80, IBRClass.FUNCTIONAL),
            (0.68, IBRClass.IMPAIRED),
            (0.52, IBRClass.DEGRADED),
            (0.35, IBRClass.COLLAPSED)
        ]
        
        for score, expected in test_cases:
            result = biotica_core._classify_ibr(score)
            assert result == expected
    
    def test_validate_parameters(self, biotica_core):
        """Test parameter validation."""
        valid_params = {'VCA': 0.5, 'MDI': 0.6}
        invalid_params = {'VCA': 1.5, 'MDI': -0.1}
        
        assert biotica_core._validate_parameters(valid_params)
        assert not biotica_core._validate_parameters(invalid_params)
    
    def test_detect_tipping_point(self, biotica_core, sample_timeseries):
        """Test tipping point detection."""
        result = biotica_core.detect_tipping_point(sample_timeseries)
        
        assert isinstance(result, dict)
        assert 'critical_slowing_down' in result
        assert 'warning_level' in result
        assert 0 <= result['warning_level'] <= 3
        assert 'variance_trend' in result
        assert 'autocorrelation_trend' in result
    
    def test_normalize_veg_index(self, biotica_core):
        """Test vegetation index normalization."""
        # Test NDVI normalization
        ndvi_norm = biotica_core._normalize_veg_index('NDVI', 0.75)
        assert 0 <= ndvi_norm <= 1
        
        # Test out of range values
        ndvi_norm = biotica_core._normalize_veg_index('NDVI', 1.5)
        assert ndvi_norm == 1.0
        
        ndvi_norm = biotica_core._normalize_veg_index('NDVI', -0.5)
        assert ndvi_norm == 0.0

class TestParameterResult:
    """Test ParameterResult dataclass."""
    
    def test_creation(self):
        """Test ParameterResult creation."""
        result = ParameterResult(
            value=0.85,
            uncertainty=0.05,
            confidence=0.95,
            metadata={'test': True}
        )
        
        assert result.value == 0.85
        assert result.uncertainty == 0.05
        assert result.confidence == 0.95
        assert result.metadata['test'] is True
    
    def test_default_metadata(self):
        """Test default metadata."""
        result = ParameterResult(value=0.85, uncertainty=0.05, confidence=0.95)
        assert result.metadata == {}
