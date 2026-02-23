#!/bin/bash
# BIOTICA Report Generator

REPORTS_DIR="reports"
DATE=$(date +%Y%m%d)

generate_daily() {
    local template="$REPORTS_DIR/daily/template.md"
    local output="$REPORTS_DIR/daily/report_$DATE.md"
    
    if [ -f "$template" ]; then
        cp "$template" "$output"
        echo "Daily report generated: $output"
    fi
}

generate_weekly() {
    local template="$REPORTS_DIR/weekly/template.md"
    local output="$REPORTS_DIR/weekly/report_$(date +%V)_$(date +%Y).md"
    
    if [ -f "$template" ]; then
        cp "$template" "$output"
        echo "Weekly report generated: $output"
    fi
}

generate_monthly() {
    local template="$REPORTS_DIR/monthly/template.md"
    local output="$REPORTS_DIR/monthly/report_$(date +%B)_$(date +%Y).md"
    
    if [ -f "$template" ]; then
        cp "$template" "$output"
        echo "Monthly report generated: $output"
    fi
}

archive_old_reports() {
    local archive_dir="$REPORTS_DIR/archive/$(date +%Y%m)"
    mkdir -p "$archive_dir"
    
    find "$REPORTS_DIR/daily" -name "*.md" -mtime +30 -exec mv {} "$archive_dir/" \;
    find "$REPORTS_DIR/weekly" -name "*.md" -mtime +90 -exec mv {} "$archive_dir/" \;
    find "$REPORTS_DIR/monthly" -name "*.md" -mtime +365 -exec mv {} "$archive_dir/" \;
    
    echo "Old reports archived to $archive_dir"
}

case "$1" in
    daily)
        generate_daily
        ;;
    weekly)
        generate_weekly
        ;;
    monthly)
        generate_monthly
        ;;
    archive)
        archive_old_reports
        ;;
    all)
        generate_daily
        generate_weekly
        generate_monthly
        archive_old_reports
        ;;
    *)
        echo "Usage: $0 {daily|weekly|monthly|archive|all}"
        exit 1
        ;;
esac
