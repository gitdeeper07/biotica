"""BIOTICA Mathematical Equations - نسخة محدثة مع تصحيح التصنيف"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

@dataclass
class ParameterResult:
    value: float
    uncertainty: float
    confidence: float
    metadata: dict = None

class BiomeType:
    TROPICAL_FOREST = "tropical_forest"
    TEMPERATE_FOREST = "temperate_forest"
    GRASSLAND = "grassland"
    DESERT = "desert"
    TUNDRA = "tundra"

class IBRClass:
    PRISTINE = "PRISTINE"
    FUNCTIONAL = "FUNCTIONAL"
    IMPAIRED = "IMPAIRED"
    DEGRADED = "DEGRADED"
    COLLAPSED = "COLLAPSED"

class BIOTICACore:
    """المحرك الأساسي لـ BIOTICA - نسخة محدثة"""
    
    IBR_WEIGHTS = {
        'VCA': 0.20, 'MDI': 0.15, 'PTS': 0.12,
        'HFI': 0.11, 'BNC': 0.10, 'SGH': 0.09,
        'AES': 0.08, 'TMI': 0.08, 'RRC': 0.07
    }
    
    def __init__(self, config_path=None, biome=None):
        self.config = {}
        self.biome = biome
        
    def compute_ibr(self, parameters):
        """حساب مؤشر IBR مع تطبيع النتيجة"""
        raw_score = 0.0
        total_weight = 0.0
        contributions = {}
        
        for param, weight in self.IBR_WEIGHTS.items():
            if param in parameters:
                contrib = parameters[param] * weight
                raw_score += contrib
                total_weight += weight
                contributions[param] = contrib
        
        # تطبيع النتيجة
        if total_weight > 0:
            normalized_score = raw_score / total_weight
        else:
            normalized_score = 0
        
        # تصنيف النتيجة
        if normalized_score > 0.88:
            cls = "PRISTINE"
        elif normalized_score > 0.75:
            cls = "FUNCTIONAL"
        elif normalized_score > 0.60:
            cls = "IMPAIRED"
        elif normalized_score > 0.45:
            cls = "DEGRADED"
        else:
            cls = "COLLAPSED"
        
        return {
            'score': raw_score,
            'normalized_score': normalized_score,
            'classification': cls,
            'contributions': contributions,
            'uncertainty': 0.05,
            'confidence': 0.95
        }
    
    def compute_vca(self, ndvi, lai, gpp):
        value = (ndvi + lai/10 + gpp/3000) / 3
        return ParameterResult(value=min(value,1), uncertainty=0.05, confidence=0.95)
    
    def compute_mdi(self, shannon, chao1, otus):
        value = (shannon/5 + min(chao1/200,1) + min(otus/200,1)) / 3
        return ParameterResult(value=min(value,1), uncertainty=0.05, confidence=0.95)
    
    def detect_tipping_point(self, timeseries, window=24):
        if len(timeseries) < 50:
            return {'warning_level': 0, 'message': 'بيانات غير كافية'}
        
        first_half = timeseries[:len(timeseries)//2]
        second_half = timeseries[len(timeseries)//2:]
        
        var1 = np.var(first_half)
        var2 = np.var(second_half)
        
        if var2 > var1 * 1.5:
            warning_level = 2
        elif var2 > var1 * 1.2:
            warning_level = 1
        else:
            warning_level = 0
        
        return {
            'warning_level': warning_level,
            'variance_ratio': float(var2/var1),
            'critical_slowing_down': warning_level >= 2
        }
