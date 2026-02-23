#!/usr/bin/env python3
"""Quick test for BIOTICA"""

import sys
sys.path.insert(0, 'src')
from biotica import BIOTICACore

def test_ecosystem(name, vca, mdi):
    """Test ecosystem with VCA and MDI only"""
    core = BIOTICACore()
    params = {'VCA': vca, 'MDI': mdi}
    result = core.compute_ibr(params)
    print(f"{name:20} IBR={result['normalized_score']:.3f} -> {result['classification']}")

print("\n🔍 Quick Ecosystem Tests")
print("="*50)
test_ecosystem("Pristine Forest", 0.95, 0.92)
test_ecosystem("Healthy Forest", 0.85, 0.82)
test_ecosystem("Moderate Forest", 0.72, 0.70)
test_ecosystem("Degraded Land", 0.55, 0.52)
test_ecosystem("Collapsed Area", 0.35, 0.32)
print("="*50)

# Show available functions
print("\n📚 Available in BIOTICACore:")
methods = [m for m in dir(BIOTICACore) if not m.startswith('_')]
for m in methods[:5]:  # Show first 5
    print(f"  • {m}")
