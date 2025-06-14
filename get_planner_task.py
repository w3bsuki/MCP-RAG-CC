#!/usr/bin/env python3
"""Get next task for planner agent"""

import json
import sys
from datetime import datetime
from pathlib import Path

def get_next_planner_task():
    """Get the next task for the planner agent"""
    state_file = Path("mcp-coordinator/state.json")
    
    if not state_file.exists():
        print("Error: Coordinator state file not found")
        return None
        
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
            
        # Find tasks for planner
        tasks = state.get("tasks", [])
        planner_task = None
        
        for task in tasks:
            if task.get("assigned_to") == "planner" and task.get("status") == "pending":
                planner_task = task
                break
                
        if planner_task:
            print(f"Found task for planner:")
            print(json.dumps(planner_task, indent=2))
            
            # Update task status to in_progress
            task["status"] = "in_progress"
            task["updated_at"] = datetime.now().isoformat()
            
            # Save updated state
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
                
            return planner_task
        else:
            print("No pending tasks found for planner")
            return None
            
    except Exception as e:
        print(f"Error reading state: {e}")
        return None

if __name__ == "__main__":
    task = get_next_planner_task()
    if task:
        sys.exit(0)
    else:
        sys.exit(1)