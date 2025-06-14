#!/bin/bash

echo "🚀 USING GNOME TERMINAL - PROPER CLIPBOARD!"
pkill -f "claude --dangerously-skip-permissions" 2>/dev/null

cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC
export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json

# Launch each agent in gnome-terminal with proper clipboard
gnome-terminal --title="AUDITOR" -- bash -c "source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo 'AUDITOR - Ctrl+Shift+C/V works!' && claude --dangerously-skip-permissions 'I am AUDITOR agent'; exec bash" &

sleep 2

gnome-terminal --title="PLANNER" -- bash -c "source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo 'PLANNER - Ctrl+Shift+C/V works!' && claude --dangerously-skip-permissions 'I am PLANNER agent'; exec bash" &

sleep 2

gnome-terminal --title="CODER-1" -- bash -c "source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo 'CODER-1 - Ctrl+Shift+C/V works!' && claude --dangerously-skip-permissions 'I am CODER-1 agent'; exec bash" &

sleep 2

gnome-terminal --title="CODER-2" -- bash -c "source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo 'CODER-2 - Ctrl+Shift+C/V works!' && claude --dangerously-skip-permissions 'I am CODER-2 agent'; exec bash" &

sleep 2

gnome-terminal --title="TESTER" -- bash -c "source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo 'TESTER - Ctrl+Shift+C/V works!' && claude --dangerously-skip-permissions 'I am TESTER agent'; exec bash" &

sleep 2

gnome-terminal --title="REVIEWER" -- bash -c "source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo 'REVIEWER - Ctrl+Shift+C/V works!' && claude --dangerously-skip-permissions 'I am REVIEWER agent'; exec bash" &

echo "✅ GNOME TERMINAL LAUNCHED - CTRL+SHIFT+C/V WORKS!"