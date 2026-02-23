#!/usr/bin/env python3
"""BIOTICA - بداية سريعة"""

import sys
sys.path.insert(0, 'src')

from biotica import BIOTICACore
import numpy as np

def main():
    print("\n" + "="*50)
    print("🌿 BIOTICA - نظام تقييم مرونة النظم البيئية")
    print("="*50)
    
    # تهيئة المحرك
    core = BIOTICACore()
    
    print("\n📊 أمثلة على التصنيفات:")
    print("-"*40)
    
    # أمثلة على حالات مختلفة
    examples = [
        {
            'name': '🏝️ غابة استوائية سليمة',
            'params': {
                'VCA': 0.95, 'MDI': 0.92, 'PTS': 0.90,
                'HFI': 0.88, 'BNC': 0.90, 'SGH': 0.89,
                'AES': 0.92, 'TMI': 0.90, 'RRC': 0.88
            }
        },
        {
            'name': '🌳 غابة معتدلة صحية',
            'params': {
                'VCA': 0.82, 'MDI': 0.80, 'PTS': 0.78,
                'HFI': 0.75, 'BNC': 0.77, 'SGH': 0.76
            }
        },
        {
            'name': '🌾 مراعي متوسطة',
            'params': {
                'VCA': 0.68, 'MDI': 0.65, 'PTS': 0.62,
                'HFI': 0.60, 'BNC': 0.63
            }
        },
        {
            'name': '🏜️ منطقة متدهورة',
            'params': {
                'VCA': 0.45, 'MDI': 0.42, 'PTS': 0.40
            }
        },
        {
            'name': '💀 نظام منهار',
            'params': {
                'VCA': 0.25, 'MDI': 0.22
            }
        }
    ]
    
    for ex in examples:
        result = core.compute_ibr(ex['params'])
        print(f"\n{ex['name']}:")
        print(f"  IBR: {result['normalized_score']:.3f}")
        print(f"  التصنيف: {result['classification']}")
    
    print("\n" + "="*50)
    print("📝 كيفية الاستخدام:")
    print("="*50)
    print("""
from biotica import BIOTICACore

# تهيئة المحرك
core = BIOTICACore()

# تعريف المعاملات
params = {
    'VCA': 0.85,  # Vegetative Carbon Absorption
    'MDI': 0.78,  # Microbial Diversity Index
    'PTS': 0.82,  # Phenological Time Shift
    # ... إلخ
}

# حساب IBR
result = core.compute_ibr(params)
print(f"IBR: {result['normalized_score']:.3f}")
print(f"التصنيف: {result['classification']}")
    """)
    
    print("\n" + "="*50)
    print("✅ النظام جاهز للاستخدام!")
    print("="*50)

if __name__ == "__main__":
    main()
