#!/usr/bin/env python3
"""اختبار سريع لـ BIOTICA"""

import sys
sys.path.insert(0, 'src')
from biotica import BIOTICACore

def test_ibr_calculation():
    """اختبار حسابات IBR"""
    core = BIOTICACore()
    
    # قيم اختبارية
    test_params = [
        ({'VCA': 0.9, 'MDI': 0.9}, 0.90, "يجب أن يكون PRISTINE"),
        ({'VCA': 0.8, 'MDI': 0.8}, 0.80, "يجب أن يكون FUNCTIONAL"),
        ({'VCA': 0.7, 'MDI': 0.7}, 0.70, "يجب أن يكون IMPAIRED"),
        ({'VCA': 0.5, 'MDI': 0.5}, 0.50, "يجب أن يكون DEGRADED"),
        ({'VCA': 0.3, 'MDI': 0.3}, 0.30, "يجب أن يكون COLLAPSED")
    ]
    
    print("🔍 اختبار حسابات IBR:")
    print("-" * 40)
    
    for params, expected, desc in test_params:
        result = core.compute_ibr(params)
        norm_score = result['normalized_score']
        classification = result['classification']
        
        print(f"المعاملات: {params}")
        print(f"النتيجة: {norm_score:.3f} -> {classification}")
        print(f"توقع: {desc}")
        
        if abs(norm_score - expected) < 0.01:
            print("✅ صحيح")
        else:
            print(f"⚠️ غير متطابق: {norm_score} != {expected}")
        print()

if __name__ == "__main__":
    test_ibr_calculation()
