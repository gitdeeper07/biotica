# BIOTICA Documentation

Welcome to the BIOTICA documentation.

## Overview

BIOTICA is a framework for ecosystem resilience assessment.

## Quick Start

```python
from biotica import BIOTICACore

core = BIOTICACore()
params = {'VCA': 0.85, 'MDI': 0.78}
result = core.compute_ibr(params)
print(result)
```

Installation

```bash
pip install biotica
```

