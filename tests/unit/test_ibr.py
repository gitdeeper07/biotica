"""Unit tests for IBR composite module."""

import pytest
import numpy as np
from biotica.ibr.composite import IBRComposite, IBRResult
from biotica.ibr.weights import BayesianWeights, WeightResult
from biotica.equations import IBRClass

class TestIBRComposite:
    """Test IBR composite calculator."""
    
    def test_initialization(self):
        """Test IBRComposite initialization."""
        ibr = IBRComposite(plot_id="TEST_001")
        assert ibr.plot_id == "TEST_001"
        assert ibr.parameters == {}
    
    def test_set_parameter(self):
        """Test setting single parameter."""
        ibr = IBRComposite()
        ibr.set_parameter('VCA', 0.85)
        
        assert 'VCA' in ibr.parameters
        assert ibr.parameters['VCA']['value'] == 0.85
        assert ibr.parameters['VCA']['uncertainty'] == 0.05
    
    def test_set_parameter_with_uncertainty(self):
        """Test setting parameter with custom uncertainty."""
        ibr = IBRComposite()
        ibr.set_parameter('VCA', 0.85, uncertainty=0.03)
        
        assert ibr.parameters['VCA']['uncertainty'] == 0.03
    
    def test_set_parameters(self, sample_parameters):
        """Test setting multiple parameters."""
        ibr = IBRComposite()
        ibr.set_parameters(sample_parameters)
        
        assert len(ibr.parameters) == 9
        for name, value in sample_parameters.items():
            assert name in ibr.parameters
            assert ibr.parameters[name]['value'] == value
    
    def test_validate_parameters(self):
        """Test parameter validation."""
        ibr = IBRComposite()
        
        # Valid parameters
        ibr.set_parameters({
            'VCA': 0.85, 'MDI': 0.78, 'PTS': 0.82,
            'HFI': 0.71, 'BNC': 0.68, 'SGH': 0.73,
            'AES': 0.88, 'TMI': 0.79, 'RRC': 0.65
        })
        
        is_valid, warnings = ibr.validate_parameters()
        assert is_valid
        assert len(warnings) == 0
        
        # Missing parameters
        ibr.parameters = {'VCA': 0.85}
        is_valid, warnings = ibr.validate_parameters()
        assert not is_valid
        assert len(warnings) > 0
    
    def test_compute(self, sample_parameters):
        """Test IBR computation."""
        ibr = IBRComposite(plot_id="TEST_001")
        ibr.set_parameters(sample_parameters)
        
        result = ibr.compute()
        
        assert isinstance(result, IBRResult)
        assert result.plot_id == "TEST_001"
        assert 0 <= result.score <= 1
        assert isinstance(result.classification, IBRClass)
        assert len(result.contributions) == 9
        assert 0 <= result.uncertainty <= 1
        assert 0 <= result.confidence <= 1
        
        # Check IBR formula: weighted sum
        expected_score = (
            0.85 * 0.20 + 0.78 * 0.15 + 0.82 * 0.12 +
            0.71 * 0.11 + 0.68 * 0.10 + 0.73 * 0.09 +
            0.88 * 0.08 + 0.79 * 0.08 + 0.65 * 0.07
        )
        assert abs(result.score - expected_score) < 1e-10
    
    def test_compute_from_raw(self, sample_plot_data):
        """Test IBR computation from raw data."""
        ibr = IBRComposite(plot_id=sample_plot_data['plot_id'])
        result = ibr.compute_from_raw(sample_plot_data)
        
        assert result.plot_id == "TEST_001"
        assert result.score > 0
        assert len(result.contributions) > 0
    
    def test_ibr_result_to_dict(self):
        """Test IBRResult to_dict conversion."""
        result = IBRResult(
            score=0.85,
            classification=IBRClass.FUNCTIONAL,
            contributions={'VCA': 0.17},
            uncertainty=0.05,
            confidence=0.95,
            plot_id="TEST_001",
            warnings=["Test warning"]
        )
        
        result_dict = result.to_dict()
        assert result_dict['score'] == 0.85
        assert result_dict['classification'] == "FUNCTIONAL"
        assert result_dict['plot_id'] == "TEST_001"
        assert 'timestamp' in result_dict
    
    def test_ibr_result_to_json(self):
        """Test IBRResult JSON serialization."""
        result = IBRResult(
            score=0.85,
            classification=IBRClass.FUNCTIONAL,
            contributions={'VCA': 0.17},
            uncertainty=0.05,
            confidence=0.95
        )
        
        json_str = result.to_json()
        assert isinstance(json_str, str)
        assert '"score": 0.85' in json_str

class TestBayesianWeights:
    """Test Bayesian weight estimation."""
    
    def test_initialization(self):
        """Test BayesianWeights initialization."""
        bw = BayesianWeights(n_chains=2, n_samples=1000)
        assert bw.n_chains == 2
        assert bw.n_samples == 1000
    
    def test_fallback_weights(self):
        """Test fallback weight estimation."""
        bw = BayesianWeights()
        param_names = ['VCA', 'MDI', 'PTS']
        
        result = bw._fallback_weights(param_names)
        
        assert isinstance(result, WeightResult)
        assert len(result.weights) == 3
        assert abs(sum(result.weights.values()) - 1.0) < 1e-10
        assert result.method == "fixed"
    
    def test_pca_weights(self):
        """Test PCA weight estimation."""
        # Create sample data
        np.random.seed(42)
        X = np.random.randn(100, 5)
        param_names = ['P1', 'P2', 'P3', 'P4', 'P5']
        
        result = BayesianWeights.pca_weights(X, param_names)
        
        assert isinstance(result, WeightResult)
        assert len(result.weights) == 5
        assert abs(sum(result.weights.values()) - 1.0) < 1e-10
        assert result.method == "pca"

class TestWeightResult:
    """Test WeightResult dataclass."""
    
    def test_creation(self):
        """Test WeightResult creation."""
        result = WeightResult(
            weights={'VCA': 0.20, 'MDI': 0.15},
            uncertainties={'VCA': 0.02, 'MDI': 0.03},
            convergence=True,
            method="test"
        )
        
        assert result.weights['VCA'] == 0.20
        assert result.uncertainties['MDI'] == 0.03
        assert result.convergence is True
        assert result.method == "test"
