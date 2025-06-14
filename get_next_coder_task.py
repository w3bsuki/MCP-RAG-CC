#!/usr/bin/env python3
"""Get next task for CODER-2 agent from MCP coordinator"""

import json
from pathlib import Path
from datetime import datetime

def get_next_task():
    """Get the next pending implementation task for a coder"""
    try:
        # Load the coordinator state
        state_file = Path("mcp-coordinator/state.json")
        if not state_file.exists():
            print(f"Error: State file not found at {state_file}")
            return None
            
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        # Look for pending implementation tasks
        for task in state.get('task_queue', []):
            if (task.get('type') == 'implementation' and 
                task.get('status') == 'pending'):
                
                # Assign the task to CODER-2
                task['status'] = 'in_progress'
                task['assigned_to'] = 'CODER-2'
                task['updated_at'] = datetime.now().isoformat()
                
                # Save the updated state
                with open(state_file, 'w') as f:
                    json.dump(state, f, indent=2)
                
                print(f"✅ Task {task['id']} assigned to CODER-2")
                return task
        
        print("No pending implementation tasks available")
        return None
        
    except Exception as e:
        print(f"Error getting task: {e}")
        return None

def main():
    print("Getting next task for CODER-2...")
    task = get_next_task()
    
    if task:
        print(f"\n📋 Task Details:")
        print(f"ID: {task['id']}")
        print(f"Description: {task['description']}")
        print(f"Priority: {task['priority']}")
        print(f"Type: {task['type']}")
        
        if 'context' in task and 'plan' in task['context']:
            plan = task['context']['plan']
            print(f"\n📝 Implementation Plan:")
            print(f"Finding ID: {plan.get('finding_id', 'N/A')}")
            print(f"Title: {plan.get('title', 'N/A')}")
            print(f"\nSteps:")
            for step in plan.get('steps', []):
                print(f"  - {step}")
        
        # Save the task for reference
        with open("current_task.json", 'w') as f:
            json.dump(task, f, indent=2)
        print(f"\n💾 Task saved to current_task.json")
    else:
        print("\nNo tasks available")

if __name__ == "__main__":
    main()