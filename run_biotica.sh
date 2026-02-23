#!/bin/bash
# BIOTICA Launcher

clear
echo "🌿 BIOTICA Launcher"
echo "=================="
echo ""
echo "Select option:"
echo "1) Complete Demo"
echo "2) Quick Test"
echo "3) Statistics"
echo "4) Dashboard"
echo "5) Interactive Menu"
echo "6) View Completion Certificate"
echo "7) Exit"
echo ""
read -p "Choice [1-7]: " opt

case $opt in
    1) python3 biotica_demo.py ;;
    2) python3 test_quick.py ;;
    3) python3 stats.py ;;
    4) bash dashboard.sh ;;
    5) bash quick_start.sh ;;
    6) cat COMPLETION.txt ;;
    7) exit ;;
    *) echo "Invalid option" ;;
esac
