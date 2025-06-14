#!/bin/bash

echo "🚀 USING WINDOWS TERMINAL - PROPER COPY/PASTE!"
pkill -f "claude --dangerously-skip-permissions" 2>/dev/null

# Launch directly in Windows Terminal tabs - this WILL work for copy/paste
cmd.exe /c "wt.exe -w 0 new-tab --title \"AUDITOR\" -- wsl.exe -d Ubuntu -e bash -l -c \"cd ~/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=~/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo 'AUDITOR - Normal Ctrl+C/Ctrl+V works here!' && claude --dangerously-skip-permissions 'I am AUDITOR agent'; exec bash\""

sleep 2

cmd.exe /c "wt.exe -w 0 new-tab --title \"PLANNER\" wsl.exe -e bash -c \"cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo 'PLANNER - Normal Ctrl+C/Ctrl+V works here!' && claude --dangerously-skip-permissions 'I am PLANNER agent'\""

sleep 2

cmd.exe /c "wt.exe -w 0 new-tab --title \"CODER-1\" wsl.exe -e bash -c \"cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo 'CODER-1 - Normal Ctrl+C/Ctrl+V works here!' && claude --dangerously-skip-permissions 'I am CODER-1 agent'\""

sleep 2

cmd.exe /c "wt.exe -w 0 new-tab --title \"CODER-2\" wsl.exe -e bash -c \"cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo 'CODER-2 - Normal Ctrl+C/Ctrl+V works here!' && claude --dangerously-skip-permissions 'I am CODER-2 agent'\""

sleep 2

cmd.exe /c "wt.exe -w 0 new-tab --title \"TESTER\" wsl.exe -e bash -c \"cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo 'TESTER - Normal Ctrl+C/Ctrl+V works here!' && claude --dangerously-skip-permissions 'I am TESTER agent'\""

sleep 2

cmd.exe /c "wt.exe -w 0 new-tab --title \"REVIEWER\" wsl.exe -e bash -c \"cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo 'REVIEWER - Normal Ctrl+C/Ctrl+V works here!' && claude --dangerously-skip-permissions 'I am REVIEWER agent'\""

echo "✅ WINDOWS TERMINAL TABS LAUNCHED!"
echo ""
echo "🎯 WINDOWS TERMINAL HAS:"
echo "- Normal Ctrl+C/Ctrl+V copy/paste"
echo "- Clickable links" 
echo "- Right-click context menu"
echo "- Perfect Windows clipboard integration"
echo ""
echo "THIS WILL FUCKING WORK!"