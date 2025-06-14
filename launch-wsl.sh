#!/bin/bash

# Convert WSL path to Windows path
WIN_PATH=$(wslpath -w "$(pwd)")

echo "Killing old sessions..."
pkill -f "claude --dangerously-skip-permissions" 2>/dev/null

echo "Starting agents in Windows Terminal..."

# Launch each agent in a new Windows Terminal tab
cmd.exe /c "wt.exe -w 0 new-tab --title \"🔍 AUDITOR - Security Scanner\" wsl.exe bash -c 'cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions \"I am AUDITOR agent - I scan for security issues and code quality problems\"'"

sleep 2

cmd.exe /c "wt.exe -w 0 new-tab --title PLANNER wsl.exe bash -c 'cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions \"I am PLANNER agent\"'"

sleep 2

cmd.exe /c "wt.exe -w 0 new-tab --title CODER-1 wsl.exe bash -c 'cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions \"I am CODER-1 agent\"'"

sleep 2

cmd.exe /c "wt.exe -w 0 new-tab --title CODER-2 wsl.exe bash -c 'cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions \"I am CODER-2 agent\"'"

sleep 2

cmd.exe /c "wt.exe -w 0 new-tab --title TESTER wsl.exe bash -c 'cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions \"I am TESTER agent\"'"

sleep 2

cmd.exe /c "wt.exe -w 0 new-tab --title REVIEWER wsl.exe bash -c 'cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions \"I am REVIEWER agent\"'"

echo "✅ All agents launched in Windows Terminal tabs!"