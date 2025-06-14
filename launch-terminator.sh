#!/bin/bash

echo "🚀 USING TERMINATOR - BEST CLIPBOARD SUPPORT!"
pkill -f "claude --dangerously-skip-permissions" 2>/dev/null

cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC
export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json

# Launch agents in terminator
terminator --title="AUDITOR" -e "bash -c 'source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo \"AUDITOR - Right-click works, Ctrl+Shift+C/V works!\" && claude --dangerously-skip-permissions \"I am AUDITOR agent. I will now automatically register with the MCP coordinator and start working. First, let me use mcp-coordinator.register_agent with agent_id='auditor-001', role='auditor', capabilities=['code_analysis', 'security_scanning', 'performance_analysis', 'quality_assessment', 'pattern_recognition']. Then I'll use mcp-coordinator.get_next_task to get work and begin my autonomous operation.\"; exec bash'" &

sleep 2

terminator --title="PLANNER" -e "bash -c 'source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo \"PLANNER - Right-click works, Ctrl+Shift+C/V works!\" && claude --dangerously-skip-permissions \"I am PLANNER agent. I will automatically register with mcp-coordinator.register_agent using agent_id='planner-001', role='planner', capabilities=['planning', 'task_breakdown', 'architecture_design', 'solution_planning']. Then I'll continuously get tasks with mcp-coordinator.get_next_task and create implementation plans.\"; exec bash'" &

sleep 2

terminator --title="CODER-1" -e "bash -c 'source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo \"CODER-1 - Right-click works, Ctrl+Shift+C/V works!\" && claude --dangerously-skip-permissions \"I am CODER-1 agent. I will register with mcp-coordinator.register_agent using agent_id='coder-001', role='coder', capabilities=['code_implementation', 'bug_fixing', 'refactoring', 'feature_development']. Then I'll get implementation tasks with mcp-coordinator.get_next_task and implement solutions.\"; exec bash'" &

sleep 2

terminator --title="CODER-2" -e "bash -c 'source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo \"CODER-2 - Right-click works, Ctrl+Shift+C/V works!\" && claude --dangerously-skip-permissions \"I am CODER-2 agent. I will register with mcp-coordinator.register_agent using agent_id='coder-002', role='coder', capabilities=['code_implementation', 'optimization', 'performance_tuning', 'code_cleanup']. Then I'll get tasks with mcp-coordinator.get_next_task and work on optimizations.\"; exec bash'" &

sleep 2

terminator --title="TESTER" -e "bash -c 'source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo \"TESTER - Right-click works, Ctrl+Shift+C/V works!\" && claude --dangerously-skip-permissions \"I am TESTER agent. I will register with mcp-coordinator.register_agent using agent_id='tester-001', role='tester', capabilities=['test_writing', 'test_execution', 'coverage_analysis', 'quality_assurance']. Then I'll get testing tasks with mcp-coordinator.get_next_task and write comprehensive tests.\"; exec bash'" &

sleep 2

terminator --title="REVIEWER" -e "bash -c 'source venv/bin/activate && export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && echo \"REVIEWER - Right-click works, Ctrl+Shift+C/V works!\" && claude --dangerously-skip-permissions \"I am REVIEWER agent. I will register with mcp-coordinator.register_agent using agent_id='reviewer-001', role='reviewer', capabilities=['code_review', 'pr_creation', 'quality_checking', 'documentation_review']. Then I'll get review tasks with mcp-coordinator.get_next_task and review code changes.\"; exec bash'" &

echo "✅ TERMINATOR LAUNCHED - PERFECT CLIPBOARD!"