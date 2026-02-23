"""Biome classification system and registry."""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import warnings

class BiomeType(Enum):
    """Enumeration of supported biome types."""
    TROPICAL_RAINFOREST = "tropical_rainforest"
    TROPICAL_DRY_FOREST = "tropical_dry_forest"
    TEMPERATE_BROADLEAF = "temperate_broadleaf"
    TEMPERATE_CONIFEROUS = "temperate_coniferous"
    BOREAL_FOREST = "boreal_forest"
    TROPICAL_SAVANNA = "tropical_savanna"
    TEMPERATE_GRASSLAND = "temperate_grassland"
    MEDITERRANEAN = "mediterranean"
    DESERT = "desert"
    TUNDRA = "tundra"
    MANGROVE = "mangrove"
    WETLAND = "wetland"
    MONTANE = "montane"
    CLOUD_FOREST = "cloud_forest"
    ALPINE = "alpine"
    COASTAL = "coastal"
    MARINE = "marine"
    FRESHWATER = "freshwater"
    RIPARIAN = "riparian"
    STEPPE = "steppe"
    SCRUBLAND = "scrubland"
    WOODLAND = "woodland"

@dataclass
class BiomeCharacteristics:
    """Characteristics of a biome type."""
    name: str
    code: str
    climate_zone: str
    mean_temperature: float  # °C
    mean_precipitation: float  # mm/year
    dominant_vegetation: List[str]
    soil_types: List[str]
    biodiversity_index: float  # 0-1
    carbon_storage: float  # Mg C/ha
    reference_ibr: float  # Expected IBR score
    thresholds: Dict[str, Tuple[float, float]]  # Parameter thresholds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'code': self.code,
            'climate_zone': self.climate_zone,
            'mean_temperature': self.mean_temperature,
            'mean_precipitation': self.mean_precipitation,
            'dominant_vegetation': self.dominant_vegetation,
            'soil_types': self.soil_types,
            'biodiversity_index': self.biodiversity_index,
            'carbon_storage': self.carbon_storage,
            'reference_ibr': self.reference_ibr,
            'thresholds': {
                k: [v[0], v[1]] for k, v in self.thresholds.items()
            }
        }

