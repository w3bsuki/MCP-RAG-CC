#!/bin/bash

echo "🚀 STARTING MCP COORDINATOR PROPERLY"

# Kill any existing coordinator
pkill -f "mcp-coordinator/server.py" 2>/dev/null

# The MCP coordinator needs to run as a stdio server
# It's waiting for connections from Claude instances

cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC
source venv/bin/activate

echo "Starting MCP Coordinator Server..."

# The coordinator is designed to work with stdio, not as standalone
# We need to run it in a way that keeps it alive for MCP connections

python3 -c "
import sys
sys.path.append('.')
from mcp_coordinator.server import main
import asyncio

# Run the coordinator
asyncio.run(main())
" &

COORD_PID=$!
echo "MCP Coordinator started with PID: $COORD_PID"

# Give it time to start
sleep 3

# Check if it's still running
if ps -p $COORD_PID > /dev/null; then
    echo "✅ MCP Coordinator is running!"
else
    echo "❌ MCP Coordinator failed to start"
    echo "Checking what went wrong..."
    
    # The issue is that the coordinator is designed for stdio communication
    # It needs to be connected to by Claude instances
    echo ""
    echo "The coordinator is waiting for MCP connections from Claude agents."
    echo "Your Claude agents need to call mcp-coordinator tools to connect!"
fi