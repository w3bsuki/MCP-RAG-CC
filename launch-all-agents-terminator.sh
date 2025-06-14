#!/bin/bash

echo "🚀 LAUNCHING ALL 6 AGENTS WITH TERMINATOR"
echo "✅ Using terminator for proper clipboard support"

# Kill any existing agents
pkill -f "claude --dangerously-skip-permissions" 2>/dev/null
sleep 2

cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC
source venv/bin/activate
export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json

# Ensure dashboard is running
echo "Checking dashboard status..."
if ! curl -s http://localhost:5000/api/status > /dev/null 2>&1; then
    echo "Starting dashboard..."
    python dashboard.py &
    sleep 3
fi

echo "Launching agents with auto-registration..."

# AUDITOR
terminator --title="AUDITOR-001" -e "bash -c '
cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && 
source venv/bin/activate && 
export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && 
echo \"AUDITOR-001 READY - Auto-registering with MCP...\" && 
claude --dangerously-skip-permissions \"I am AUDITOR-001. First, I will register with the MCP coordinator by calling mcp-coordinator.register_agent with these parameters: agent_id=auditor-001, role=auditor, capabilities=[code_analysis, security_scanning, performance_analysis, quality_assessment, pattern_recognition]. After registration, I will call mcp-coordinator.get_next_task to get my first task and begin autonomous operation. I will continue working autonomously, getting new tasks when I complete each one.\"; 
exec bash'" &

sleep 3

# PLANNER
terminator --title="PLANNER-001" -e "bash -c '
cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && 
source venv/bin/activate && 
export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && 
echo \"PLANNER-001 READY - Auto-registering with MCP...\" && 
claude --dangerously-skip-permissions \"I am PLANNER-001. First, I will register with the MCP coordinator by calling mcp-coordinator.register_agent with these parameters: agent_id=planner-001, role=planner, capabilities=[planning, task_breakdown, architecture_design, solution_planning, requirement_analysis]. After registration, I will call mcp-coordinator.get_next_task to get planning tasks and create detailed implementation plans. I will work autonomously and continuously.\"; 
exec bash'" &

sleep 3

# CODER-1
terminator --title="CODER-001" -e "bash -c '
cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && 
source venv/bin/activate && 
export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && 
echo \"CODER-001 READY - Auto-registering with MCP...\" && 
claude --dangerously-skip-permissions \"I am CODER-001. First, I will register with the MCP coordinator by calling mcp-coordinator.register_agent with these parameters: agent_id=coder-001, role=coder, capabilities=[code_implementation, bug_fixing, refactoring, feature_development, code_generation]. After registration, I will call mcp-coordinator.get_next_task to get implementation tasks and write code. I will work autonomously on the svelte-threadly-1 codebase.\"; 
exec bash'" &

sleep 3

# CODER-2
terminator --title="CODER-002" -e "bash -c '
cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && 
source venv/bin/activate && 
export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && 
echo \"CODER-002 READY - Auto-registering with MCP...\" && 
claude --dangerously-skip-permissions \"I am CODER-002. First, I will register with the MCP coordinator by calling mcp-coordinator.register_agent with these parameters: agent_id=coder-002, role=coder, capabilities=[code_implementation, optimization, performance_tuning, code_cleanup, parallel_development]. After registration, I will call mcp-coordinator.get_next_task to get optimization and implementation tasks. I will work autonomously alongside CODER-001.\"; 
exec bash'" &

sleep 3

# TESTER
terminator --title="TESTER-001" -e "bash -c '
cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && 
source venv/bin/activate && 
export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && 
echo \"TESTER-001 READY - Auto-registering with MCP...\" && 
claude --dangerously-skip-permissions \"I am TESTER-001. First, I will register with the MCP coordinator by calling mcp-coordinator.register_agent with these parameters: agent_id=tester-001, role=tester, capabilities=[test_writing, test_execution, coverage_analysis, quality_assurance, test_automation]. After registration, I will call mcp-coordinator.get_next_task to get testing tasks and write comprehensive tests for all new code. I will work autonomously.\"; 
exec bash'" &

sleep 3

# REVIEWER
terminator --title="REVIEWER-001" -e "bash -c '
cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC && 
source venv/bin/activate && 
export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json && 
echo \"REVIEWER-001 READY - Auto-registering with MCP...\" && 
claude --dangerously-skip-permissions \"I am REVIEWER-001. First, I will register with the MCP coordinator by calling mcp-coordinator.register_agent with these parameters: agent_id=reviewer-001, role=reviewer, capabilities=[code_review, pr_creation, quality_checking, documentation_review, best_practices]. After registration, I will call mcp-coordinator.get_next_task to review code changes and ensure quality. I will work autonomously.\"; 
exec bash'" &

echo ""
echo "✅ ALL 6 AGENTS LAUNCHED WITH TERMINATOR!"
echo ""
echo "The agents will:"
echo "1. Auto-register with MCP coordinator"
echo "2. Get tasks automatically"
echo "3. Work autonomously on the svelte-threadly-1 codebase"
echo ""
echo "Check dashboard at http://localhost:5000"
echo "Public dashboard at http://localhost:8080"
echo ""
echo "Agents will authenticate with Claude when they start."
echo "Use right-click or Ctrl+Shift+C/V to copy auth codes in terminator."