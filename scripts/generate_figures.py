#!/usr/bin/env python3
"""Generate figures for publication."""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from biotica import BIOTICACore

def main():
    """Generate sample figures."""
    print("Generating figures...")
    
    # Create figures directory
    fig_dir = Path("paper/figures")
    fig_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate sample IBR distribution
    np.random.seed(42)
    core = BIOTICACore()
    
    scores = []
    for i in range(1000):
        params = {
            'VCA': np.random.normal(0.7, 0.1),
            'MDI': np.random.normal(0.7, 0.1),
            'PTS': np.random.normal(0.7, 0.1),
            'HFI': np.random.normal(0.7, 0.1),
            'BNC': np.random.normal(0.7, 0.1),
            'SGH': np.random.normal(0.7, 0.1),
            'AES': np.random.normal(0.7, 0.1),
            'TMI': np.random.normal(0.7, 0.1),
            'RRC': np.random.normal(0.7, 0.1)
        }
        # Clip to [0,1]
        params = {k: np.clip(v, 0, 1) for k, v in params.items()}
        result = core.compute_ibr(params)
        scores.append(result['score'])
    
    # Figure 1: IBR distribution
    plt.figure(figsize=(10, 6))
    plt.hist(scores, bins=30, edgecolor='black', alpha=0.7)
    plt.axvline(np.mean(scores), color='red', linestyle='--', label=f'Mean: {np.mean(scores):.2f}')
    plt.xlabel('IBR Score')
    plt.ylabel('Frequency')
    plt.title('Distribution of IBR Scores')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(fig_dir / 'fig01_ibr_distribution.png', dpi=300, bbox_inches='tight')
    
    # Figure 2: Parameter contributions
    plt.figure(figsize=(12, 6))
    params_list = list(core.IBR_WEIGHTS.keys())
    weights = list(core.IBR_WEIGHTS.values())
    
    plt.bar(params_list, weights)
    plt.xlabel('Parameter')
    plt.ylabel('Weight')
    plt.title('IBR Parameter Weights')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3, axis='y')
    plt.savefig(fig_dir / 'fig02_parameter_weights.png', dpi=300, bbox_inches='tight')
    
    print(f"Figures saved to {fig_dir}")

if __name__ == "__main__":
    main()
