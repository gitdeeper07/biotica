#!/usr/bin/env python3
"""Generate plots from BIOTICA data."""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

def generate_ibr_distribution(data_file, output_dir):
    """Generate IBR distribution histogram."""
    with open(data_file) as f:
        data = json.load(f)
    
    ibr_scores = [p['ibr'] for p in data['plots']]
    
    plt.figure(figsize=(10, 6))
    plt.hist(ibr_scores, bins=20, edgecolor='black', alpha=0.7)
    plt.axvline(data['avg_ibr'], color='red', linestyle='--', 
                label=f"Mean: {data['avg_ibr']:.2f}")
    plt.xlabel('IBR Score')
    plt.ylabel('Frequency')
    plt.title(f"IBR Distribution - {data['date']}")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    output_file = Path(output_dir) / f"ibr_distribution_{data['date']}.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Generated: {output_file}")

def generate_time_series(stats_file, output_dir):
    """Generate time series plot."""
    import csv
    from datetime import datetime
    
    dates = []
    means = []
    
    with open(stats_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            dates.append(datetime.strptime(row['date'], '%Y-%m-%d'))
            means.append(float(row['mean_ibr']))
    
    plt.figure(figsize=(12, 6))
    plt.plot(dates, means, 'b-o', markersize=4)
    plt.fill_between(dates, 
                     [m - 0.1 for m in means], 
                     [m + 0.1 for m in means], 
                     alpha=0.2, color='blue')
    plt.xlabel('Date')
    plt.ylabel('Mean IBR')
    plt.title('IBR Time Series')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    output_file = Path(output_dir) / "ibr_timeseries.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Generated: {output_file}")

def generate_alert_map(alert_dir, output_dir):
    """Generate alert map (simplified)."""
    alerts = []
    for f in Path(alert_dir).glob("*.json"):
        with open(f) as af:
            try:
                alerts.append(json.load(af))
            except:
                continue
    
    if not alerts:
        return
    
    severities = {'CRITICAL': 3, 'HIGH': 2, 'MEDIUM': 1, 'LOW': 0}
    counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
    
    for alert in alerts:
        if alert['severity'] in counts:
            counts[alert['severity']] += 1
    
    plt.figure(figsize=(8, 6))
    bars = plt.bar(counts.keys(), counts.values(), 
                   color=['red', 'orange', 'yellow', 'green'])
    plt.xlabel('Severity')
    plt.ylabel('Count')
    plt.title(f'Active Alerts - {len(alerts)} total')
    
    for bar, count in zip(bars, counts.values()):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                str(count), ha='center', va='bottom')
    
    output_file = Path(output_dir) / "alert_map.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Generated: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: plot_generator.py <data_dir>")
        sys.exit(1)
    
    data_dir = Path(sys.argv[1])
    plots_dir = data_dir / "plots"
    plots_dir.mkdir(exist_ok=True)
    
    # Generate distribution plot from latest JSON
    json_files = list((data_dir / "json_archive").glob("*.json"))
    if json_files:
        latest = max(json_files, key=lambda p: p.stat().st_mtime)
        generate_ibr_distribution(latest, plots_dir)
    
    # Generate time series from stats
    stats_file = data_dir / "statistics" / "daily_stats.csv"
    if stats_file.exists():
        generate_time_series(stats_file, plots_dir)
    
    # Generate alert map
    generate_alert_map(data_dir / "alerts", plots_dir)
