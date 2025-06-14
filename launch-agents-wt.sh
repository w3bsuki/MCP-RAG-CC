#!/bin/bash

# For Windows Terminal (wt.exe)

# Kill any existing tmux session
tmux kill-session -t autonomous-claude 2>/dev/null

# Kill existing agents
pkill -f "claude --dangerously-skip-permissions" 2>/dev/null

echo "🚀 Launching agents in Windows Terminal tabs..."

# Set MCP settings path
export CLAUDE_MCP_SETTINGS_PATH="$(pwd)/claude_mcp_settings.json"

# Launch all agents in Windows Terminal with tabs
wt.exe -w 0 nt -d "$(pwd)" --title "AUDITOR" bash -c "source venv/bin/activate && claude --dangerously-skip-permissions 'I am an auditor agent.'" \; \
  nt -d "$(pwd)" --title "PLANNER" bash -c "source venv/bin/activate && claude --dangerously-skip-permissions 'I am a planner agent.'" \; \
  nt -d "$(pwd)" --title "CODER-1" bash -c "source venv/bin/activate && claude --dangerously-skip-permissions 'I am a coder agent #1.'" \; \
  nt -d "$(pwd)" --title "CODER-2" bash -c "source venv/bin/activate && claude --dangerously-skip-permissions 'I am a coder agent #2.'" \; \
  nt -d "$(pwd)" --title "TESTER" bash -c "source venv/bin/activate && claude --dangerously-skip-permissions 'I am a tester agent.'" \; \
  nt -d "$(pwd)" --title "REVIEWER" bash -c "source venv/bin/activate && claude --dangerously-skip-permissions 'I am a reviewer agent.'"

echo "✅ All agents launched in Windows Terminal tabs!"