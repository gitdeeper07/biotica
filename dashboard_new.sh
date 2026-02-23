#!/bin/bash
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              🌿 BIOTICA - System Dashboard                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

LATEST_JSON=$(ls -t reports/daily/analysis_*.json 2>/dev/null | head -1)

if [ -f "$LATEST_JSON" ]; then
    echo "📊 Latest Analysis: $(basename $LATEST_JSON)"
    echo "────────────────────────────────────────────"
    
    TOTAL=$(grep -o '"total_plots": [0-9]*' "$LATEST_JSON" | cut -d' ' -f2)
    AVG=$(grep -o '"average_ibr": [0-9.]*' "$LATEST_JSON" | cut -d' ' -f2)
    RISK=$(grep -o '"risk_level": "[^"]*"' "$LATEST_JSON" | cut -d'"' -f4)
    
    echo "📈 System Status:"
    echo "  • Total Plots: $TOTAL"
    echo "  • Average IBR: $AVG"
    echo "  • Risk Level: $RISK"
    echo ""
    
    echo "📋 Classification:"
    grep -A6 '"classification"' "$LATEST_JSON" | grep -E '"(pristine|functional|impaired|degraded|collapsed)"' | while read line; do
        name=$(echo $line | cut -d'"' -f2)
        value=$(echo $line | cut -d':' -f2 | tr -d ' ,')
        printf "  • %-10s : %s\n" "${name^^}" "$value"
    done
    echo ""
    
    echo "⚠️ Active Alerts:"
    grep -A3 '"alerts_list"' "$LATEST_JSON" | grep -E '"plot":' | head -3 | while read line; do
        plot=$(echo $line | cut -d'"' -f4)
        echo "  • $plot"
    done
else
    echo "❌ No analysis files found"
fi

echo ""
echo "────────────────────────────────────────────"
echo "✅ Dashboard loaded successfully"
echo "────────────────────────────────────────────"
