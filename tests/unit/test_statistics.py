"""Unit tests for statistics module."""

import pytest
import numpy as np
from biotica.statistics.tipping_points import TippingPointDetector, TippingPointResult, EarlyWarningSignals

# Skip tests if SciPy not available
pytest.importorskip("scipy")

class TestTippingPointDetector:
    """Test tipping point detector."""
    
    def test_initialization(self):
        """Test detector initialization."""
        detector = TippingPointDetector(window=30, lag=1, min_data_points=50)
        
        assert detector.window == 30
        assert detector.lag == 1
        assert detector.min_data_points == 50
        assert detector.significance_level == 0.05
    
    def test_detect_with_sufficient_data(self, sample_timeseries):
        """Test detection with sufficient data."""
        detector = TippingPointDetector(window=30, min_data_points=50)
        result = detector.detect(sample_timeseries)
        
        assert isinstance(result, TippingPointResult)
        assert hasattr(result, 'critical_slowing_down')
        assert hasattr(result, 'warning_level')
        assert hasattr(result, 'variance_trend')
        assert hasattr(result, 'autocorrelation_trend')
        assert hasattr(result, 'confidence')
        
        assert 0 <= result.warning_level <= 3
        assert 0 <= result.confidence <= 1
    
    def test_detect_with_insufficient_data(self):
        """Test detection with insufficient data."""
        detector = TippingPointDetector(min_data_points=100)
        small_series = np.random.randn(50)
        
        result = detector.detect(small_series)
        
        assert result.warning_level == 0
        assert 'error' in result.metadata
    
    def test_detect_trending_series(self):
        """Test detection with trending series."""
        # Create series with increasing variance (early warning)
        np.random.seed(42)
        n_points = 200
        t = np.linspace(0, 10, n_points)
        
        # Increasing variance
        noise = np.random.randn(n_points) * (1 + 0.2 * t)
        x = np.cumsum(noise)  # Random walk
        
        detector = TippingPointDetector(window=30)
        result = detector.detect(x)
        
        # Should detect some warning
        assert result.warning_level >= 1
    
    def test_detect_stable_series(self):
        """Test detection with stable series."""
        # Create stable series (no warning)
        np.random.seed(42)
        stable = np.random.randn(200) * 0.1
        
        detector = TippingPointDetector(window=30)
        result = detector.detect(stable)
        
        # Should have low warning level
        assert result.warning_level <= 1
    
    def test_detrend(self):
        """Test detrending functionality."""
        # Create series with trend
        t = np.arange(200)
        series = 0.01 * t + np.random.randn(200) * 0.1
        
        detector = TippingPointDetector(detrend=True)
        result_with_detrend = detector.detect(series)
        
        detector_no_detrend = TippingPointDetector(detrend=False)
        result_no_detrend = detector_no_detrend.detect(series)
        
        # Results should differ
        assert result_with_detrend.variance_trend != result_no_detrend.variance_trend
    
    def test_detect_multivariate(self):
        """Test multivariate detection."""
        # Create multivariate time series
        n_points = 200
        n_vars = 3
        data = np.random.randn(n_points, n_vars)
        var_names = ['Var1', 'Var2', 'Var3']
        
        detector = TippingPointDetector()
        results = detector.detect_multivariate(data, var_names)
        
        assert len(results) == n_vars
        for name in var_names:
            assert name in results
            assert isinstance(results[name], TippingPointResult)
    
    def test_spatial_coherence(self):
        """Test spatial coherence analysis."""
        # Create spatial data (time, lat, lon)
        n_time, n_lat, n_lon = 100, 10, 10
        spatial_data = np.random.randn(n_time, n_lat, n_lon)
        
        # Add coherent signal in one region
        spatial_data[:, 2:5, 3:6] += np.linspace(0, 1, n_time)[:, None, None]
        
        lat = np.linspace(-10, 10, n_lat)
        lon = np.linspace(-20, 20, n_lon)
        
        detector = TippingPointDetector()
        result = detector.spatial_coherence(spatial_data, lat, lon)
        
        assert 'n_coherent_regions' in result
        assert 'warning_map' in result
        assert 'regions' in result
        assert result['n_coherent_regions'] >= 0

