#!/bin/bash

echo "🚀 LAUNCHING AGENTS - NO AUTH BULLSHIT"
pkill -f "claude --dangerously-skip-permissions" 2>/dev/null

# Check if already authenticated
if [ -f ~/.config/claude/credentials ]; then
    echo "✅ Already authenticated!"
else
    echo "❌ Need to auth once in main terminal first"
    echo "Run: claude --dangerously-skip-permissions 'test'"
    echo "Auth there, then come back and run this script"
    exit 1
fi

cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC
source venv/bin/activate
export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json

# Launch all agents - they should use existing auth
for agent in AUDITOR PLANNER CODER-1 CODER-2 TESTER REVIEWER; do
    echo "Starting $agent..."
    xterm -title "$agent" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions 'I am $agent agent - I need to register with the MCP coordinator first using: mcp-coordinator.register_agent()'; exec bash" &
    sleep 1
done

echo "✅ ALL AGENTS LAUNCHED!"