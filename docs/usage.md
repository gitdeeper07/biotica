
Usage Guide

Basic Usage

```python
from biotica import BIOTICACore

# Initialize
core = BIOTICACore()

# Compute parameters
vca = core.compute_vca(ndvi=0.75, lai=5.2, gpp=1800)

# Compute IBR
params = {'VCA': vca.value, 'MDI': 0.78}
result = core.compute_ibr(params)
```

Advanced Usage

See API reference for detailed documentation.
