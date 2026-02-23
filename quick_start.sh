#!/bin/bash
echo "🚀 BIOTICA Quick Start"
echo "======================"
echo ""
echo "Select an option:"
echo "1) Run complete demo"
echo "2) Quick test"
echo "3) View statistics"
echo "4) Show dashboard"
echo "5) View reports"
echo "6) Exit"
echo ""
read -p "Choice [1-6]: " choice

case $choice in
    1) python3 biotica_demo.py ;;
    2) python3 test_quick.py ;;
    3) python3 stats.py ;;
    4) bash dashboard.sh ;;
    5) ls -la reports/daily/ ;;
    6) exit ;;
    *) echo "Invalid choice" ;;
esac
