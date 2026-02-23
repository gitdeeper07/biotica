"""Tipping point detection using critical slowing down indicators."""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
import warnings
import json

try:
    from scipy import stats, signal
    from scipy.ndimage import gaussian_filter
    from scipy.signal import argrelextrema
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    warnings.warn("SciPy not available. Tipping point detection disabled.")

@dataclass
class TippingPointResult:
    """Results from tipping point analysis."""
    critical_slowing_down: bool
    warning_level: int  # 0-3, higher = more warning
    variance_trend: float
    autocorrelation_trend: float
    skewness_trend: float
    recovery_rate_trend: float
    estimated_months: int
    confidence: float
    metrics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'critical_slowing_down': self.critical_slowing_down,
            'warning_level': self.warning_level,
            'variance_trend': self.variance_trend,
            'autocorrelation_trend': self.autocorrelation_trend,
            'skewness_trend': self.skewness_trend,
            'recovery_rate_trend': self.recovery_rate_trend,
            'estimated_months': self.estimated_months,
            'confidence': self.confidence,
            'metrics': self.metrics,
            'metadata': self.metadata
        }

class TippingPointDetector:
    """
    Detect ecosystem tipping points using critical slowing down indicators.
    
    Implements methods from paper Section 5.3:
    - Variance increase (indicator of critical slowing down)
    - Autocorrelation increase (lag-1 autocorrelation)
    - Skewness change (asymmetry in fluctuations)
    - Recovery rate slowing (perturbation experiments)
    
    Reference: Scheffer et al. (2009) Nature, Dakos et al. (2012) PLoS ONE
    """
    
    def __init__(self, 
                 window: int = 24,
                 lag: int = 1,
                 min_data_points: int = 50,
                 significance_level: float = 0.05,
                 detrend: bool = True):
        """
        Initialize tipping point detector.
        
        Args:
            window: Rolling window size for statistics
            lag: Lag for autocorrelation
            min_data_points: Minimum data points required
            significance_level: p-value threshold for significance
            detrend: Remove linear trend before analysis
        """
        self.window = window
        self.lag = lag
        self.min_data_points = min_data_points
        self.significance_level = significance_level
        self.detrend = detrend
        
    def detect(self, 
              timeseries: Union[np.ndarray, List[float]],
              timestamps: Optional[np.ndarray] = None,
              variable_name: str = "IBR") -> TippingPointResult:
        """
        Detect early warning signals in timeseries.
        
        Args:
            timeseries: Time series data
            timestamps: Optional timestamps (for time estimation)
            variable_name: Name of the variable being analyzed
            
        Returns:
            TippingPointResult with detection results
        """
        if not SCIPY_AVAILABLE:
            return self._fallback_result()
        
        # Convert to numpy array
        timeseries = np.asarray(timeseries, dtype=float)
        
        # Remove NaN values
        valid_mask = ~np.isnan(timeseries)
        timeseries = timeseries[valid_mask]
        
        if timestamps is not None:
            timestamps = np.asarray(timestamps)[valid_mask]
        
        if len(timeseries) < self.min_data_points:
            return TippingPointResult(
                critical_slowing_down=False,
                warning_level=0,
                variance_trend=0.0,
                autocorrelation_trend=0.0,
                skewness_trend=0.0,
                recovery_rate_trend=0.0,
                estimated_months=0,
                confidence=0.0,
                metrics={},
                metadata={'error': f'Insufficient data: {len(timeseries)} < {self.min_data_points}'}
            )
        
        # Detrend if requested
        if self.detrend:
            timeseries = self._detrend_series(timeseries)
        
        # Calculate rolling statistics
        n_rolling = len(timeseries) - self.window
        variances = np.zeros(n_rolling)
        autocorrelations = np.zeros(n_rolling)
        skewnesses = np.zeros(n_rolling)
        recovery_rates = np.zeros(n_rolling)
        
        for i in range(n_rolling):
            segment = timeseries[i:i+self.window]
            
            # Variance
            variances[i] = np.var(segment)
            
            # Lag-1 autocorrelation
            if len(segment) > self.lag:
                autocorr = np.corrcoef(segment[:-self.lag], segment[self.lag:])[0,1]
                autocorrelations[i] = autocorr if not np.isnan(autocorr) else 0
            else:
                autocorrelations[i] = 0
            
            # Skewness
            skewnesses[i] = float(stats.skew(segment))
            
            # Recovery rate (from perturbation experiments)
            recovery_rates[i] = self._estimate_recovery_rate(segment)
        
        # Calculate trends using Kendall tau
        x = np.arange(n_rolling)
        
        tau_var, p_var = stats.kendalltau(x, variances)
        tau_ac, p_ac = stats.kendalltau(x, autocorrelations)
        tau_skew, p_skew = stats.kendalltau(x, skewnesses)
        tau_rec, p_rec = stats.kendalltau(x, recovery_rates)
        
        # Determine warning level (0-3)
        warning_level = 0
        indicators = []
        
        # Variance increase (key indicator)
        if tau_var > 0.2 and p_var < self.significance_level:
            warning_level += 1
            indicators.append('variance_increase')
        elif tau_var > 0.1:
            warning_level += 0.5
            indicators.append('variance_increase_trend')
        
        # Autocorrelation increase (key indicator)
        if tau_ac > 0.2 and p_ac < self.significance_level:
            warning_level += 1
            indicators.append('autocorrelation_increase')
        elif tau_ac > 0.1:
            warning_level += 0.5
            indicators.append('autocorrelation_trend')
        
        # Skewness change (supporting indicator)
        if abs(tau_skew) > 0.15 and p_skew < self.significance_level:
            warning_level += 0.5
            indicators.append('skewness_change')
        
        # Recovery rate slowing (if available)
        if tau_rec < -0.15 and p_rec < self.significance_level:
            warning_level += 0.5
            indicators.append('recovery_slowing')
        
        warning_level = int(np.floor(warning_level))
        warning_level = min(warning_level, 3)
        
        # Estimate months to tipping point
        estimated_months = self._estimate_time_to_tipping(
            tau_var, tau_ac, timeseries, timestamps
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            warning_level, p_var, p_ac, len(timeseries)
        )
        
        # Critical slowing down detection
        critical_slowing_down = warning_level >= 2
        
        # Compile metrics
        metrics = {
            'variance': {
                'trend': float(tau_var),
                'p_value': float(p_var),
                'current': float(variances[-1]) if len(variances) > 0 else 0,
                'initial': float(variances[0]) if len(variances) > 0 else 0,
                'ratio': float(variances[-1] / variances[0]) if len(variances) > 0 and variances[0] > 0 else 1
            },
            'autocorrelation': {
                'trend': float(tau_ac),
                'p_value': float(p_ac),
                'current': float(autocorrelations[-1]) if len(autocorrelations) > 0 else 0,
                'initial': float(autocorrelations[0]) if len(autocorrelations) > 0 else 0
            },
            'skewness': {
                'trend': float(tau_skew),
                'p_value': float(p_skew),
                'current': float(skewnesses[-1]) if len(skewnesses) > 0 else 0
            },
            'recovery_rate': {
                'trend': float(tau_rec),
                'p_value': float(p_rec),
                'current': float(recovery_rates[-1]) if len(recovery_rates) > 0 else 0
            },
            'indicators': indicators,
            'n_points': len(timeseries),
            'window_size': self.window
        }
        
        metadata = {
            'variable_name': variable_name,
            'detrended': self.detrend,
            'lag': self.lag,
            'significance_level': self.significance_level
        }
        
        return TippingPointResult(
            critical_slowing_down=critical_slowing_down,
            warning_level=warning_level,
            variance_trend=float(tau_var),
            autocorrelation_trend=float(tau_ac),
            skewness_trend=float(tau_skew),
            recovery_rate_trend=float(tau_rec),
            estimated_months=estimated_months,
            confidence=confidence,
            metrics=metrics,
            metadata=metadata
        )
    
    def _detrend_series(self, timeseries: np.ndarray) -> np.ndarray:
        """Remove linear trend from timeseries."""
        x = np.arange(len(timeseries))
        slope, intercept = np.polyfit(x, timeseries, 1)
        trend = slope * x + intercept
        return timeseries - trend
    
    def _estimate_recovery_rate(self, segment: np.ndarray) -> float:
        """
        Estimate recovery rate from perturbations.
        
        Uses the decay rate of autocorrelation as proxy for recovery rate.
        """
        if len(segment) < 3:
            return 0.0
        
        # Calculate power spectrum
        try:
            fft_vals = np.fft.fft(segment)
            power = np.abs(fft_vals)**2
            freqs = np.fft.fftfreq(len(segment))
            
            # Low frequencies indicate slow recovery
            low_freq_mask = np.abs(freqs) < 0.1
            if low_freq_mask.any():
                low_freq_power = power[low_freq_mask].mean()
                total_power = power.mean()
                recovery_rate = 1 - (low_freq_power / total_power)
                return float(recovery_rate)
        except:
            pass
        
        return 0.5  # Default
    
    def _estimate_time_to_tipping(self, 
                                  tau_var: float,
                                  tau_ac: float,
                                  timeseries: np.ndarray,
                                  timestamps: Optional[np.ndarray]) -> int:
        """
        Estimate months until potential tipping point.
        """
        if timestamps is not None and len(timestamps) > 1:
            # Calculate time step in months
            time_diffs = np.diff(timestamps)
            median_step = np.median(time_diffs)
            
            # Convert to months (assuming days)
            if median_step <= 31:  # Daily data
                months_per_step = 1/30.44
            elif median_step <= 365:  # Monthly data
                months_per_step = 1
            else:  # Annual data
                months_per_step = 12
        else:
            months_per_step = 1  # Assume monthly
        
        # Use trend strength to estimate time
        trend_strength = (abs(tau_var) + abs(tau_ac)) / 2
        
        if trend_strength > 0.3:
            # Strong trend - tipping likely within 1-2 years
            months = 12
        elif trend_strength > 0.2:
            # Moderate trend - tipping within 2-3 years
            months = 24
        elif trend_strength > 0.1:
            # Weak trend - tipping within 3-5 years
            months = 36
        else:
            # No clear trend
            months = 60
        
        return months
    
    def _calculate_confidence(self, 
                             warning_level: int,
                             p_var: float,
                             p_ac: float,
                             n_points: int) -> float:
        """Calculate confidence in detection."""
        confidence = 0.0
        
        # Warning level contribution
        confidence += warning_level * 0.2
        
        # Statistical significance
        if p_var < 0.01:
            confidence += 0.2
        elif p_var < 0.05:
            confidence += 0.1
        
        if p_ac < 0.01:
            confidence += 0.2
        elif p_ac < 0.05:
            confidence += 0.1
        
        # Sample size contribution
        if n_points > 200:
            confidence += 0.2
        elif n_points > 100:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _fallback_result(self) -> TippingPointResult:
        """Return fallback result when SciPy is not available."""
        return TippingPointResult(
            critical_slowing_down=False,
            warning_level=0,
            variance_trend=0.0,
            autocorrelation_trend=0.0,
            skewness_trend=0.0,
            recovery_rate_trend=0.0,
            estimated_months=0,
            confidence=0.0,
            metrics={},
            metadata={'error': 'SciPy not available'}
        )
    
    def detect_multivariate(self, 
                           data_matrix: np.ndarray,
                           variable_names: List[str],
                           timestamps: Optional[np.ndarray] = None) -> Dict[str, TippingPointResult]:
        """
        Detect tipping points in multiple variables.
        
        Args:
            data_matrix: Matrix of shape (n_timesteps, n_variables)
            variable_names: Names of variables
            timestamps: Optional timestamps
            
        Returns:
            Dictionary mapping variable names to results
        """
        results = {}
        
        for i, name in enumerate(variable_names):
            timeseries = data_matrix[:, i]
            results[name] = self.detect(timeseries, timestamps, name)
        
        return results
    
    def spatial_coherence(self, 
                         spatial_data: np.ndarray,
                         lat: np.ndarray,
                         lon: np.ndarray) -> Dict[str, Any]:
        """
        Analyze spatial coherence of tipping points.
        
        Args:
            spatial_data: 3D array (time, lat, lon)
            lat: Latitude array
            lon: Longitude array
            
        Returns:
            Dictionary with spatial tipping point patterns
        """
        n_time, n_lat, n_lon = spatial_data.shape
        
        # Detect tipping points for each pixel
        warning_map = np.zeros((n_lat, n_lon))
        confidence_map = np.zeros((n_lat, n_lon))
        
        for i in range(n_lat):
            for j in range(n_lon):
                timeseries = spatial_data[:, i, j]
                result = self.detect(timeseries)
                warning_map[i, j] = result.warning_level
                confidence_map[i, j] = result.confidence
        
        # Find coherent regions
        from scipy.ndimage import label, find_objects
        
        # Threshold for significant warning
        significant = warning_map >= 2
        labeled, n_regions = label(significant)
        
        regions = []
        for slice_obj in find_objects(labeled):
            if slice_obj is not None:
                region_mask = labeled[slice_obj] > 0
                region_warnings = warning_map[slice_obj][region_mask]
                region_conf = confidence_map[slice_obj][region_mask]
                
                regions.append({
                    'bounds': [int(slice_obj[0].start), int(slice_obj[0].stop),
                              int(slice_obj[1].start), int(slice_obj[1].stop)],
                    'size': int(region_mask.sum()),
                    'mean_warning': float(region_warnings.mean()),
                    'max_warning': float(region_warnings.max()),
                    'mean_confidence': float(region_conf.mean())
                })
        
        return {
            'n_coherent_regions': n_regions,
            'warning_map': warning_map.tolist(),
            'confidence_map': confidence_map.tolist(),
            'regions': regions,
            'total_area_at_risk': int(significant.sum())
        }

