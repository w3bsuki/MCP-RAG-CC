#!/usr/bin/env python3
"""Get next task for reviewer-001 agent from MCP coordinator"""

import json
from pathlib import Path
from datetime import datetime

def get_next_task():
    """Get next review task directly from state file"""
    try:
        # Load the coordinator state
        state_file = Path("mcp-coordinator/state.json")
        if not state_file.exists():
            print(f"Error: State file not found at {state_file}")
            return None
            
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        # Look for pending review tasks
        for task in state.get('task_queue', []):
            if (task.get('type') == 'review' and 
                task.get('status') == 'pending'):
                
                # Assign the task to reviewer-001
                task['status'] = 'in_progress'
                task['assigned_to'] = 'reviewer-001'
                task['updated_at'] = datetime.now().isoformat()
                
                # Save the updated state
                with open(state_file, 'w') as f:
                    json.dump(state, f, indent=2)
                
                print(f"✅ Task {task['id']} assigned to reviewer-001")
                return task
        
        print("No pending review tasks available")
        return None
        
    except Exception as e:
        print(f"Error getting task: {e}")
        return None

def main():
    print("Getting next task for reviewer-001...")
    
    # Get task directly from file
    task = get_next_task()
    
    if task:
        print(f"\n📋 Task Details:")
        print(f"ID: {task['id']}")
        print(f"Description: {task['description']}")
        print(f"Priority: {task.get('priority', 'normal')}")
        print(f"Type: {task['type']}")
        print(f"Status: {task['status']}")
        print(f"Assigned to: {task.get('assigned_to', 'reviewer-001')}")
        
        if 'context' in task:
            print(f"\n📝 Context:")
            print(json.dumps(task['context'], indent=2))
        
        # Save the task for reference
        with open("current_reviewer_task.json", 'w') as f:
            json.dump(task, f, indent=2)
        print(f"\n💾 Task saved to current_reviewer_task.json")
    else:
        print("\nNo review tasks available")

if __name__ == "__main__":
    main()