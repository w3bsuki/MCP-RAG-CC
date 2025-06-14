#!/bin/bash

# Kill any existing tmux session
tmux kill-session -t autonomous-claude 2>/dev/null

# Kill existing agents
pkill -f "claude --dangerously-skip-permissions" 2>/dev/null

echo "🚀 Launching agents in separate terminals..."

# Set MCP settings path
export CLAUDE_MCP_SETTINGS_PATH="$(pwd)/claude_mcp_settings.json"

# Launch each agent in a new terminal window
# Auditor
gnome-terminal --title="Agent: AUDITOR" -- bash -c "cd $(pwd) && source venv/bin/activate && claude --dangerously-skip-permissions 'I am an auditor agent. My role is to continuously audit the codebase for issues.'; exec bash" &

sleep 2

# Planner
gnome-terminal --title="Agent: PLANNER" -- bash -c "cd $(pwd) && source venv/bin/activate && claude --dangerously-skip-permissions 'I am a planner agent. My role is to create implementation plans from audit findings.'; exec bash" &

sleep 2

# Coder 1
gnome-terminal --title="Agent: CODER-1" -- bash -c "cd $(pwd) && source venv/bin/activate && claude --dangerously-skip-permissions 'I am a coder agent. My role is to implement solutions based on plans.'; exec bash" &

sleep 2

# Coder 2
gnome-terminal --title="Agent: CODER-2" -- bash -c "cd $(pwd) && source venv/bin/activate && claude --dangerously-skip-permissions 'I am a coder agent. My role is to implement solutions based on plans.'; exec bash" &

sleep 2

# Tester
gnome-terminal --title="Agent: TESTER" -- bash -c "cd $(pwd) && source venv/bin/activate && claude --dangerously-skip-permissions 'I am a tester agent. My role is to write and run tests for new code.'; exec bash" &

sleep 2

# Reviewer
gnome-terminal --title="Agent: REVIEWER" -- bash -c "cd $(pwd) && source venv/bin/activate && claude --dangerously-skip-permissions 'I am a reviewer agent. My role is to review code changes and create PRs.'; exec bash" &

echo "✅ All agents launched in separate terminals!"
echo ""
echo "Each agent will:"
echo "1. Show theme selection - just type 1 and Enter"
echo "2. Show OAuth URL - copy/paste to browser"
echo "3. Ask for auth code - paste it back"
echo "4. Start working autonomously"