class EarlyWarningSignals:
    """
    Comprehensive early warning signals analysis.
    
    Combines multiple indicators for robust tipping point detection.
    """
    
    def __init__(self, detector: Optional[TippingPointDetector] = None):
        self.detector = detector or TippingPointDetector()
        self.results = []
    
    def analyze(self, 
               timeseries: np.ndarray,
               method: str = 'all') -> Dict[str, Any]:
        """
        Comprehensive early warning signals analysis.
        
        Args:
            timeseries: Time series data
            method: 'all', 'variance', 'autocorrelation', 'skewness', 'kurtosis'
            
        Returns:
            Dictionary with all EWS metrics
        """
        results = {}
        
        # Detrend if needed
        x = np.arange(len(timeseries))
        slope, intercept = np.polyfit(x, timeseries, 1)
        detrended = timeseries - (slope * x + intercept)
        
        # Rolling window statistics
        window = min(50, len(timeseries) // 4)
        
        if method in ['all', 'variance']:
            # Variance
            rolling_var = self._rolling_stat(detrended, window, np.var)
            tau_var, p_var = stats.kendalltau(np.arange(len(rolling_var)), rolling_var)
            results['variance'] = {
                'trend': float(tau_var),
                'p_value': float(p_var),
                'values': rolling_var.tolist()
            }
        
        if method in ['all', 'autocorrelation']:
            # Lag-1 autocorrelation
            rolling_ac = self._rolling_autocorr(detrended, window)
            tau_ac, p_ac = stats.kendalltau(np.arange(len(rolling_ac)), rolling_ac)
            results['autocorrelation'] = {
                'trend': float(tau_ac),
                'p_value': float(p_ac),
                'values': rolling_ac.tolist()
            }
        
        if method in ['all', 'skewness']:
            # Skewness
            rolling_skew = self._rolling_stat(detrended, window, stats.skew)
            tau_skew, p_skew = stats.kendalltau(np.arange(len(rolling_skew)), rolling_skew)
            results['skewness'] = {
                'trend': float(tau_skew),
                'p_value': float(p_skew),
                'values': rolling_skew.tolist()
            }
        
        if method in ['all', 'kurtosis']:
            # Kurtosis
            rolling_kurt = self._rolling_stat(detrended, window, stats.kurtosis)
            tau_kurt, p_kurt = stats.kendalltau(np.arange(len(rolling_kurt)), rolling_kurt)
            results['kurtosis'] = {
                'trend': float(tau_kurt),
                'p_value': float(p_kurt),
                'values': rolling_kurt.tolist()
            }
        
        # Combined indicator
        if method == 'all':
            combined_score = (
                (results.get('variance', {}).get('trend', 0) > 0.2) +
                (results.get('autocorrelation', {}).get('trend', 0) > 0.2) +
                (abs(results.get('skewness', {}).get('trend', 0)) > 0.15)
            ) / 3.0
            
            results['combined'] = {
                'score': float(combined_score),
                'interpretation': self._interpret_score(combined_score)
            }
        
        return results
    
    def _rolling_stat(self, data: np.ndarray, window: int, func) -> np.ndarray:
        """Calculate rolling statistic."""
        result = np.zeros(len(data) - window + 1)
        for i in range(len(result)):
            result[i] = func(data[i:i+window])
        return result
    
    def _rolling_autocorr(self, data: np.ndarray, window: int) -> np.ndarray:
        """Calculate rolling autocorrelation."""
        result = np.zeros(len(data) - window + 1)
        for i in range(len(result)):
            segment = data[i:i+window]
            if len(segment) > 1:
                autocorr = np.corrcoef(segment[:-1], segment[1:])[0,1]
                result[i] = autocorr if not np.isnan(autocorr) else 0
        return result
    
    def _interpret_score(self, score: float) -> str:
        """Interpret combined score."""
        if score > 0.7:
            return "High risk - strong early warning signals"
        elif score > 0.4:
            return "Moderate risk - some warning signals detected"
        elif score > 0.1:
            return "Low risk - weak warning signals"
        else:
            return "No clear warning signals"

# Example usage
if __name__ == "__main__":
    # Generate synthetic data with critical slowing down
    np.random.seed(42)
    n_points = 200
    
    # Create timeseries with increasing variance and autocorrelation
    t = np.linspace(0, 10, n_points)
    noise = np.random.randn(n_points) * (1 + 0.1 * t)
    
    # Add autocorrelation
    x = np.zeros(n_points)
    x[0] = noise[0]
    for i in range(1, n_points):
        x[i] = 0.7 * x[i-1] + noise[i] * (1 + 0.02 * i)
    
    # Add trend
    x = x + 0.01 * t
    
    # Initialize detector
    detector = TippingPointDetector(window=30)
    
    # Detect tipping point
    result = detector.detect(x)
    
    print(f"Critical slowing down: {result.critical_slowing_down}")
    print(f"Warning level: {result.warning_level}/3")
    print(f"Variance trend: {result.variance_trend:.3f}")
    print(f"Autocorrelation trend: {result.autocorrelation_trend:.3f}")
    print(f"Estimated months to tipping: {result.estimated_months}")
    print(f"Confidence: {result.confidence:.1%}")
    
    # Comprehensive EWS
    ews = EarlyWarningSignals(detector)
    full_analysis = ews.analyze(x)
    print(f"\nCombined score: {full_analysis.get('combined', {}).get('score', 0):.2f}")
    print(f"Interpretation: {full_analysis.get('combined', {}).get('interpretation', 'N/A')}")
