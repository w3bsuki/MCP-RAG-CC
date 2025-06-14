#!/usr/bin/env python3
"""
Register REVIEWER-001 agent by updating state file directly
"""

import json
from datetime import datetime
from pathlib import Path

def register_reviewer():
    """Register REVIEWER-001 agent in the coordinator state"""
    try:
        # Load current state
        state_file = Path("mcp-coordinator/state.json")
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        # Prepare agent registration data
        agent_data = {
            "agent_id": "reviewer-001",
            "role": "reviewer",
            "capabilities": [
                "code_review",
                "pr_creation",
                "quality_checking",
                "documentation_review",
                "best_practices"
            ],
            "status": "active",
            "registered_at": datetime.now().isoformat(),
            "last_heartbeat": datetime.now().isoformat(),
            "task_count": 0,
            "error_count": 0
        }
        
        # Update agents section
        if "agents" not in state:
            state["agents"] = {}
        
        state["agents"]["reviewer-001"] = agent_data
        
        # Update agent_health section
        if "agent_health" not in state:
            state["agent_health"] = {}
        
        state["agent_health"]["reviewer-001"] = {
            "last_heartbeat": datetime.now().isoformat(),
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_task_time": 0.0,
            "error_count": 0,
            "recovery_count": 0,
            "status": "active"
        }
        
        # Save updated state
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        print("✅ REVIEWER-001 agent registered successfully!")
        print(f"Agent ID: {agent_data['agent_id']}")
        print(f"Role: {agent_data['role']}")
        print(f"Capabilities: {', '.join(agent_data['capabilities'])}")
        print(f"Status: {agent_data['status']}")
        
        # Save registration file
        reg_file = Path("mcp-coordinator/reviewer-001-registration.json")
        with open(reg_file, 'w') as f:
            json.dump(agent_data, f, indent=2)
        
        print(f"\n💾 Registration saved to {reg_file}")
        
        # Check for available tasks
        reviewer_tasks = []
        for task in state.get("task_queue", []):
            if task.get("status") == "pending" and task.get("type") == "review":
                reviewer_tasks.append(task)
        
        if reviewer_tasks:
            print(f"\n📋 Found {len(reviewer_tasks)} review tasks waiting:")
            for task in reviewer_tasks[:3]:  # Show first 3
                print(f"  - {task['id']}: {task['description'][:60]}...")
        else:
            print("\n📋 No review tasks currently available")
        
        return True
        
    except Exception as e:
        print(f"❌ Error registering agent: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    register_reviewer()