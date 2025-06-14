#!/bin/bash

echo "🚀 Launching AI Agent Team in better terminals..."
echo "Killing old agents..."
pkill -f "claude --dangerously-skip-permissions" 2>/dev/null

# Set environment
export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json

echo "Starting agents in separate terminal windows..."

# Launch each agent in a separate terminal window with better copy/paste support
xterm -title "AUDITOR" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo '=== AUDITOR AGENT STARTING ===' && echo 'TIP: Right-click to copy/paste links!' && claude --dangerously-skip-permissions 'I am AUDITOR agent - I scan for security issues and code quality problems. I need to register with the MCP coordinator first using: mcp-coordinator.register_agent()'; exec bash" &

sleep 2

xterm -title "PLANNER" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo '=== PLANNER AGENT STARTING ===' && echo 'TIP: Right-click to copy/paste links!' && claude --dangerously-skip-permissions 'I am PLANNER agent - I create implementation plans from audit findings. I need to register with the MCP coordinator first using: mcp-coordinator.register_agent()'; exec bash" &

sleep 2

xterm -title "CODER-1" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo '=== CODER-1 AGENT STARTING ===' && echo 'TIP: Right-click to copy/paste links!' && claude --dangerously-skip-permissions 'I am CODER-1 agent - I implement solutions and write code. I need to register with the MCP coordinator first using: mcp-coordinator.register_agent()'; exec bash" &

sleep 2

xterm -title "CODER-2" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo '=== CODER-2 AGENT STARTING ===' && echo 'TIP: Right-click to copy/paste links!' && claude --dangerously-skip-permissions 'I am CODER-2 agent - I handle refactoring and optimization. I need to register with the MCP coordinator first using: mcp-coordinator.register_agent()'; exec bash" &

sleep 2

xterm -title "TESTER" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo '=== TESTER AGENT STARTING ===' && echo 'TIP: Right-click to copy/paste links!' && claude --dangerously-skip-permissions 'I am TESTER agent - I write tests and verify code quality. I need to register with the MCP coordinator first using: mcp-coordinator.register_agent()'; exec bash" &

sleep 2

xterm -title "REVIEWER" -e bash -c "cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo '=== REVIEWER AGENT STARTING ===' && echo 'TIP: Right-click to copy/paste links!' && claude --dangerously-skip-permissions 'I am REVIEWER agent - I review code and create pull requests. I need to register with the MCP coordinator first using: mcp-coordinator.register_agent()'; exec bash" &

echo "✅ All 6 AI agents launched in better terminal windows!"
echo ""
echo "Each window shows:"
echo "🔍 AUDITOR - Finds security & quality issues" 
echo "📋 PLANNER - Creates implementation plans"
echo "💻 CODER-1 - Implements new features"
echo "⚡ CODER-2 - Optimizes & refactors code"
echo "🧪 TESTER - Writes tests & validates"
echo "👁️ REVIEWER - Reviews & creates PRs"
echo ""
echo "💡 COPY/PASTE TIPS:"
echo "- Right-click in terminal to copy/paste"
echo "- Or select text with mouse and middle-click to paste"
echo "- Ctrl+Shift+C/V might work in some terminals"
echo ""
echo "🎯 IMPORTANT: Each agent needs to:"
echo "1. Sign in to Claude when browser opens"
echo "2. Call: mcp-coordinator.register_agent() to join the team"
echo "3. Start working autonomously!"