#!/usr/bin/env python3
"""BIOTICA - Early Warning Time Series"""

import numpy as np
import matplotlib.pyplot as plt
from biotica import BIOTICACore

core = BIOTICACore()

# محاكاة سلسلة زمنية لمدة 24 شهراً
months = np.arange(24)
base_ibr = 0.75
noise = np.random.normal(0, 0.02, 24)
trend = -0.003 * months  # تدهور تدريجي

# نظام صحي مقابل نظام متدهور
healthy = base_ibr + np.random.normal(0, 0.01, 24)
degrading = base_ibr + trend + noise * 1.5

# كشف نقاط التحول
warning_healthy = core.detect_tipping_point(healthy)
warning_degrading = core.detect_tipping_point(degrading)

plt.figure(figsize=(12, 5))

plt.subplot(1,2,1)
plt.plot(months, healthy, 'g-', linewidth=2, label='Stable System')
plt.plot(months, degrading, 'r-', linewidth=2, label='Degrading System')
plt.xlabel('Months')
plt.ylabel('IBR')
plt.title('Time Series Comparison')
plt.legend()
plt.grid(True, alpha=0.3)

plt.subplot(1,2,2)
plt.bar(['Healthy', 'Degrading'], 
        [warning_healthy['warning_level'], warning_degrading['warning_level']],
        color=['green', 'red'])
plt.ylabel('Warning Level (0-3)')
plt.title('Early Warning Signals')

plt.tight_layout()
plt.savefig('reports/plots/early_warning.png', dpi=300)
print(f"⚠️ Degrading system warning level: {warning_degrading['warning_level']}")
