#!/usr/bin/env python3
"""BIOTICA - Sensitivity Analysis"""

import numpy as np
from biotica import BIOTICACore

core = BIOTICACore()
base_params = {'VCA': 0.80, 'MDI': 0.75, 'PTS': 0.70, 'HFI': 0.72, 
               'BNC': 0.68, 'SGH': 0.71, 'AES': 0.74, 'TMI': 0.69, 'RRC': 0.66}

weights = {'HFI': 0.11, 'RRC': 0.07, 'PTS': 0.12}

print("\n📊 Sensitivity Analysis")
print("="*50)

for param, weight in weights.items():
    print(f"\n🔬 Testing {param} (weight: {weight})")
    variations = np.linspace(0.3, 1.0, 8)
    results = []
    
    for val in variations:
        test_params = base_params.copy()
        test_params[param] = val
        result = core.compute_ibr(test_params)
        results.append(result['normalized_score'])
    
    sensitivity = (max(results) - min(results)) / 0.7
    print(f"   Impact range: {min(results):.3f} → {max(results):.3f}")
    print(f"   Sensitivity: {sensitivity:.3f}")
    
    if sensitivity > 0.25:
        print(f"   ⚠️ High sensitivity - {param} is critical")