class TestEarlyWarningSignals:
    """Test comprehensive early warning signals."""
    
    def test_initialization(self):
        """Test initialization."""
        ews = EarlyWarningSignals()
        assert ews.detector is not None
        assert ews.results == []
    
    def test_analyze_all_methods(self, sample_timeseries):
        """Test analysis with all methods."""
        ews = EarlyWarningSignals()
        results = ews.analyze(sample_timeseries, method='all')
        
        assert 'variance' in results
        assert 'autocorrelation' in results
        assert 'skewness' in results
        assert 'kurtosis' in results
        assert 'combined' in results
        
        # Check variance results
        assert 'trend' in results['variance']
        assert 'p_value' in results['variance']
        assert 'values' in results['variance']
    
    def test_analyze_single_method(self, sample_timeseries):
        """Test analysis with single method."""
        ews = EarlyWarningSignals()
        
        results = ews.analyze(sample_timeseries, method='variance')
        assert 'variance' in results
        assert 'autocorrelation' not in results
        
        results = ews.analyze(sample_timeseries, method='autocorrelation')
        assert 'autocorrelation' in results
        assert 'variance' not in results
    
    def test_interpret_score(self):
        """Test score interpretation."""
        ews = EarlyWarningSignals()
        
        assert 'High risk' in ews._interpret_score(0.8)
        assert 'Moderate risk' in ews._interpret_score(0.5)
        assert 'Low risk' in ews._interpret_score(0.2)
        assert 'No clear' in ews._interpret_score(0.0)
    
    def test_rolling_stat(self, sample_timeseries):
        """Test rolling statistics."""
        ews = EarlyWarningSignals()
        
        # Test rolling variance
        rolling_var = ews._rolling_stat(sample_timeseries, 30, np.var)
        assert len(rolling_var) == len(sample_timeseries) - 30 + 1
        assert np.all(rolling_var >= 0)
        
        # Test rolling mean
        rolling_mean = ews._rolling_stat(sample_timeseries, 30, np.mean)
        assert len(rolling_mean) == len(sample_timeseries) - 30 + 1
    
    def test_rolling_autocorr(self, sample_timeseries):
        """Test rolling autocorrelation."""
        ews = EarlyWarningSignals()
        
        rolling_ac = ews._rolling_autocorr(sample_timeseries, 30)
        assert len(rolling_ac) == len(sample_timeseries) - 30 + 1
        assert np.all(-1 <= rolling_ac) and np.all(rolling_ac <= 1)

class TestTippingPointResult:
    """Test TippingPointResult dataclass."""
    
    def test_creation(self):
        """Test result creation."""
        result = TippingPointResult(
            critical_slowing_down=True,
            warning_level=2,
            variance_trend=0.45,
            autocorrelation_trend=0.38,
            skewness_trend=0.12,
            recovery_rate_trend=-0.15,
            estimated_months=12,
            confidence=0.85,
            metrics={'test_metric': 42},
            metadata={'test': True}
        )
        
        assert result.critical_slowing_down is True
        assert result.warning_level == 2
        assert result.variance_trend == 0.45
        assert result.estimated_months == 12
        assert result.confidence == 0.85
        assert result.metrics['test_metric'] == 42
        assert result.metadata['test'] is True
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = TippingPointResult(
            critical_slowing_down=True,
            warning_level=2,
            variance_trend=0.45,
            autocorrelation_trend=0.38,
            skewness_trend=0.12,
            recovery_rate_trend=-0.15,
            estimated_months=12,
            confidence=0.85
        )
        
        result_dict = result.to_dict()
        
        assert result_dict['critical_slowing_down'] is True
        assert result_dict['warning_level'] == 2
        assert result_dict['variance_trend'] == 0.45
        assert result_dict['estimated_months'] == 12
        assert result_dict['confidence'] == 0.85
