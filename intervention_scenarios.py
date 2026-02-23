#!/usr/bin/env python3
"""BIOTICA - Intervention Scenario Simulator"""

import numpy as np
from biotica import BIOTICACore
import matplotlib.pyplot as plt

core = BIOTICACore()

# نظام متضرر (IMPAIRED)
impaired_system = {
    'VCA': 0.68, 'MDI': 0.65, 'PTS': 0.62,
    'HFI': 0.58, 'BNC': 0.64, 'SGH': 0.61,
    'AES': 0.72, 'TMI': 0.60, 'RRC': 0.59
}

# سيناريوهات التدخل
scenarios = {
    'Baseline': impaired_system.copy(),
    '🚰 Improve HFI': {**impaired_system, 'HFI': 0.75},
    '🌱 Boost RRC': {**impaired_system, 'RRC': 0.75},
    '🛡️ Protect AES': {**impaired_system, 'AES': 0.85},
    '🔧 Combined': {**impaired_system, 'HFI': 0.75, 'RRC': 0.75, 'AES': 0.85}
}

results = {}
for name, params in scenarios.items():
    result = core.compute_ibr(params)
    results[name] = result['normalized_score']
    print(f"{name}: {result['normalized_score']:.3f} → {result['classification']}")

# تصور النتائج
plt.figure(figsize=(10, 6))
bars = plt.bar(results.keys(), results.values(), 
               color=['gray', 'blue', 'green', 'orange', 'red'])
plt.axhline(y=0.60, color='red', linestyle='--', label='Collapse Threshold')
plt.axhline(y=0.75, color='green', linestyle='--', label='Recovery Target')
plt.ylabel('IBR Score')
plt.title('Intervention Scenarios Impact')
plt.xticks(rotation=45)
plt.legend()
plt.grid(True, alpha=0.3)

for bar, val in zip(bars, results.values()):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
             f'{val:.3f}', ha='center', va='bottom')

plt.tight_layout()
plt.savefig('reports/plots/interventions.png', dpi=300)
print("\n✅ Best intervention: " + max(results, key=results.get))
