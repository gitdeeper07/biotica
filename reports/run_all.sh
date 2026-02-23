#!/bin/bash
# Run all reporting tasks

REPORTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPORTS_DIR"

echo "======================================"
echo "BIOTICA Reporting System"
echo "======================================"
echo "Started: $(date)"
echo ""

# Generate reports
echo "📊 Generating daily report..."
./generate_report.sh daily

echo "📈 Generating plots..."
python3 plots/plot_generator.py .

echo "📉 Analyzing trends..."
python3 analyze_trends.py .

echo "📋 Exporting data..."
python3 export_data.py summary . reports/summary_latest.json

# Check alerts
echo ""
echo "🚨 Checking alerts..."
active_alerts=$(find alerts -name "*.json" -exec grep -l '"status": "new"' {} \; | wc -l)
echo "Active alerts: $active_alerts"

if [ $active_alerts -gt 0 ]; then
    echo "⚠️  WARNING: $active_alerts active alerts found"
    
    # Count critical alerts
    critical=$(find alerts -name "*.json" -exec grep -l '"severity": "CRITICAL"' {} \; | wc -l)
    if [ $critical -gt 0 ]; then
        echo "🚨 CRITICAL: $critical critical alerts need immediate attention"
    fi
fi

echo ""
echo "======================================"
echo "Completed: $(date)"
echo "======================================"
