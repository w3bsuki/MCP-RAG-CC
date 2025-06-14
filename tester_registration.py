#!/usr/bin/env python3
"""Register as TESTER agent and get tasks"""

import json
import os
from datetime import datetime
from pathlib import Path

def register_tester():
    """Register as a tester agent with the MCP coordinator"""
    
    # Generate unique agent ID
    agent_id = f"tester-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{os.getpid()}"
    
    # Registration data
    registration_data = {
        "agent_id": agent_id,
        "role": "tester",
        "capabilities": [
            "unit_testing",
            "integration_testing", 
            "test_coverage",
            "edge_case_testing",
            "performance_testing",
            "test_automation",
            "python_testing",
            "javascript_testing",
            "typescript_testing",
            "e2e_testing",
            "mock_creation"
        ],
        "status": "active",
        "registered_at": datetime.now().isoformat(),
        "last_seen": datetime.now().isoformat()
    }
    
    # Read current state
    state_file = Path("/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/mcp-coordinator/state.json")
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
    except:
        state = {"agents": {}, "tasks": {}, "findings": {}}
    
    # Add our agent
    state["agents"][agent_id] = registration_data
    
    # Write state back
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
        
    # Also save registration info separately
    reg_file = Path(f"/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/mcp-coordinator/{agent_id}-registration.json")
    with open(reg_file, 'w') as f:
        json.dump(registration_data, f, indent=2)
    
    print(f"✅ Successfully registered as TESTER agent: {agent_id}")
    print(f"📋 Capabilities: {', '.join(registration_data['capabilities'])}")
    
    return agent_id

def get_tester_tasks(agent_id):
    """Get available tasks for testing"""
    
    # Read current state
    state_file = Path("/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/mcp-coordinator/state.json")
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
    except:
        print("❌ Could not read state file")
        return []
    
    # Find tasks suitable for tester
    available_tasks = []
    for task_id, task_data in state.get('tasks', {}).items():
        if task_data.get('status') == 'pending':
            task_type = task_data.get('type', '')
            if any(keyword in task_type.lower() for keyword in ['test', 'verify', 'validation', 'coverage']):
                available_tasks.append((task_id, task_data))
            elif task_data.get('assigned_to') == agent_id:
                available_tasks.append((task_id, task_data))
    
    if available_tasks:
        print(f"\n📝 Found {len(available_tasks)} testing tasks:")
        for task_id, task_data in available_tasks[:5]:
            print(f"   - {task_id}: {task_data.get('description', 'No description')[:60]}...")
    else:
        print("\n📝 No testing tasks currently available")
        
        # Check if there are any completed implementation tasks that need testing
        implementation_tasks = []
        for task_id, task_data in state.get('tasks', {}).items():
            if (task_data.get('status') == 'completed' and 
                task_data.get('type', '').lower() in ['implementation', 'fix', 'feature']):
                implementation_tasks.append((task_id, task_data))
                
        if implementation_tasks:
            print(f"\n💡 Found {len(implementation_tasks)} completed implementations that may need testing:")
            for task_id, task_data in implementation_tasks[:3]:
                print(f"   - {task_id}: {task_data.get('description', 'No description')[:60]}...")
                
    return available_tasks

if __name__ == "__main__":
    # Register as tester
    agent_id = register_tester()
    
    # Check for tasks
    tasks = get_tester_tasks(agent_id)
    
    print(f"\n✨ TESTER agent {agent_id} is ready to work!")
    print("🔄 Agent will continuously check for testing tasks...")