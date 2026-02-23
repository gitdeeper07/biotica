#!/usr/bin/env python3
"""BIOTICA - Advanced Analysis Suite"""

import subprocess
import sys

scripts = [
    'radar_dashboard.py',
    'sensitivity_analysis.py', 
    'early_warning.py',
    'intervention_scenarios.py'
]

print("="*60)
print("🌿 BIOTICA - Advanced Analysis Suite")
print("="*60)

for script in scripts:
    print(f"\n🚀 Running {script}...")
    print("-"*40)
    subprocess.run([sys.executable, script])
    
print("\n" + "="*60)
print("✅ All advanced analyses complete!")
print("📁 Check reports/plots/ for visualizations")
print("="*60)
