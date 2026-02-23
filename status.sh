#!/bin/bash
echo "======================================"
echo "🌿 BIOTICA System Status"
echo "======================================"
echo ""

echo "📁 Project Structure:"
echo "-------------------"
ls -la | grep -v total | head -10
echo "..."

echo ""
echo "📊 Reports Directory:"
echo "-------------------"
if [ -d "reports" ]; then
    ls -la reports/
else
    echo "  No reports directory yet"
fi

echo ""
echo "🐍 Python Files:"
echo "--------------"
find . -name "*.py" 2>/dev/null | head -5 || echo "  No Python files found"

echo ""
echo "📝 Documentation:"
echo "---------------"
ls -la *.md 2>/dev/null || echo "  No markdown files found"

echo ""
echo "======================================"
