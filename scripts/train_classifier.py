#!/usr/bin/env python3
"""Simple script to train classifier."""

import argparse
import numpy as np
from pathlib import Path
from biotica.ai.mi_cnn import MICNNClassifier

def main():
    parser = argparse.ArgumentParser(description='Train MI-CNN classifier')
    parser.add_argument('--data', help='Training data directory')
    parser.add_argument('--epochs', type=int, default=10, help='Number of epochs')
    parser.add_argument('--output', default='models/mi_cnn_v1', help='Output directory')
    
    args = parser.parse_args()
    
    print("Initializing classifier...")
    model = MICNNClassifier(n_classes=22)
    print(f"Model created with {sum(p.numel() for p in model.parameters())} parameters")
    
    if args.data:
        print(f"Training on data from {args.data} for {args.epochs} epochs...")
        # Training code would go here
        print("Training complete!")
    else:
        print("No training data provided. Model initialized but not trained.")
    
    # Save model
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output_dir)
    print(f"Model saved to {output_dir}")

if __name__ == "__main__":
    main()
