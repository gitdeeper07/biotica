#!/usr/bin/env python3
"""مساعدة BIOTICA"""

import sys
sys.path.insert(0, 'src')

try:
    from biotica import BIOTICACore, __version__, __author__
    
    print("\n" + "="*50)
    print("🌿 BIOTICA - مساعدة سريعة")
    print("="*50)
    print(f"الإصدار: {__version__}")
    print(f"المؤلف: {__author__}")
    print("\n📦 الفئات المتاحة:")
    print("  • BIOTICACore   - المحرك الرئيسي")
    print("  • ParameterResult - نتائج المعاملات")
    print("  • BiomeType     - أنواع النظم البيئية")
    print("  • IBRClass      - فئات التصنيف")
    
    print("\n🔧 دوال BIOTICACore:")
    print("  • compute_ibr(parameters) - حساب IBR")
    print("  • compute_vca(ndvi, lai, gpp) - حساب VCA")
    print("  • compute_mdi(shannon, chao1, otus) - حساب MDI")
    
    print("\n📊 مثال:")
    print('  from biotica import BIOTICACore')
    print('  core = BIOTICACore()')
    print('  params = {"VCA": 0.85, "MDI": 0.78}')
    print('  result = core.compute_ibr(params)')
    print('  print(result)')
    
    print("\n⚖️ أوزان IBR:")
    core = BIOTICACore()
    for p, w in core.IBR_WEIGHTS.items():
        print(f"  • {p}: {w}")
    
    print("\n" + "="*50)
    
except ImportError as e:
    print(f"❌ خطأ: {e}")
    print("تأكد من وجود المجلد src/biotica")
