#!/bin/bash

echo "🚀 Starting ONE agent at a time so you can authenticate properly"
echo ""

cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC
source venv/bin/activate
export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json

echo "Starting AUDITOR agent..."
echo "💡 Auth URL will appear - copy it to browser, get auth code, paste it back"
echo ""

claude --dangerously-skip-permissions "I am AUDITOR agent - I scan for security issues and code quality problems. I need to register with the MCP coordinator first using: mcp-coordinator.register_agent()"