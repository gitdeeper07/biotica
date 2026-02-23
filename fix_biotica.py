#!/usr/bin/env python3
"""إصلاح مشكلة التصنيف في BIOTICA"""

import sys
sys.path.insert(0, 'src')

from biotica import BIOTICACore

class BIOTICAFixed(BIOTICACore):
    """نسخة معدلة من BIOTICACore مع تصحيح التصنيف"""
    
    def compute_ibr(self, parameters):
        """حساب IBR مع تصحيح التصنيف"""
        # حساب المجموع الموزون
        raw_score = 0.0
        total_weight = 0.0
        
        for p, w in self.IBR_WEIGHTS.items():
            if p in parameters:
                raw_score += parameters[p] * w
                total_weight += w
        
        # تطبيع النتيجة إذا لم تكن كل الأوزان مستخدمة
        if total_weight > 0:
            normalized_score = raw_score / total_weight
        else:
            normalized_score = 0
        
        # تصنيف النتيجة (النطاق الصحيح 0-1)
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
            'raw_contributions': {p: parameters.get(p, 0) * w for p, w in self.IBR_WEIGHTS.items() if p in parameters}
        }

# اختبار
fixed = BIOTICAFixed()

# اختبار 1: نظام صحي (يجب أن يكون PRISTINE أو FUNCTIONAL)
params1 = {'VCA': 0.95, 'MDI': 0.92, 'PTS': 0.90, 'HFI': 0.88, 
           'BNC': 0.90, 'SGH': 0.89, 'AES': 0.92, 'TMI': 0.90, 'RRC': 0.88}
r1 = fixed.compute_ibr(params1)
print(f"✅ نظام صحي كامل:")
print(f"   النتيجة الخام: {r1['score']:.3f}")
print(f"   النتيجة الطبيعية: {r1['normalized_score']:.3f}")
print(f"   التصنيف: {r1['classification']}")

# اختبار 2: نظام متوسط
params2 = {'VCA': 0.70, 'MDI': 0.68, 'PTS': 0.65, 'HFI': 0.62}
r2 = fixed.compute_ibr(params2)
print(f"\n🟡 نظام متوسط:")
print(f"   النتيجة الطبيعية: {r2['normalized_score']:.3f}")
print(f"   التصنيف: {r2['classification']}")

# اختبار 3: نظام متدهور
params3 = {'VCA': 0.40, 'MDI': 0.35}
r3 = fixed.compute_ibr(params3)
print(f"\n🔴 نظام متدهور:")
print(f"   النتيجة الطبيعية: {r3['normalized_score']:.3f}")
print(f"   التصنيف: {r3['classification']}")
