#!/bin/bash

echo "Killing old sessions..."
tmux kill-session -t agents 2>/dev/null
pkill -f "claude --dangerously-skip-permissions" 2>/dev/null

echo "Starting agents in tmux with split panes..."

# Create new tmux session
tmux new-session -d -s agents -n main

# Set MCP path
tmux send-keys -t agents:main "export CLAUDE_MCP_SETTINGS_PATH=$(pwd)/claude_mcp_settings.json" Enter

# Split into 6 panes
tmux split-window -t agents:main -h
tmux split-window -t agents:main -v
tmux split-window -t agents:main.0 -v
tmux split-window -t agents:main.2 -h
tmux split-window -t agents:main.4 -h

# Launch agents in each pane
tmux send-keys -t agents:main.0 "source venv/bin/activate && claude --dangerously-skip-permissions 'I am AUDITOR agent'" Enter
sleep 1
tmux send-keys -t agents:main.1 "source venv/bin/activate && claude --dangerously-skip-permissions 'I am PLANNER agent'" Enter
sleep 1
tmux send-keys -t agents:main.2 "source venv/bin/activate && claude --dangerously-skip-permissions 'I am CODER-1 agent'" Enter
sleep 1
tmux send-keys -t agents:main.3 "source venv/bin/activate && claude --dangerously-skip-permissions 'I am CODER-2 agent'" Enter
sleep 1
tmux send-keys -t agents:main.4 "source venv/bin/activate && claude --dangerously-skip-permissions 'I am TESTER agent'" Enter
sleep 1
tmux send-keys -t agents:main.5 "source venv/bin/activate && claude --dangerously-skip-permissions 'I am REVIEWER agent'" Enter

echo "✅ Done! Attach with: tmux attach -t agents"
echo ""
echo "You'll see all 6 agents in split panes!"
echo "Navigate with Ctrl+B then arrow keys"