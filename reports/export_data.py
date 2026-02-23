#!/usr/bin/env python3
"""Export BIOTICA data to various formats."""

import json
import csv
import sys
from pathlib import Path
from datetime import datetime

def export_to_csv(json_file, output_file):
    """Export JSON data to CSV."""
    with open(json_file) as f:
        data = json.load(f)
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['plot_id', 'ibr_score', 'classification'])
        
        for plot in data.get('plots', []):
            writer.writerow([
                plot['id'],
                plot['ibr'],
                plot['class']
            ])
    
    print(f"Exported {len(data.get('plots', []))} plots to {output_file}")

def export_alerts_to_csv(alert_dir, output_file):
    """Export alerts to CSV."""
    alerts = []
    for f in Path(alert_dir).glob("*.json"):
        with open(f) as af:
            try:
                alerts.append(json.load(af))
            except:
                continue
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'severity', 'plot_id', 'ibr_score', 'status'])
        
        for alert in alerts:
            writer.writerow([
                alert.get('timestamp', ''),
                alert.get('severity', ''),
                alert.get('plot_id', ''),
                alert.get('ibr_score', ''),
                alert.get('status', '')
            ])
    
    print(f"Exported {len(alerts)} alerts to {output_file}")

def export_summary(data_dir, output_file):
    """Export summary statistics."""
    stats_file = data_dir / "statistics" / "daily_stats.csv"
    if not stats_file.exists():
        print("No statistics file found")
        return
    
    import csv
    summary = {
        'export_date': datetime.now().isoformat(),
        'daily_stats': []
    }
    
    with open(stats_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            summary['daily_stats'].append(row)
    
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Summary exported to {output_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: export_data.py <command> [args]")
        print("Commands:")
        print("  csv <json_file> <output.csv>")
        print("  alerts <alert_dir> <output.csv>")
        print("  summary <data_dir> <output.json>")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "csv" and len(sys.argv) == 4:
        export_to_csv(sys.argv[2], sys.argv[3])
    elif cmd == "alerts" and len(sys.argv) == 4:
        export_alerts_to_csv(sys.argv[2], sys.argv[3])
    elif cmd == "summary" and len(sys.argv) == 4:
        export_summary(Path(sys.argv[2]), sys.argv[3])
    else:
        print("Invalid command or arguments")

if __name__ == "__main__":
    main()
