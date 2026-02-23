# 🌿 Welcome to BIOTICA!

## 🎉 Installation Successful!
Your BIOTICA Ecosystem Resilience Framework is now fully operational.

## 📊 Quick Reference
```

Mean IBR: 0.683 | Range: 0.312 - 0.902 | Tested: 8 ecosystems

```

## 🚀 Quick Start Commands
```bash
# Run the complete demo
python3 biotica_demo.py

# Quick functionality test
python3 test_quick.py

# Show statistics
python3 stats.py

# Generate reports
cd reports && ./generate_report.sh daily

# Check alerts
cd reports && source alerts/alert_system.sh && list_active_alerts
```

📁 Project Structure

```
BIOTICA/
├── src/biotica/          # Core modules
├── reports/              # Generated reports
│   ├── daily/
│   ├── weekly/
│   ├── monthly/
│   ├── alerts/
│   └── plots/
├── scripts/              # Utility scripts
└── *.py                  # Demo and test files
```

💡 Example Code

```python
from biotica import BIOTICACore

# Initialize
core = BIOTICACore()

# Analyze ecosystem
params = {'VCA': 0.85, 'MDI': 0.78, 'PTS': 0.82}
result = core.compute_ibr(params)

print(f"IBR: {result['normalized_score']:.3f}")
print(f"Classification: {result['classification']}")
```

📊 Classification Guide

IBR Range Classification
0.88 PRISTINE
0.75 - 0.88 FUNCTIONAL
0.60 - 0.75 IMPAIRED
0.45 - 0.60 DEGRADED
≤ 0.45 COLLAPSED

✅ Next Steps

1. Explore the demo: python3 biotica_demo.py
2. Generate your first report: cd reports && ./generate_report.sh daily
3. Create custom analyses by modifying parameters in src/biotica/equations.py
4. Check alerts: cd reports && source alerts/alert_system.sh

📞 Support

· Author: Samir Baladi
· Email: gitdeeper@gmail.com
· Location: /storage/emulated/0/Download/BIOTICA

---

Thank you for installing BIOTICA! 🌿
