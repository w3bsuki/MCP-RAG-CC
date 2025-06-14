#!/bin/bash

echo "🚀 LAUNCHING REAL CLAUDE AGENTS WITH MCP"

# Kill fake Python agents
pkill -f "auditor_agent.py"
pkill -f "coder_agent_loop.py"
pkill -f "planner_agent.py"
pkill -f "tester_agent.py"

# Ensure coordinator is running
./start-coordinator.sh

echo "Waiting for coordinator to start..."
sleep 5

# Launch REAL Claude instances that will use MCP
terminator --title="REAL-AUDITOR" -e "bash -c '
cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC
source venv/bin/activate
export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json

echo \"=== REAL CLAUDE AUDITOR AGENT ===\"
echo \"\"
echo \"This is a REAL Claude instance with MCP access!\"
echo \"\"
echo \"Initial task: Use mcp-coordinator tools to:\"
echo \"1. Register as AUDITOR agent\"
echo \"2. Get tasks and start working\"
echo \"\"

claude --dangerously-skip-permissions \"I am a REAL AUDITOR agent. I will now register with the MCP coordinator and start my work. First, let me use the mcp-coordinator.register_agent tool to register myself.\"

exec bash'" &

sleep 3

terminator --title="REAL-PLANNER" -e "bash -c '
cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC
source venv/bin/activate
export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json

echo \"=== REAL CLAUDE PLANNER AGENT ===\"
echo \"\"
echo \"This is a REAL Claude instance with MCP access!\"
echo \"\"

claude --dangerously-skip-permissions \"I am a REAL PLANNER agent. I will register with mcp-coordinator.register_agent and then get tasks to create implementation plans.\"

exec bash'" &

echo "✅ Launching REAL Claude agents that actually use MCP!"
echo ""
echo "These are ACTUAL Claude instances that will:"
echo "- Register with the coordinator via MCP"
echo "- Get tasks through MCP protocol"
echo "- Collaborate properly"
echo ""
echo "Watch them work for real!"