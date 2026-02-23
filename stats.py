#!/usr/bin/env python3
"""Calculate statistics from BIOTICA results"""

import sys
sys.path.insert(0, 'src')
from biotica import BIOTICACore
import numpy as np

core = BIOTICACore()

# Sample data from demo
results = [
    0.902,  # Amazon
    0.788,  # Siberia
    0.638,  # Mongolia
    0.312,  # Sahara
    0.777,  # Everglades
    0.601,  # Alps
    0.777,  # Mangrove
    0.667   # US Plains
]

print("\n📊 BIOTICA Statistics")
print("="*40)
print(f"Mean IBR: {np.mean(results):.3f}")
print(f"Median IBR: {np.median(results):.3f}")
print(f"Std Dev: {np.std(results):.3f}")
print(f"Min IBR: {np.min(results):.3f}")
print(f"Max IBR: {np.max(results):.3f}")
print("="*40)
