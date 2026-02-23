#!/usr/bin/env python3
"""Analyze trends in BIOTICA data."""

import json
import csv
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import sys

def analyze_daily_trends(stats_file):
    """Analyze daily trends."""
    dates = []
    means = []
    
    with open(stats_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            dates.append(datetime.strptime(row['date'], '%Y-%m-%d'))
            means.append(float(row['mean_ibr']))
    
    if len(means) < 2:
        return {}
    
    # Calculate trends
    changes = [means[i] - means[i-1] for i in range(1, len(means))]
    avg_change = np.mean(changes)
    volatility = np.std(changes)
    
    # Linear trend
    x = np.arange(len(means))
    z = np.polyfit(x, means, 1)
    trend = z[0]
    
    return {
        'avg_daily_change': avg_change,
        'volatility': volatility,
        'linear_trend': trend,
        'current_mean': means[-1],
        'days_analyzed': len(means)
    }

def analyze_alerts(alert_dir):
    """Analyze alert patterns."""
    alerts = []
    for f in Path(alert_dir).glob("*.json"):
        with open(f) as af:
            try:
                alerts.append(json.load(af))
            except:
                continue
    
    if not alerts:
        return {}
    
    severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
    resolved = 0
    new = 0
    
    for alert in alerts:
        if alert['severity'] in severity_counts:
            severity_counts[alert['severity']] += 1
        if alert.get('status') == 'resolved':
            resolved += 1
        else:
            new += 1
    
    return {
        'total_alerts': len(alerts),
        'active_alerts': new,
        'resolved_alerts': resolved,
        'by_severity': severity_counts
    }

def generate_recommendations(trends, alerts):
    """Generate recommendations based on analysis."""
    recs = []
    
    if trends.get('linear_trend', 0) < -0.01:
        recs.append("⚠️  NEGATIVE TREND: Overall IBR declining")
        if trends['linear_trend'] < -0.05:
            recs.append("🚨 CRITICAL: Accelerated decline detected")
    
    if alerts.get('active_alerts', 0) > 10:
        recs.append(f"⚠️  HIGH ALERT COUNT: {alerts['active_alerts']} active alerts")
    
    if alerts.get('by_severity', {}).get('CRITICAL', 0) > 0:
        recs.append(f"🚨 CRITICAL SITES: {alerts['by_severity']['CRITICAL']} sites need immediate action")
    
    if not recs:
        recs.append("✅ System stable - continue monitoring")
    
    return recs

def main():
    data_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("reports")
    
    stats_file = data_dir / "statistics" / "daily_stats.csv"
    if not stats_file.exists():
        print("No statistics file found")
        return
    
    trends = analyze_daily_trends(stats_file)
    alerts = analyze_alerts(data_dir / "alerts")
    recommendations = generate_recommendations(trends, alerts)
    
    print("\n" + "="*50)
    print("BIOTICA TREND ANALYSIS")
    print("="*50)
    
    print(f"\n📊 Current mean IBR: {trends.get('current_mean', 0):.3f}")
    print(f"📈 Daily change: {trends.get('avg_daily_change', 0):+.4f}")
    print(f"📉 Linear trend: {trends.get('linear_trend', 0):+.4f}")
    print(f"📊 Volatility: {trends.get('volatility', 0):.4f}")
    
    print(f"\n🚨 Alert Status:")
    print(f"   Active: {alerts.get('active_alerts', 0)}")
    print(f"   Resolved: {alerts.get('resolved_alerts', 0)}")
    
    print(f"\n💡 Recommendations:")
    for rec in recommendations:
        print(f"   {rec}")
    
    # Save analysis
    output = {
        'timestamp': datetime.now().isoformat(),
        'trends': trends,
        'alerts': alerts,
        'recommendations': recommendations
    }
    
    with open(data_dir / "statistics" / "latest_analysis.json", 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Analysis saved to statistics/latest_analysis.json")

if __name__ == "__main__":
    main()
