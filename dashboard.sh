#!/bin/bash
# Launch the monitoring dashboard

echo "🌐 Launching Monitoring Dashboard"
echo "================================="

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask not installed. The dashboard is optional."
    echo "To install: pip install flask flask-cors"
    echo ""
    echo "The autonomous system works without the dashboard."
    echo "Use ./status.sh for command-line monitoring."
    exit 0
fi

echo "📊 Starting dashboard server..."
echo "🌐 Dashboard will be available at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo ""

cd "$(dirname "$0")"
python3 dashboard/server.py