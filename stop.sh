#!/bin/bash
# Stop the Autonomous Multi-Agent System

echo "🛑 Stopping Autonomous Multi-Agent System"
echo "========================================"

# Check if session exists
if tmux has-session -t autonomous-claude 2>/dev/null; then
    echo "📤 Sending shutdown signal to agents..."
    
    # Send exit command to all windows
    for window in $(tmux list-windows -t autonomous-claude -F '#I'); do
        tmux send-keys -t autonomous-claude:$window "/exit" Enter 2>/dev/null || true
    done
    
    # Give agents time to shutdown gracefully
    echo "⏳ Waiting for graceful shutdown..."
    sleep 3
    
    # Kill the tmux session
    echo "🔪 Terminating tmux session..."
    tmux kill-session -t autonomous-claude 2>/dev/null
    
    echo "✅ Autonomous agents stopped"
else
    echo "ℹ️  No autonomous session found"
fi

# Kill any orphaned MCP coordinator processes
echo "🧹 Cleaning up MCP coordinator..."
pkill -f "mcp-coordinator/server.py" 2>/dev/null || true

# Save shutdown timestamp
TIMESTAMP=$(date -Iseconds)
echo "{\"shutdown_time\": \"$TIMESTAMP\"}" > mcp-coordinator/last-shutdown.json 2>/dev/null || true

echo ""
echo "✅ System stopped successfully"
echo ""
echo "📊 To check logs:"
echo "   cat mcp-coordinator/state.json"
echo ""
echo "🚀 To restart:"
echo "   ./start.sh"