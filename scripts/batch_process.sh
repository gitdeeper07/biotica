#!/bin/bash
# Batch processing script for BIOTICA

echo "=================================="
echo "BIOTICA Batch Processing"
echo "=================================="

# Configuration
INPUT_DIR=${1:-"data/raw"}
OUTPUT_DIR=${2:-"data/processed/ibr_scores"}
mkdir -p "$OUTPUT_DIR"

# Process all JSON files
count=0
for file in "$INPUT_DIR"/*.json; do
    if [ -f "$file" ]; then
        filename=$(basename "$file" .json)
        echo "Processing $filename..."
        python scripts/compute_ibr.py "$file" --output "$OUTPUT_DIR/${filename}_result.json"
        count=$((count + 1))
    fi
done

echo "=================================="
echo "Processed $count files"
echo "Results saved to $OUTPUT_DIR"
echo "=================================="
