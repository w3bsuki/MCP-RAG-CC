#!/bin/bash

echo "Killing old agents..."
pkill -f "claude --dangerously-skip-permissions" 2>/dev/null

echo "🚀 Launching AI Agent Team in Windows Terminal..."

# Launch each agent with descriptive titles and roles
cmd.exe /c "wt.exe -w 0 new-tab --title \"🔍 AUDITOR - Security Scanner\" wsl.exe bash -c 'cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions \"I am AUDITOR agent - I scan for security issues and code quality problems\"'"

sleep 2

cmd.exe /c "wt.exe -w 0 new-tab --title \"📋 PLANNER - Task Architect\" wsl.exe bash -c 'cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions \"I am PLANNER agent - I create implementation plans from audit findings\"'"

sleep 2

cmd.exe /c "wt.exe -w 0 new-tab --title \"💻 CODER-1 - Implementation\" wsl.exe bash -c 'cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions \"I am CODER-1 agent - I implement solutions and write code\"'"

sleep 2

cmd.exe /c "wt.exe -w 0 new-tab --title \"⚡ CODER-2 - Optimization\" wsl.exe bash -c 'cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions \"I am CODER-2 agent - I handle refactoring and optimization\"'"

sleep 2

cmd.exe /c "wt.exe -w 0 new-tab --title \"🧪 TESTER - Quality Guard\" wsl.exe bash -c 'cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions \"I am TESTER agent - I write tests and verify code quality\"'"

sleep 2

cmd.exe /c "wt.exe -w 0 new-tab --title \"👁️ REVIEWER - Code Critic\" wsl.exe bash -c 'cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && claude --dangerously-skip-permissions \"I am REVIEWER agent - I review code and create pull requests\"'"

echo "✅ All 6 AI agents launched in Windows Terminal!"
echo ""
echo "Each tab shows:"
echo "🔍 AUDITOR - Finds security & quality issues" 
echo "📋 PLANNER - Creates implementation plans"
echo "💻 CODER-1 - Implements new features"
echo "⚡ CODER-2 - Optimizes & refactors code"
echo "🧪 TESTER - Writes tests & validates"
echo "👁️ REVIEWER - Reviews & creates PRs"
echo ""
echo "Authenticate each agent to start the autonomous work!"