class BiomeRegistry:
    """
    Registry of biome types and their characteristics.
    
    Based on IUCN Global Ecosystem Typology and BIOTICA field data.
    """
    
    # Biome characteristics from paper Supplementary Table S3
    BIOME_DATA = {
        BiomeType.TROPICAL_RAINFOREST: {
            'code': 'TRF',
            'climate_zone': 'tropical',
            'mean_temperature': 26.5,
            'mean_precipitation': 2200,
            'dominant_vegetation': ['evergreen_broadleaf', 'lianas', 'epiphytes'],
            'soil_types': ['oxisols', 'ultisols'],
            'biodiversity_index': 0.95,
            'carbon_storage': 250,
            'reference_ibr': 0.88,
            'thresholds': {
                'VCA': (0.75, 0.95),
                'MDI': (0.80, 0.98),
                'PTS': (0.70, 0.92),
                'HFI': (0.65, 0.88),
                'BNC': (0.72, 0.94),
                'SGH': (0.68, 0.90),
                'AES': (0.55, 0.92),
                'TMI': (0.65, 0.91),
                'RRC': (0.50, 0.88)
            }
        },
        BiomeType.TEMPERATE_BROADLEAF: {
            'code': 'TBF',
            'climate_zone': 'temperate',
            'mean_temperature': 12.0,
            'mean_precipitation': 950,
            'dominant_vegetation': ['deciduous_broadleaf', 'shrubs'],
            'soil_types': ['alfisols', 'ineeptisols'],
            'biodiversity_index': 0.75,
            'carbon_storage': 150,
            'reference_ibr': 0.80,
            'thresholds': {
                'VCA': (0.65, 0.88),
                'MDI': (0.70, 0.92),
                'PTS': (0.60, 0.85),
                'HFI': (0.62, 0.86),
                'BNC': (0.68, 0.90),
                'SGH': (0.63, 0.87),
                'AES': (0.48, 0.88),
                'TMI': (0.60, 0.86),
                'RRC': (0.45, 0.84)
            }
        },
        BiomeType.TEMPERATE_CONIFEROUS: {
            'code': 'TCF',
            'climate_zone': 'temperate',
            'mean_temperature': 8.5,
            'mean_precipitation': 850,
            'dominant_vegetation': ['coniferous', 'evergreen_needleleaf'],
            'soil_types': ['spodosols', 'ineeptisols'],
            'biodiversity_index': 0.65,
            'carbon_storage': 180,
            'reference_ibr': 0.78,
            'thresholds': {
                'VCA': (0.60, 0.85),
                'MDI': (0.65, 0.88),
                'PTS': (0.55, 0.82),
                'HFI': (0.58, 0.84),
                'BNC': (0.62, 0.86),
                'SGH': (0.58, 0.83),
                'AES': (0.45, 0.85),
                'TMI': (0.55, 0.82),
                'RRC': (0.42, 0.80)
            }
        },
        BiomeType.BOREAL_FOREST: {
            'code': 'BOR',
            'climate_zone': 'boreal',
            'mean_temperature': 2.0,
            'mean_precipitation': 500,
            'dominant_vegetation': ['coniferous', 'deciduous', 'mosses'],
            'soil_types': ['spodosols', 'ineeptisols', 'histosols'],
            'biodiversity_index': 0.55,
            'carbon_storage': 120,
            'reference_ibr': 0.72,
            'thresholds': {
                'VCA': (0.50, 0.80),
                'MDI': (0.55, 0.82),
                'PTS': (0.45, 0.75),
                'HFI': (0.52, 0.80),
                'BNC': (0.52, 0.78),
                'SGH': (0.48, 0.75),
                'AES': (0.60, 0.90),
                'TMI': (0.45, 0.72),
                'RRC': (0.35, 0.70)
            }
        },
        BiomeType.TROPICAL_SAVANNA: {
            'code': 'SAV',
            'climate_zone': 'tropical',
            'mean_temperature': 24.0,
            'mean_precipitation': 800,
            'dominant_vegetation': ['grasses', 'scattered_trees', 'shrubs'],
            'soil_types': ['ineeptisols', 'alfisols'],
            'biodiversity_index': 0.70,
            'carbon_storage': 80,
            'reference_ibr': 0.75,
            'thresholds': {
                'VCA': (0.50, 0.82),
                'MDI': (0.60, 0.88),
                'PTS': (0.55, 0.80),
                'HFI': (0.48, 0.78),
                'BNC': (0.55, 0.82),
                'SGH': (0.52, 0.80),
                'AES': (0.45, 0.85),
                'TMI': (0.48, 0.75),
                'RRC': (0.48, 0.82)
            }
        },
        BiomeType.TEMPERATE_GRASSLAND: {
            'code': 'GRS',
            'climate_zone': 'temperate',
            'mean_temperature': 10.0,
            'mean_precipitation': 600,
            'dominant_vegetation': ['grasses', 'forbs'],
            'soil_types': ['mollisols'],
            'biodiversity_index': 0.60,
            'carbon_storage': 70,
            'reference_ibr': 0.72,
            'thresholds': {
                'VCA': (0.45, 0.78),
                'MDI': (0.55, 0.84),
                'PTS': (0.50, 0.78),
                'HFI': (0.45, 0.75),
                'BNC': (0.50, 0.80),
                'SGH': (0.48, 0.78),
                'AES': (0.42, 0.82),
                'TMI': (0.45, 0.72),
                'RRC': (0.45, 0.80)
            }
        },
        BiomeType.MEDITERRANEAN: {
            'code': 'MED',
            'climate_zone': 'mediterranean',
            'mean_temperature': 16.0,
            'mean_precipitation': 550,
            'dominant_vegetation': ['sclerophyll_shrubs', 'evergreen_trees'],
            'soil_types': ['ineeptisols', 'alfisols'],
            'biodiversity_index': 0.65,
            'carbon_storage': 60,
            'reference_ibr': 0.70,
            'thresholds': {
                'VCA': (0.40, 0.75),
                'MDI': (0.50, 0.80),
                'PTS': (0.45, 0.75),
                'HFI': (0.35, 0.70),
                'BNC': (0.45, 0.75),
                'SGH': (0.42, 0.72),
                'AES': (0.35, 0.78),
                'TMI': (0.40, 0.68),
                'RRC': (0.40, 0.75)
            }
        },
        BiomeType.DESERT: {
            'code': 'DES',
            'climate_zone': 'arid',
            'mean_temperature': 20.0,
            'mean_precipitation': 150,
            'dominant_vegetation': ['xerophytes', 'succulents', 'shrubs'],
            'soil_types': ['aridisols', 'entisols'],
            'biodiversity_index': 0.30,
            'carbon_storage': 20,
            'reference_ibr': 0.55,
            'thresholds': {
                'VCA': (0.20, 0.60),
                'MDI': (0.30, 0.65),
                'PTS': (0.30, 0.65),
                'HFI': (0.15, 0.50),
                'BNC': (0.25, 0.60),
                'SGH': (0.25, 0.60),
                'AES': (0.40, 0.85),
                'TMI': (0.25, 0.55),
                'RRC': (0.25, 0.60)
            }
        },
        BiomeType.TUNDRA: {
            'code': 'TUN',
            'climate_zone': 'polar',
            'mean_temperature': -5.0,
            'mean_precipitation': 300,
            'dominant_vegetation': ['mosses', 'lichens', 'dwarf_shrubs'],
            'soil_types': ['ineeptisols', 'histosols', 'gelisols'],
            'biodiversity_index': 0.35,
            'carbon_storage': 50,
            'reference_ibr': 0.60,
            'thresholds': {
                'VCA': (0.30, 0.65),
                'MDI': (0.35, 0.70),
                'PTS': (0.25, 0.60),
                'HFI': (0.35, 0.70),
                'BNC': (0.30, 0.65),
                'SGH': (0.28, 0.62),
                'AES': (0.50, 0.90),
                'TMI': (0.30, 0.62),
                'RRC': (0.20, 0.55)
            }
        },
        BiomeType.MANGROVE: {
            'code': 'MAN',
            'climate_zone': 'tropical',
            'mean_temperature': 25.0,
            'mean_precipitation': 1800,
            'dominant_vegetation': ['mangroves', 'halophytes'],
            'soil_types': ['ineeptisols', 'entisols'],
            'biodiversity_index': 0.60,
            'carbon_storage': 300,
            'reference_ibr': 0.75,
            'thresholds': {
                'VCA': (0.60, 0.88),
                'MDI': (0.65, 0.90),
                'PTS': (0.55, 0.82),
                'HFI': (0.70, 0.95),
                'BNC': (0.60, 0.88),
                'SGH': (0.50, 0.80),
                'AES': (0.30, 0.75),
                'TMI': (0.55, 0.82),
                'RRC': (0.55, 0.85)
            }
        },
        BiomeType.WETLAND: {
            'code': 'WET',
            'climate_zone': 'variable',
            'mean_temperature': 15.0,
            'mean_precipitation': 1000,
            'dominant_vegetation': ['hydrophytes', 'sedges', 'reeds'],
            'soil_types': ['histosols', 'ineeptisols'],
            'biodiversity_index': 0.65,
            'carbon_storage': 200,
            'reference_ibr': 0.70,
            'thresholds': {
                'VCA': (0.50, 0.82),
                'MDI': (0.60, 0.88),
                'PTS': (0.50, 0.80),
                'HFI': (0.65, 0.92),
                'BNC': (0.55, 0.84),
                'SGH': (0.45, 0.75),
                'AES': (0.35, 0.78),
                'TMI': (0.50, 0.78),
                'RRC': (0.50, 0.82)
            }
        },
        BiomeType.MONTANE: {
            'code': 'MON',
            'climate_zone': 'montane',
            'mean_temperature': 10.0,
            'mean_precipitation': 1200,
            'dominant_vegetation': ['mixed_forest', 'cloud_forest'],
            'soil_types': ['ineeptisols', 'andisols'],
            'biodiversity_index': 0.70,
            'carbon_storage': 180,
            'reference_ibr': 0.78,
            'thresholds': {
                'VCA': (0.60, 0.88),
                'MDI': (0.65, 0.90),
                'PTS': (0.55, 0.85),
                'HFI': (0.60, 0.88),
                'BNC': (0.60, 0.86),
                'SGH': (0.55, 0.82),
                'AES': (0.40, 0.82),
                'TMI': (0.55, 0.82),
                'RRC': (0.45, 0.80)
            }
        }
    }
    
    def __init__(self):
        """Initialize biome registry."""
        self.biomes = {}
        self._load_biomes()
    
    def _load_biomes(self):
        """Load biome data."""
        for biome_type, data in self.BIOME_DATA.items():
            characteristics = BiomeCharacteristics(
                name=biome_type.value,
                code=data['code'],
                climate_zone=data['climate_zone'],
                mean_temperature=data['mean_temperature'],
                mean_precipitation=data['mean_precipitation'],
                dominant_vegetation=data['dominant_vegetation'],
                soil_types=data['soil_types'],
                biodiversity_index=data['biodiversity_index'],
                carbon_storage=data['carbon_storage'],
                reference_ibr=data['reference_ibr'],
                thresholds=data['thresholds']
            )
            self.biomes[biome_type] = characteristics
    
    def get_biome(self, biome_type: Union[BiomeType, str]) -> Optional[BiomeCharacteristics]:
        """Get biome characteristics by type."""
        if isinstance(biome_type, str):
            try:
                biome_type = BiomeType(biome_type)
            except ValueError:
                return None
        
        return self.biomes.get(biome_type)
    
    def list_biomes(self) -> List[str]:
        """List all available biomes."""
        return [b.value for b in self.biomes.keys()]
    
    def classify_by_coordinates(self, 
                               lat: float, 
                               lon: float,
                               elevation: Optional[float] = None) -> List[Tuple[BiomeType, float]]:
        """
        Classify biome based on coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            elevation: Elevation in meters
            
        Returns:
            List of (biome_type, confidence) tuples
        """
        # Simple climate-based classification
        # This is a simplified version - would use actual climate data in practice
        
        results = []
        
        # Temperature zones
        if abs(lat) < 23.5:
            # Tropical
            if elevation and elevation > 1500:
                results.append((BiomeType.MONTANE, 0.7))
                results.append((BiomeType.TROPICAL_RAINFOREST, 0.3))
            elif 23.5 <= abs(lat) < 35:
                # Subtropical
                results.append((BiomeType.TROPICAL_SAVANNA, 0.6))
                results.append((BiomeType.MEDITERRANEAN, 0.4))
            else:
                results.append((BiomeType.TROPICAL_RAINFOREST, 0.8))
                results.append((BiomeType.TROPICAL_SAVANNA, 0.2))
        
        elif 23.5 <= abs(lat) < 45:
            # Temperate
            if lon and -10 < lon < 40:
                # Europe/Mediterranean
                results.append((BiomeType.MEDITERRANEAN, 0.7))
                results.append((BiomeType.TEMPERATE_BROADLEAF, 0.3))
            else:
                results.append((BiomeType.TEMPERATE_BROADLEAF, 0.5))
                results.append((BiomeType.TEMPERATE_CONIFEROUS, 0.3))
                results.append((BiomeType.TEMPERATE_GRASSLAND, 0.2))
        
        elif 45 <= abs(lat) < 60:
            # Cool temperate
            results.append((BiomeType.TEMPERATE_CONIFEROUS, 0.6))
            results.append((BiomeType.BOREAL_FOREST, 0.4))
        
        else:
            # Boreal/Arctic
            results.append((BiomeType.BOREAL_FOREST, 0.5))
            results.append((BiomeType.TUNDRA, 0.5))
        
        return results
    
    def get_thresholds(self, 
                      biome_type: BiomeType,
                      parameter: str) -> Tuple[float, float]:
        """Get parameter thresholds for biome."""
        biome = self.get_biome(biome_type)
        if biome and parameter in biome.thresholds:
            return biome.thresholds[parameter]
        return (0.0, 1.0)  # Default full range
    
    def normalize_parameter(self,
                           biome_type: BiomeType,
                           parameter: str,
                           value: float) -> float:
        """
        Normalize parameter value using biome-specific thresholds.
        
        Args:
            biome_type: Biome type
            parameter: Parameter name
            value: Raw parameter value
            
        Returns:
            Normalized value in [0, 1]
        """
        low, high = self.get_thresholds(biome_type, parameter)
        
        if high <= low:
            return np.clip(value, 0, 1)
        
        normalized = (value - low) / (high - low)
        return float(np.clip(normalized, 0, 1))
    
    def calculate_biome_similarity(self,
                                  biome1: BiomeType,
                                  biome2: BiomeType) -> float:
        """Calculate similarity between two biomes."""
        chars1 = self.get_biome(biome1)
        chars2 = self.get_biome(biome2)
        
        if not chars1 or not chars2:
            return 0.0
        
        # Climate similarity
        temp_diff = abs(chars1.mean_temperature - chars2.mean_temperature) / 30
        precip_diff = abs(chars1.mean_precipitation - chars2.mean_precipitation) / 3000
        
        climate_sim = 1 - (0.5 * temp_diff + 0.5 * precip_diff)
        
        # Vegetation similarity
        veg_intersection = len(set(chars1.dominant_vegetation) & set(chars2.dominant_vegetation))
        veg_union = len(set(chars1.dominant_vegetation) | set(chars2.dominant_vegetation))
        veg_sim = veg_intersection / veg_union if veg_union > 0 else 0
        
        # IBR reference similarity
        ibr_sim = 1 - abs(chars1.reference_ibr - chars2.reference_ibr)
        
        # Combined similarity
        similarity = 0.4 * climate_sim + 0.4 * veg_sim + 0.2 * ibr_sim
        
        return float(np.clip(similarity, 0, 1))
    
    def find_similar_biomes(self,
                           biome_type: BiomeType,
                           n_results: int = 5) -> List[Tuple[BiomeType, float]]:
        """Find most similar biomes."""
        similarities = []
        
        for other in self.biomes.keys():
            if other != biome_type:
                sim = self.calculate_biome_similarity(biome_type, other)
                similarities.append((other, sim))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:n_results]
    
    def save_registry(self, filepath: str):
        """Save biome registry to JSON."""
        data = {
            biome_type.value: chars.to_dict()
            for biome_type, chars in self.biomes.items()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_registry(self, filepath: str):
        """Load biome registry from JSON."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        for biome_name, chars_data in data.items():
            try:
                biome_type = BiomeType(biome_name)
                characteristics = BiomeCharacteristics(
                    name=chars_data['name'],
                    code=chars_data['code'],
                    climate_zone=chars_data['climate_zone'],
                    mean_temperature=chars_data['mean_temperature'],
                    mean_precipitation=chars_data['mean_precipitation'],
                    dominant_vegetation=chars_data['dominant_vegetation'],
                    soil_types=chars_data['soil_types'],
                    biodiversity_index=chars_data['biodiversity_index'],
                    carbon_storage=chars_data['carbon_storage'],
                    reference_ibr=chars_data['reference_ibr'],
                    thresholds={
                        k: (v[0], v[1]) for k, v in chars_data['thresholds'].items()
                    }
                )
                self.biomes[biome_type] = characteristics
            except ValueError:
                warnings.warn(f"Unknown biome type: {biome_name}")

class TransitionZoneResolver:
    """Resolve biome transition zones."""
    
    def __init__(self, registry: BiomeRegistry):
        self.registry = registry
    
    def resolve(self,
               biome_scores: Dict[BiomeType, float],
               threshold: float = 0.2) -> Tuple[BiomeType, float]:
        """
        Resolve transition zone classification.
        
        Args:
            biome_scores: Dictionary mapping biomes to confidence scores
            threshold: Minimum score difference for clear classification
            
        Returns:
            (biome_type, confidence) tuple
        """
        if not biome_scores:
            return (None, 0.0)
        
        # Sort by score
        sorted_biomes = sorted(biome_scores.items(), key=lambda x: x[1], reverse=True)
        
        top_biome, top_score = sorted_biomes[0]
        
        if len(sorted_biomes) > 1:
            second_score = sorted_biomes[1][1]
            
            # Check if clearly in top biome
            if top_score - second_score > threshold:
                return (top_biome, top_score)
            else:
                # Transition zone - return weighted combination
                return self._transition_classification(sorted_biomes)
        else:
            return (top_biome, top_score)
    
    def _transition_classification(self,
                                  biome_scores: List[Tuple[BiomeType, float]],
                                  n_top: int = 3) -> Tuple[BiomeType, float]:
        """Handle transition zone classification."""
        # Take top N biomes
        top_biomes = biome_scores[:n_top]
        
        # Normalize scores
        total = sum(score for _, score in top_biomes)
        if total == 0:
            return (top_biomes[0][0], 0.0)
        
        normalized = [(b, s/total) for b, s in top_biomes]
        
        # Calculate similarity-weighted biome
        # Return the one with highest similarity-weighted score
        weighted_scores = {}
        
        for biome1, score1 in normalized:
            weighted_scores[biome1] = score1
            
            for biome2, score2 in normalized:
                if biome1 != biome2:
                    similarity = self.registry.calculate_biome_similarity(biome1, biome2)
                    weighted_scores[biome1] += 0.5 * similarity * score2
        
        # Get best biome
        best_biome = max(weighted_scores.items(), key=lambda x: x[1])[0]
        
        # Calculate confidence (lower in transitions)
        confidence = weighted_scores[best_biome] * 0.7  # Reduced confidence
        
        return (best_biome, confidence)

# Example usage
if __name__ == "__main__":
    # Initialize registry
    registry = BiomeRegistry()
    
    print(f"Loaded {len(registry.list_biomes())} biomes")
    print(f"First 5 biomes: {registry.list_biomes()[:5]}")
    
    # Get tropical rainforest characteristics
    biome = registry.get_biome(BiomeType.TROPICAL_RAINFOREST)
    if biome:
        print(f"\nTropical Rainforest:")
        print(f"  Temperature: {biome.mean_temperature}°C")
        print(f"  Precipitation: {biome.mean_precipitation} mm")
        print(f"  Carbon storage: {biome.carbon_storage} Mg C/ha")
        print(f"  Reference IBR: {biome.reference_ibr}")
    
    # Find similar biomes
    similar = registry.find_similar_biomes(BiomeType.TROPICAL_RAINFOREST)
    print(f"\nSimilar biomes to Tropical Rainforest:")
    for biome, sim in similar:
        print(f"  {biome.value}: {sim:.2f}")
    
    # Normalize parameter
    vca = 0.82
    normalized = registry.normalize_parameter(
        BiomeType.TROPICAL_RAINFOREST, 'VCA', vca
    )
    print(f"\nVCA {vca} normalized to {normalized:.2f}")
