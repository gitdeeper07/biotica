#!/usr/bin/env python3
"""Validate input data files."""

import sys
import json
import csv
from pathlib import Path

def validate_json(filepath):
    """Validate JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        print(f"✓ {filepath.name}: Valid JSON")
        return True
    except Exception as e:
        print(f"✗ {filepath.name}: Invalid JSON - {e}")
        return False

def validate_csv(filepath):
    """Validate CSV file."""
    try:
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            rows = sum(1 for _ in reader)
        print(f"✓ {filepath.name}: Valid CSV ({len(headers)} columns, {rows} rows)")
        return True
    except Exception as e:
        print(f"✗ {filepath.name}: Invalid CSV - {e}")
        return False

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python validate_data.py <file_or_directory>")
        return
    
    path = Path(sys.argv[1])
    
    if path.is_file():
        if path.suffix == '.json':
            validate_json(path)
        elif path.suffix == '.csv':
            validate_csv(path)
        else:
            print(f"Unknown file type: {path.suffix}")
    
    elif path.is_dir():
        print(f"\nValidating files in {path}:\n")
        json_files = list(path.glob("*.json"))
        csv_files = list(path.glob("*.csv"))
        
        valid = 0
        for f in json_files:
            if validate_json(f):
                valid += 1
        for f in csv_files:
            if validate_csv(f):
                valid += 1
        
        total = len(json_files) + len(csv_files)
        print(f"\nSummary: {valid}/{total} files valid")

if __name__ == "__main__":
    main()
