#!/bin/bash
# Start the MCP Coordinator Server

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting MCP Coordinator Server${NC}"

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
fi

# Kill any existing coordinator processes
echo -e "${YELLOW}Stopping any existing coordinator processes...${NC}"
pkill -f "mcp-coordinator/server.py" 2>/dev/null || true
sleep 1

# Create log directory if it doesn't exist
mkdir -p mcp-coordinator/logs

# Start the coordinator in the background
echo -e "${GREEN}Starting MCP Coordinator...${NC}"
nohup python3 mcp-coordinator/server.py \
    > mcp-coordinator/logs/coordinator.stdout.log \
    2> mcp-coordinator/logs/coordinator.stderr.log &

COORDINATOR_PID=$!
echo $COORDINATOR_PID > mcp-coordinator/coordinator.pid

# Wait a moment and check if it started
sleep 2

if ps -p $COORDINATOR_PID > /dev/null; then
    echo -e "${GREEN}✅ MCP Coordinator started successfully (PID: $COORDINATOR_PID)${NC}"
    echo -e "${GREEN}Logs available at:${NC}"
    echo "  - stdout: mcp-coordinator/logs/coordinator.stdout.log"
    echo "  - stderr: mcp-coordinator/logs/coordinator.stderr.log"
else
    echo -e "${RED}❌ Failed to start MCP Coordinator${NC}"
    echo -e "${RED}Check logs for errors:${NC}"
    tail -20 mcp-coordinator/logs/coordinator.stderr.log
    exit 1
fi