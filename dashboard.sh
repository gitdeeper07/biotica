#!/bin/bash
# BIOTICA Dashboard

clear
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              🌿 BIOTICA - System Dashboard                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# قراءة آخر تحليل JSON
LATEST_JSON=$(ls -t reports/daily/analysis_*.json 2>/dev/null | head -1)

if [ -f "$LATEST_JSON" ]; then
    echo "📊 Latest Analysis: $(basename $LATEST_JSON)"
    echo "────────────────────────────────────────────"
    
    # استخراج البيانات (باستخدام grep بسيط)
    TOTAL=$(grep -o '"total_plots": [0-9]*' "$LATEST_JSON" | cut -d' ' -f2)
    AVG=$(grep -o '"average_ibr": [0-9.]*' "$LATEST_JSON" | cut -d' ' -f2)
    RISK=$(grep -o '"risk_level": "[^"]*"' "$LATEST_JSON" | cut -d'"' -f4)
    
    echo "📈 System Status:"
    echo "  • Total Plots: $TOTAL"
    echo "  • Average IBR: $AVG"
    echo "  • Risk Level: $RISK"
    echo ""
    
    # عرض التصنيف
    echo "📋 Classification:"
    grep -A6 '"classification"' "$LATEST_JSON" | grep -E '"(pristine|functional|impaired|degraded|collapsed)"' | while read line; do
        name=$(echo $line | cut -d'"' -f2)
        value=$(echo $line | cut -d':' -f2 | tr -d ' ,')
        printf "  • %-10s : %s\n" "${name^^}" "$value"
    done
    echo ""
    
    # عرض التنبيهات
    echo "⚠️ Active Alerts:"
    grep -A3 '"alerts_list"' "$LATEST_JSON" | grep -E '"plot":' | head -3 | while read line; do
        plot=$(echo $line | cut -d'"' -f4)
        echo "  • $plot"
    done
    
else
    echo "❌ No analysis files found"
    echo "Run './reports/generate_report.sh daily' first"
fi

echo ""
echo "────────────────────────────────────────────"
echo "🚀 Commands:"
echo "  refresh    - Reload dashboard"
echo "  reports    - View reports directory"
echo "  demo       - Run complete demo"
echo "  exit       - Exit dashboard"
echo "────────────────────────────────────────────"
