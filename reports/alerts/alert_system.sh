#!/bin/bash
# BIOTICA Alert System

ALERTS_DIR="reports/alerts"
DATE=$(date +%Y%m%d_%H%M%S)

create_alert() {
    local severity=$1
    local plot_id=$2
    local message=$3
    local ibr_score=$4
    
    alert_file="${ALERTS_DIR}/alert_${DATE}_${severity}.json"
    
    cat > "$alert_file" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "severity": "$severity",
    "plot_id": "$plot_id",
    "ibr_score": $ibr_score,
    "message": "$message",
    "status": "new"
}
