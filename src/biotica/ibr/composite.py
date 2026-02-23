"""IBR Composite Index Calculator
Implements the full IBR calculation pipeline with validation and reporting.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging

from ..equations import BIOTICACore, ParameterResult, IBRClass, BiomeType

logger = logging.getLogger(__name__)

@dataclass
class IBRResult:
    """Complete IBR calculation result."""
    score: float
    classification: IBRClass
    contributions: Dict[str, float]
    uncertainty: float
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    plot_id: Optional[str] = None
    biome: Optional[BiomeType] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'score': self.score,
            'classification': self.classification.value,
            'contributions': self.contributions,
            'uncertainty': self.uncertainty,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'plot_id': self.plot_id,
            'biome': self.biome.value if self.biome else None,
            'warnings': self.warnings,
            'metadata': self.metadata
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

class IBRComposite:
    """
    IBR Composite Index Calculator.
    
    Combines all 9 parameters into a single resilience score
    with full uncertainty propagation and validation.
    """
    
    def __init__(self, core: Optional[BIOTICACore] = None, 
                 plot_id: Optional[str] = None,
                 biome: Optional[BiomeType] = None):
        """
        Initialize IBR composite calculator.
        
        Args:
            core: BIOTICACore instance (creates new if None)
            plot_id: Optional plot identifier
            biome: Optional biome type for normalization
        """
        self.core = core or BIOTICACore(biome=biome)
        self.plot_id = plot_id
        self.biome = biome
        self.parameters = {}
        self.validation_results = {}
        
    def set_parameter(self, name: str, value: float, 
                     uncertainty: Optional[float] = None) -> None:
        """
        Set a single parameter value.
        
        Args:
            name: Parameter name (VCA, MDI, etc.)
            value: Parameter value in [0,1]
            uncertainty: Optional uncertainty value
        """
        if not 0 <= value <= 1:
            raise ValueError(f"Parameter {name} value {value} must be in [0,1]")
        
        self.parameters[name] = {
            'value': value,
            'uncertainty': uncertainty or 0.05
        }
    
    def set_parameters(self, params: Dict[str, float]) -> None:
        """
        Set multiple parameter values.
        
        Args:
            params: Dictionary of parameter names to values
        """
        for name, value in params.items():
            self.set_parameter(name, value)
    
    def set_parameter_result(self, name: str, result: ParameterResult) -> None:
        """
        Set parameter using ParameterResult object.
        
        Args:
            name: Parameter name
            result: ParameterResult from equations module
        """
        self.parameters[name] = {
            'value': result.value,
            'uncertainty': result.uncertainty,
            'metadata': result.metadata
        }
    
    def validate_parameters(self) -> Tuple[bool, List[str]]:
        """
        Validate all required parameters are present and in range.
        
        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        required_params = set(self.core.IBR_WEIGHTS.keys())
        provided_params = set(self.parameters.keys())
        
        warnings = []
        
        # Check for missing parameters
        missing = required_params - provided_params
        if missing:
            warnings.append(f"Missing parameters: {', '.join(missing)}")
        
        # Check for extra parameters
        extra = provided_params - required_params
        if extra:
            warnings.append(f"Extra parameters (will be ignored): {', '.join(extra)}")
        
        # Validate ranges
        for name, data in self.parameters.items():
            if not 0 <= data['value'] <= 1:
                warnings.append(f"Parameter {name} value {data['value']} out of range")
        
        # Check for extreme values
        for name, data in self.parameters.items():
            if data['value'] < 0.2:
                warnings.append(f"Critical low value for {name}: {data['value']:.3f}")
            elif data['value'] > 0.95:
                warnings.append(f"Unusually high value for {name}: {data['value']:.3f}")
        
        is_valid = len([w for w in warnings if 'Missing' in w]) == 0
        return is_valid, warnings
    
    def compute(self, validate: bool = True) -> IBRResult:
        """
        Compute IBR score from loaded parameters.
        
        Args:
            validate: Whether to validate parameters first
        
        Returns:
            IBRResult object with complete results
        """
        if validate:
            is_valid, warnings = self.validate_parameters()
            if not is_valid:
                raise ValueError(f"Parameter validation failed: {warnings}")
        else:
            warnings = []
        
        # Extract values for computation
        param_values = {}
        param_uncertainties = {}
        
        for name, data in self.parameters.items():
            if name in self.core.IBR_WEIGHTS:
                param_values[name] = data['value']
                param_uncertainties[name] = data.get('uncertainty', 0.05)
        
        # Calculate IBR
        ibr_score = 0.0
        contributions = {}
        
        for param, weight in self.core.IBR_WEIGHTS.items():
            if param in param_values:
                contrib = param_values[param] * weight
                ibr_score += contrib
                contributions[param] = contrib
        
        # Apply biome correction if available
        if self.biome:
            ibr_score = self._apply_biome_correction(ibr_score, param_values)
        
        # Calculate uncertainty
        uncertainty_sq = 0.0
        for param, weight in self.core.IBR_WEIGHTS.items():
            if param in param_uncertainties:
                uncertainty_sq += (weight ** 2) * (param_uncertainties[param] ** 2)
        uncertainty = np.sqrt(uncertainty_sq)
        
        # Determine classification
        classification = self.core._classify_ibr(ibr_score)
        
        # Calculate confidence
        confidence = 1.0 - uncertainty
        
        # Add validation warnings
        if ibr_score < 0.45:
            warnings.append("CRITICAL: Ecosystem in COLLAPSED state")
        elif ibr_score < 0.6:
            warnings.append("WARNING: Ecosystem DEGRADED, intervention recommended")
        
        return IBRResult(
            score=float(ibr_score),
            classification=classification,
            contributions=contributions,
            uncertainty=float(uncertainty),
            confidence=float(confidence),
            plot_id=self.plot_id,
            biome=self.biome,
            warnings=warnings,
            metadata={
                'n_parameters': len(param_values),
                'validation_passed': validate,
                'method': 'weighted_sum'
            }
        )
    
    def _apply_biome_correction(self, score: float, 
                                params: Dict[str, float]) -> float:
        """Apply biome-specific corrections."""
        # This would use reference data from paper
        return score
    
    def compute_from_raw(self, raw_data: Dict[str, Any]) -> IBRResult:
        """
        Compute IBR directly from raw field measurements.
        
        Args:
            raw_data: Dictionary containing field measurements
        
        Returns:
            IBRResult object
        """
        # Clear previous parameters
        self.parameters = {}
        
        # Compute VCA if data available
        if all(k in raw_data for k in ['ndvi', 'lai', 'gpp']):
            vca = self.core.compute_vca(
                raw_data['ndvi'],
                raw_data['lai'],
                raw_data['gpp']
            )
            self.set_parameter_result('VCA', vca)
        
        # Compute MDI if data available
        if all(k in raw_data for k in ['shannon', 'chao1', 'otus']):
            mdi = self.core.compute_mdi(
                raw_data['shannon'],
                raw_data['chao1'],
                raw_data['otus']
            )
            self.set_parameter_result('MDI', mdi)
        
        # Compute PTS if data available
        if all(k in raw_data for k in ['greenup_doy', 'historical_greenup']):
            senescence = raw_data.get('senescence_doy', 0)
            pts = self.core.compute_pts(
                raw_data['greenup_doy'],
                senescence,
                raw_data['historical_greenup']
            )
            self.set_parameter_result('PTS', pts)
        
        # Compute HFI if data available
        if all(k in raw_data for k in ['precipitation', 'evapotranspiration',
                                       'soil_moisture', 'runoff']):
            hfi = self.core.compute_hfi(
                raw_data['precipitation'],
                raw_data['evapotranspiration'],
                raw_data['soil_moisture'],
                raw_data['runoff']
            )
            self.set_parameter_result('HFI', hfi)
        
        # Compute BNC if data available
        if all(k in raw_data for k in ['nitrogen', 'phosphorus',
                                       'potassium', 'organic_matter']):
            bnc = self.core.compute_bnc(
                raw_data['nitrogen'],
                raw_data['phosphorus'],
                raw_data['potassium'],
                raw_data['organic_matter']
            )
            self.set_parameter_result('BNC', bnc)
        
        # Compute SGH if data available
        if all(k in raw_data for k in ['heterozygosity', 'allele_richness',
                                       'fst', 'population_size']):
            sgh = self.core.compute_sgh(
                raw_data['heterozygosity'],
                raw_data['allele_richness'],
                raw_data['fst'],
                raw_data['population_size']
            )
            self.set_parameter_result('SGH', sgh)
        
        # Compute AES if data available
        if all(k in raw_data for k in ['human_footprint', 'fragmentation',
                                       'pollution_index', 'distance_to_disturbance']):
            aes = self.core.compute_aes(
                raw_data['human_footprint'],
                raw_data['fragmentation'],
                raw_data['pollution_index'],
                raw_data['distance_to_disturbance']
            )
            self.set_parameter_result('AES', aes)
        
        # Compute TMI if data available
        if all(k in raw_data for k in ['connectance', 'modularity',
                                       'trophic_levels', 'omnivory']):
            tmi = self.core.compute_tmi(
                raw_data['connectance'],
                raw_data['modularity'],
                raw_data['trophic_levels'],
                raw_data['omnivory']
            )
            self.set_parameter_result('TMI', tmi)
        
        # Compute RRC if data available
        if all(k in raw_data for k in ['recovery_rate', 'resilience',
                                       'seed_bank', 'soil_organic_carbon']):
            rrc = self.core.compute_rrc(
                raw_data['recovery_rate'],
                raw_data['resilience'],
                raw_data['seed_bank'],
                raw_data['soil_organic_carbon']
            )
            self.set_parameter_result('RRC', rrc)
        
        # Compute final IBR
        return self.compute(validate=True)

