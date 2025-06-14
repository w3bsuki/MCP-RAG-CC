#!/bin/bash

echo "🚀 USING TERMINATOR - BEST CLIPBOARD SUPPORT!"
pkill -f "claude --dangerously-skip-permissions" 2>/dev/null

cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC
export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json

# Launch agents in terminator
terminator --title="AUDITOR" -e "bash -c 'source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo \"AUDITOR - Right-click works, Ctrl+Shift+C/V works!\" && claude --dangerously-skip-permissions \"I am AUDITOR agent\"; exec bash'" &

sleep 2

terminator --title="PLANNER" -e "bash -c 'source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo \"PLANNER - Right-click works, Ctrl+Shift+C/V works!\" && claude --dangerously-skip-permissions \"I am PLANNER agent\"; exec bash'" &

sleep 2

terminator --title="CODER-1" -e "bash -c 'source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo \"CODER-1 - Right-click works, Ctrl+Shift+C/V works!\" && claude --dangerously-skip-permissions \"I am CODER-1 agent\"; exec bash'" &

sleep 2

terminator --title="CODER-2" -e "bash -c 'source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo \"CODER-2 - Right-click works, Ctrl+Shift+C/V works!\" && claude --dangerously-skip-permissions \"I am CODER-2 agent\"; exec bash'" &

sleep 2

terminator --title="TESTER" -e "bash -c 'source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo \"TESTER - Right-click works, Ctrl+Shift+C/V works!\" && claude --dangerously-skip-permissions \"I am TESTER agent\"; exec bash'" &

sleep 2

terminator --title="REVIEWER" -e "bash -c 'source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo \"REVIEWER - Right-click works, Ctrl+Shift+C/V works!\" && claude --dangerously-skip-permissions \"I am REVIEWER agent\"; exec bash'" &

echo "✅ TERMINATOR LAUNCHED - PERFECT CLIPBOARD!"