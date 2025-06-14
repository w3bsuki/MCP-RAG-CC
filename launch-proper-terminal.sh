#!/bin/bash

echo "🚀 Using proper terminal with normal copy/paste..."
pkill -f "claude --dangerously-skip-permissions" 2>/dev/null

# Try different terminal emulators that support proper clipboard
TERMINAL="lxterm"

echo "Using terminal: $TERMINAL"

# Set environment
export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json

# Launch each agent with proper terminal
$TERMINAL -title "AUDITOR" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo 'AUDITOR AGENT - Try Ctrl+Shift+C/V for copy/paste' && claude --dangerously-skip-permissions 'I am AUDITOR agent'; exec bash" &

sleep 2

$TERMINAL -title "PLANNER" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo 'PLANNER AGENT - Try Ctrl+Shift+C/V for copy/paste' && claude --dangerously-skip-permissions 'I am PLANNER agent'; exec bash" &

sleep 2

$TERMINAL -title "CODER-1" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo 'CODER-1 AGENT - Try Ctrl+Shift+C/V for copy/paste' && claude --dangerously-skip-permissions 'I am CODER-1 agent'; exec bash" &

sleep 2

$TERMINAL -title "CODER-2" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo 'CODER-2 AGENT - Try Ctrl+Shift+C/V for copy/paste' && claude --dangerously-skip-permissions 'I am CODER-2 agent'; exec bash" &

sleep 2

$TERMINAL -title "TESTER" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo 'TESTER AGENT - Try Ctrl+Shift+C/V for copy/paste' && claude --dangerously-skip-permissions 'I am TESTER agent'; exec bash" &

sleep 2

$TERMINAL -title "REVIEWER" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo 'REVIEWER AGENT - Try Ctrl+Shift+C/V for copy/paste' && claude --dangerously-skip-permissions 'I am REVIEWER agent'; exec bash" &

echo "✅ All agents launched with proper terminal!"
echo ""
echo "🎯 PROPER TERMINAL FEATURES:"
echo "- Ctrl+Click opens links"
echo "- Ctrl+Shift+C to copy"
echo "- Ctrl+Shift+V to paste"
echo "- Right-click context menu"
echo "- Normal Windows clipboard integration"