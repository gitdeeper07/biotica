#!/usr/bin/env python3
"""Simple script to compute IBR from parameters file."""

import sys
import json
import argparse
from pathlib import Path
from biotica import BIOTICACore

def main():
    parser = argparse.ArgumentParser(description='Compute IBR from parameters')
    parser.add_argument('input', help='Input JSON file with parameters')
    parser.add_argument('--output', '-o', help='Output file (optional)')
    
    args = parser.parse_args()
    
    # Load parameters
    with open(args.input, 'r') as f:
        params = json.load(f)
    
    # Compute IBR
    core = BIOTICACore()
    result = core.compute_ibr(params)
    
    # Prepare output
    output = {
        'score': result['score'],
        'classification': result['classification'],
        'confidence': result['confidence'],
        'contributions': result['contributions']
    }
    
    # Save or print
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
