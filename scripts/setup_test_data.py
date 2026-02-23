#!/usr/bin/env python3
"""Setup test data directory structure."""

from pathlib import Path
import json
import csv
import numpy as np

def main():
    """Create test data structure."""
    base_dir = Path("tests/fixtures")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample parameters
    params = {
        'VCA': 0.85,
        'MDI': 0.78,
        'PTS': 0.82,
        'HFI': 0.71,
        'BNC': 0.68,
        'SGH': 0.73,
        'AES': 0.88,
        'TMI': 0.79,
        'RRC': 0.65
    }
    
    with open(base_dir / 'sample_params.json', 'w') as f:
        json.dump(params, f, indent=2)
    
    # Create sample timeseries
    dates = [f"2025-{i:02d}-01" for i in range(1, 13)]
    values = np.random.randn(12).cumsum() + 10
    
    with open(base_dir / 'timeseries.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'value'])
        for d, v in zip(dates, values):
            writer.writerow([d, v])
    
    print(f"Test data created in {base_dir}")

if __name__ == "__main__":
    main()
