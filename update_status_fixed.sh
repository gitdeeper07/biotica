#!/bin/bash
# BIOTICA - Quick Status Update (Fixed)

echo "📊 BIOTICA - Quick Status Update"
echo "================================="
echo ""

# Read current IBR for PLOT_089
read -p "Enter current IBR for PLOT_089 (0-1): " ibr_089

# Validate input
if (( $(echo "$ibr_089 > 1" | bc -l) )) || (( $(echo "$ibr_089 < 0" | bc -l) )); then
    echo "❌ Invalid value. IBR must be between 0 and 1"
    exit 1
fi

# Update recommendation based on value
if (( $(echo "$ibr_089 > 0.35" | bc -l) )); then
    echo "✅ PLOT_089 showing improvement (IBR: $ibr_089)"
    echo "Recommendation: Continue monitoring, recheck in 48h"
elif (( $(echo "$ibr_089 > 0.30" | bc -l) )); then
    echo "⚠️ PLOT_089 stable but critical (IBR: $ibr_089)"
    echo "Recommendation: Maintain emergency protocols"
else
    echo "🔴 PLOT_089 worsening (IBR: $ibr_089)"
    echo "Recommendation: Immediate intensive intervention required"
fi

echo ""
echo "Update logged: $(date)"
