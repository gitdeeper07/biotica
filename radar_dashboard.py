#!/usr/bin/env python3
"""BIOTICA - Comparative Radar Dashboard"""

import numpy as np
import matplotlib.pyplot as plt
from math import pi

# بيانات الأنظمة البيئية
ecosystems = {
    'Amazon': {'VCA': 0.94, 'MDI': 0.91, 'PTS': 0.89, 'HFI': 0.87, 'BNC': 0.92, 'SGH': 0.90, 'AES': 0.88, 'TMI': 0.89, 'RRC': 0.86},
    'Siberia': {'VCA': 0.82, 'MDI': 0.79, 'PTS': 0.75, 'HFI': 0.78, 'BNC': 0.80, 'SGH': 0.77, 'AES': 0.85, 'TMI': 0.76, 'RRC': 0.73},
    'Sahara': {'VCA': 0.35, 'MDI': 0.32, 'PTS': 0.30, 'HFI': 0.25, 'BNC': 0.28, 'SGH': 0.31, 'AES': 0.45, 'TMI': 0.29, 'RRC': 0.22}
}

categories = list(['VCA', 'MDI', 'PTS', 'HFI', 'BNC', 'SGH', 'AES', 'TMI', 'RRC'])
N = len(categories)
angles = [n / float(N) * 2 * pi for n in range(N)]
angles += angles[:1]

fig, axes = plt.subplots(1, 3, figsize=(15, 5), subplot_kw=dict(polar=True))
colors = ['#2E8B57', '#4682B4', '#CD5C5C']

for idx, (name, data) in enumerate(ecosystems.items()):
    values = [data[cat] for cat in categories]
    values += values[:1]
    
    axes[idx].plot(angles, values, 'o-', linewidth=2, color=colors[idx])
    axes[idx].fill(angles, values, alpha=0.25, color=colors[idx])
    axes[idx].set_thetagrids([a * 180/pi for a in angles[:-1]], categories)
    axes[idx].set_ylim(0, 1)
    axes[idx].set_title(f'{name} (IBR: {np.mean(values[:-1]):.3f})', pad=20)
    axes[idx].grid(True)

plt.tight_layout()
plt.savefig('reports/plots/radar_comparison.png', dpi=300, bbox_inches='tight')
print("✅ Radar dashboard saved to reports/plots/radar_comparison.png")
