#!/bin/bash

echo "🚀 Launching AI Agent Team in separate XTerm windows..."
echo "Killing old agents..."
pkill -f "claude --dangerously-skip-permissions" 2>/dev/null

# Set environment
export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json

echo "Starting agents in separate XTerm windows..."

# Launch each agent in a separate xterm window
xterm -title "🔍 AUDITOR - Security Scanner" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions 'I am AUDITOR agent - I scan for security issues and code quality problems. I need to register with the MCP coordinator first using: mcp-coordinator.register_agent()'; exec bash" &

sleep 2

xterm -title "📋 PLANNER - Task Architect" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions 'I am PLANNER agent - I create implementation plans from audit findings. I need to register with the MCP coordinator first using: mcp-coordinator.register_agent()'; exec bash" &

sleep 2

xterm -title "💻 CODER-1 - Implementation" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions 'I am CODER-1 agent - I implement solutions and write code. I need to register with the MCP coordinator first using: mcp-coordinator.register_agent()'; exec bash" &

sleep 2

xterm -title "⚡ CODER-2 - Optimization" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions 'I am CODER-2 agent - I handle refactoring and optimization. I need to register with the MCP coordinator first using: mcp-coordinator.register_agent()'; exec bash" &

sleep 2

xterm -title "🧪 TESTER - Quality Guard" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions 'I am TESTER agent - I write tests and verify code quality. I need to register with the MCP coordinator first using: mcp-coordinator.register_agent()'; exec bash" &

sleep 2

xterm -title "👁️ REVIEWER - Code Critic" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions 'I am REVIEWER agent - I review code and create pull requests. I need to register with the MCP coordinator first using: mcp-coordinator.register_agent()'; exec bash" &

echo "✅ All 6 AI agents launched in separate XTerm windows!"
echo ""
echo "Each window shows:"
echo "🔍 AUDITOR - Finds security & quality issues" 
echo "📋 PLANNER - Creates implementation plans"
echo "💻 CODER-1 - Implements new features"
echo "⚡ CODER-2 - Optimizes & refactors code"
echo "🧪 TESTER - Writes tests & validates"
echo "👁️ REVIEWER - Reviews & creates PRs"
echo ""
echo "🎯 IMPORTANT: Each agent needs to:"
echo "1. Sign in to Claude when browser opens"
echo "2. Call: mcp-coordinator.register_agent() to join the team"
echo "3. Start working autonomously!"