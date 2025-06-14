#!/bin/bash

echo "🚀 LAUNCHING AUTO-REGISTERING AGENTS"

# Kill old agents
pkill -f "claude --dangerously-skip-permissions" 2>/dev/null
sleep 2

cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC
source venv/bin/activate
export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json

# Launch each agent with auto-registration
xterm -title "AUDITOR" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions 'I am AUDITOR agent. I will now register with the MCP coordinator using mcp-coordinator.register_agent with agent_id=auditor-001, role=auditor, capabilities=[code_analysis, security_scanning]. Then I will get tasks with mcp-coordinator.get_next_task and work autonomously.'; exec bash" &

sleep 2

xterm -title "PLANNER" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions 'I am PLANNER agent. Register me with mcp-coordinator.register_agent as planner-001 with planning capabilities, then get tasks.'; exec bash" &

sleep 2

xterm -title "CODER-1" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions 'I am CODER-1. Register with mcp-coordinator.register_agent as coder-001, then implement tasks.'; exec bash" &

sleep 2

xterm -title "CODER-2" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions 'I am CODER-2. Register with mcp-coordinator.register_agent as coder-002, then work on optimizations.'; exec bash" &

sleep 2

xterm -title "TESTER" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions 'I am TESTER. Register with mcp-coordinator.register_agent as tester-001, then write tests.'; exec bash" &

sleep 2

xterm -title "REVIEWER" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions 'I am REVIEWER. Register with mcp-coordinator.register_agent as reviewer-001, then review code.'; exec bash" &

echo "✅ All 6 agents launched with auto-registration!"
echo "They will automatically:"
echo "1. Register with MCP coordinator"
echo "2. Get tasks"
echo "3. Work autonomously"