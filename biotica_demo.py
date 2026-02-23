#!/usr/bin/env python3
"""
🌿 BIOTICA - Complete Demo
==========================
Ecosystem Resilience Assessment Framework
"""

import sys
sys.path.insert(0, 'src')
from biotica import BIOTICACore
import numpy as np
from datetime import datetime

def print_header(text):
    """Print header"""
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60)

def analyze_ecosystem(name, params, core):
    """Analyze an ecosystem"""
    result = core.compute_ibr(params)
    
    print(f"\n📊 Analysis: {name}")
    print(f"   IBR: {result['normalized_score']:.3f}")
    print(f"   Classification: {result['classification']}")
    
    if 'contributions' in result:
        print("   Contributions:")
        for p, c in result['contributions'].items():
            print(f"     • {p}: {c:.3f}")
    
    return result

def generate_report(results):
    """Generate final report"""
    print_header("📋 Final Report")
    
    total = len(results)
    classifications = [r['classification'] for r in results]
    
    print(f"\nTotal ecosystems analyzed: {total}")
    print("\nClassification distribution:")
    
    for cls in ['PRISTINE', 'FUNCTIONAL', 'IMPAIRED', 'DEGRADED', 'COLLAPSED']:
        count = classifications.count(cls)
        if count > 0:
            print(f"  • {cls}: {count} ({count/total*100:.1f}%)")
    
    avg_score = np.mean([r['normalized_score'] for r in results])
    print(f"\nAverage IBR: {avg_score:.3f}")

def main():
    print_header("🌿 BIOTICA - Complete Demo")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Initialize core
    core = BIOTICACore()
    
    # Different ecosystem types
    ecosystems = [
        {
            'name': '🏝️ Tropical Rainforest - Amazon',
            'params': {
                'VCA': 0.94, 'MDI': 0.91, 'PTS': 0.89,
                'HFI': 0.87, 'BNC': 0.92, 'SGH': 0.90,
                'AES': 0.88, 'TMI': 0.89, 'RRC': 0.86
            }
        },
        {
            'name': '🌲 Coniferous Forest - Siberia',
            'params': {
                'VCA': 0.82, 'MDI': 0.79, 'PTS': 0.75,
                'HFI': 0.78, 'BNC': 0.80, 'SGH': 0.77,
                'AES': 0.85, 'TMI': 0.76, 'RRC': 0.73
            }
        },
        {
            'name': '🌾 Steppe - Mongolia',
            'params': {
                'VCA': 0.68, 'MDI': 0.65, 'PTS': 0.62,
                'HFI': 0.58, 'BNC': 0.64, 'SGH': 0.61,
                'AES': 0.72, 'TMI': 0.60, 'RRC': 0.59
            }
        },
        {
            'name': '🏜️ Desert - Sahara',
            'params': {
                'VCA': 0.35, 'MDI': 0.32, 'PTS': 0.30,
                'HFI': 0.25, 'BNC': 0.28, 'SGH': 0.31,
                'AES': 0.45, 'TMI': 0.29, 'RRC': 0.22
            }
        },
        {
            'name': '💧 Wetlands - Everglades',
            'params': {
                'VCA': 0.79, 'MDI': 0.84, 'PTS': 0.71,
                'HFI': 0.88, 'BNC': 0.76, 'SGH': 0.73,
                'AES': 0.69, 'TMI': 0.75, 'RRC': 0.77
            }
        },
        {
            'name': '🏔️ Alpine Region - Alps',
            'params': {
                'VCA': 0.58, 'MDI': 0.62, 'PTS': 0.54,
                'HFI': 0.71, 'BNC': 0.55, 'SGH': 0.59,
                'AES': 0.77, 'TMI': 0.57, 'RRC': 0.48
            }
        },
        {
            'name': '🌴 Mangrove - Southeast Asia',
            'params': {
                'VCA': 0.83, 'MDI': 0.81, 'PTS': 0.74,
                'HFI': 0.86, 'BNC': 0.78, 'SGH': 0.72,
                'AES': 0.64, 'TMI': 0.73, 'RRC': 0.76
            }
        },
        {
            'name': '🌿 Temperate Grassland - US Plains',
            'params': {
                'VCA': 0.71, 'MDI': 0.68, 'PTS': 0.66,
                'HFI': 0.59, 'BNC': 0.67, 'SGH': 0.64,
                'AES': 0.73, 'TMI': 0.63, 'RRC': 0.65
            }
        }
    ]
    
    # Analyze all ecosystems
    results = []
    for eco in ecosystems:
        result = analyze_ecosystem(eco['name'], eco['params'], core)
        results.append(result)
    
    # Generate report
    generate_report(results)
    
    print_header("✅ Demo Complete")
    print("BIOTICA is ready for advanced usage!")

if __name__ == "__main__":
    main()
