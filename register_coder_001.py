#!/usr/bin/env python3
"""Register coder-001 agent with the coordinator."""

import sys
import json
import subprocess
from pathlib import Path

# Add the MCP-RAG-CC directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def send_mcp_request(method, params):
    """Send a request to the MCP coordinator."""
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    
    # Run the coordinator and send the request
    process = subprocess.Popen(
        [sys.executable, "mcp-coordinator/server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send the request
    stdout, stderr = process.communicate(input=json.dumps(request) + "\n")
    
    # Parse the response
    for line in stdout.split('\n'):
        if line.strip() and line.startswith('{'):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    
    return None

# Register the agent
print("Registering coder-001...")
register_response = send_mcp_request("tools/register_agent", {
    "agent_id": "coder-001",
    "role": "coder",
    "capabilities": ["code_implementation", "bug_fixing", "refactoring", "feature_development", "code_generation"]
})

if register_response:
    print(f"Registration response: {json.dumps(register_response, indent=2)}")
else:
    print("Failed to get registration response")

# Get next task
print("\nGetting next task for coder-001...")
task_response = send_mcp_request("tools/get_next_task", {
    "agent_id": "coder-001",
    "agent_role": "coder"
})

if task_response:
    print(f"Task response: {json.dumps(task_response, indent=2)}")
else:
    print("Failed to get task response")