class IBRBatchProcessor:
    """Process multiple plots in batch."""
    
    def __init__(self, core: Optional[BIOTICACore] = None):
        self.core = core or BIOTICACore()
        self.results = []
    
    def process_plot(self, plot_data: Dict[str, Any]) -> IBRResult:
        """Process a single plot."""
        calculator = IBRComposite(core=self.core, 
                                  plot_id=plot_data.get('plot_id'),
                                  biome=plot_data.get('biome'))
        return calculator.compute_from_raw(plot_data)
    
    def process_batch(self, plots: List[Dict[str, Any]]) -> List[IBRResult]:
        """Process multiple plots."""
        self.results = [self.process_plot(plot) for plot in plots]
        return self.results
    
    def summary_statistics(self) -> Dict[str, Any]:
        """Calculate summary statistics for batch results."""
        if not self.results:
            return {}
        
        scores = [r.score for r in self.results]
        
        return {
            'n_plots': len(self.results),
            'mean_score': float(np.mean(scores)),
            'std_score': float(np.std(scores)),
            'min_score': float(np.min(scores)),
            'max_score': float(np.max(scores)),
            'classification_counts': {
                cls.value: sum(1 for r in self.results if r.classification == cls)
                for cls in IBRClass
            }
        }

# Example usage
if __name__ == "__main__":
    # Single plot example
    calculator = IBRComposite(plot_id="AMZ_0042")
    
    # Set parameters manually
    calculator.set_parameters({
        'VCA': 0.85,
        'MDI': 0.78,
        'PTS': 0.82,
        'HFI': 0.71,
        'BNC': 0.68,
        'SGH': 0.73,
        'AES': 0.88,
        'TMI': 0.79,
        'RRC': 0.65
    })
    
    result = calculator.compute()
    print(f"IBR Score: {result.score:.3f}")
    print(f"Classification: {result.classification.value}")
    print(f"Confidence: {result.confidence:.2%}")
    
    # From raw data example
    raw_data = {
        'plot_id': 'SAV_001',
        'ndvi': 0.72,
        'lai': 4.5,
        'gpp': 1500,
        'shannon': 3.2,
        'chao1': 150,
        'otus': 120,
        'greenup_doy': 120,
        'historical_greenup': [115, 118, 122, 119, 116],
        'precipitation': 800,
        'evapotranspiration': 750,
        'soil_moisture': 65,
        'runoff': 50
    }
    
    raw_calc = IBRComposite()
    raw_result = raw_calc.compute_from_raw(raw_data)
    print(f"\nRaw data IBR: {raw_result.score:.3f}")
    print(f"Warnings: {raw_result.warnings}")
