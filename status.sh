#!/bin/bash
# Check status of the Autonomous Multi-Agent System

echo "📊 Autonomous Multi-Agent System Status"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check tmux session
echo "🖥️  Agent Sessions:"
if tmux has-session -t autonomous-claude 2>/dev/null; then
    echo -e "${GREEN}✅ Main session is running${NC}"
    echo ""
    echo "Active agents:"
    tmux list-windows -t autonomous-claude -F '  - #I: #W (#{window_activity_string})' 2>/dev/null
else
    echo -e "${RED}❌ No active session${NC}"
fi

echo ""
echo "📋 MCP Coordinator Status:"

# Check coordinator state
STATE_FILE="mcp-coordinator/state.json"
if [ -f "$STATE_FILE" ]; then
    if command -v jq &> /dev/null; then
        # Use jq if available for pretty output
        AGENTS=$(jq -r '.agents | length' "$STATE_FILE" 2>/dev/null || echo "0")
        PENDING=$(jq -r '.task_queue | map(select(.status == "pending")) | length' "$STATE_FILE" 2>/dev/null || echo "0")
        IN_PROGRESS=$(jq -r '.task_queue | map(select(.status == "in_progress")) | length' "$STATE_FILE" 2>/dev/null || echo "0")
        COMPLETED=$(jq -r '.task_queue | map(select(.status == "completed")) | length' "$STATE_FILE" 2>/dev/null || echo "0")
        FINDINGS=$(jq -r '.audit_findings | length' "$STATE_FILE" 2>/dev/null || echo "0")
        
        echo -e "  Registered agents: ${BLUE}$AGENTS${NC}"
        echo -e "  Pending tasks: ${YELLOW}$PENDING${NC}"
        echo -e "  In-progress tasks: ${BLUE}$IN_PROGRESS${NC}"
        echo -e "  Completed tasks: ${GREEN}$COMPLETED${NC}"
        echo -e "  Audit findings: ${YELLOW}$FINDINGS${NC}"
    else
        # Fallback without jq
        echo "  State file exists (install jq for detailed stats)"
        echo "  Size: $(du -h "$STATE_FILE" | cut -f1)"
        echo "  Modified: $(date -r "$STATE_FILE" '+%Y-%m-%d %H:%M:%S')"
    fi
else
    echo -e "${YELLOW}  No state file found${NC}"
fi

echo ""
echo "📝 Recent Audit Findings:"
AUDIT_LOG="mcp-coordinator/state.json"
if [ -f "$AUDIT_LOG" ]; then
    if command -v jq &> /dev/null; then
        # Show last 5 findings
        jq -r '.audit_findings[-5:] | reverse | .[] | "  [\(.severity)] \(.title)"' "$AUDIT_LOG" 2>/dev/null || echo "  No findings yet"
    else
        echo "  Audit log exists (install jq to view findings)"
    fi
else
    echo "  No audit findings yet"
fi

echo ""
echo "🌳 Git Worktrees:"
if command -v git &> /dev/null && git rev-parse --git-dir > /dev/null 2>&1; then
    WORKTREES=$(git worktree list | grep -c "agent-workspaces" || echo "0")
    echo "  Active worktrees: $WORKTREES"
    if [ $WORKTREES -gt 0 ]; then
        git worktree list | grep "agent-workspaces" | sed 's/^/    /'
    fi
else
    echo "  Not in a git repository"
fi

echo ""
echo "💾 Resource Usage:"
if [ -d "mcp-coordinator" ]; then
    echo "  Coordinator data: $(du -sh mcp-coordinator 2>/dev/null | cut -f1)"
fi
if [ -d "agent-workspaces" ]; then
    echo "  Agent workspaces: $(du -sh agent-workspaces 2>/dev/null | cut -f1)"
fi

echo ""
echo "🔧 Quick Actions:"
echo "  View agents:    tmux attach -t autonomous-claude"
echo "  Stop system:    ./stop.sh"
echo "  View logs:      tail -f mcp-coordinator/state.json"
echo "  Manual agent:   claude"
echo ""

# Check last shutdown
if [ -f "mcp-coordinator/last-shutdown.json" ]; then
    LAST_SHUTDOWN=$(cat mcp-coordinator/last-shutdown.json | grep -o '"shutdown_time": "[^"]*"' | cut -d'"' -f4)
    if [ ! -z "$LAST_SHUTDOWN" ]; then
        echo "📅 Last shutdown: $LAST_SHUTDOWN"
    fi
fi