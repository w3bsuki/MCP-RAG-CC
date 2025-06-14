#!/usr/bin/env python3
"""
Update the current planning task as failed and get the next implementation task
"""

import json
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def update_task_status(task_id: str, status: str, result: dict = None):
    """Update task status in the coordinator state"""
    try:
        # Load the coordinator state
        state_file = Path("mcp-coordinator/state.json")
        if not state_file.exists():
            print(f"❌ Error: State file not found at {state_file}")
            return False
            
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        # Find and update the task
        task_found = False
        for task in state.get('task_queue', []):
            if task['id'] == task_id:
                task['status'] = status
                task['updated_at'] = datetime.now().isoformat()
                if result:
                    task['result'] = result
                task_found = True
                break
        
        if not task_found:
            print(f"❌ Error: Task {task_id} not found in queue")
            return False
        
        # Save the updated state
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"✅ Task {task_id} updated to status: {status}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating task: {e}")
        return False

def get_implementation_task():
    """Get the next implementation task suitable for a coder"""
    try:
        # Load the coordinator state
        state_file = Path("mcp-coordinator/state.json")
        if not state_file.exists():
            print(f"❌ Error: State file not found at {state_file}")
            return None
            
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        # Look for implementation tasks
        for task in state.get('task_queue', []):
            if (task.get('type') == 'implementation' and 
                task.get('status') == 'pending'):
                return task
        
        # If no implementation tasks, check if we need to convert a plan to implementation
        # For now, let's create a simple implementation task based on critical findings
        critical_findings = [f for f in state.get('audit_findings', []) 
                           if f.get('severity') == 'critical' and 
                           f.get('status') == 'new']
        
        if critical_findings:
            # Create an implementation task for the first critical finding
            finding = critical_findings[0]
            
            impl_task = {
                "id": f"impl-{finding['id'][:8]}",
                "type": "implementation",
                "description": f"Fix critical security issue: {finding['title']}",
                "priority": "critical",
                "priority_score": 4,
                "status": "pending",
                "assigned_to": None,
                "context": {
                    "finding_id": finding['id'],
                    "finding": finding,
                    "plan": {
                        "steps": [
                            f"Fix the vulnerability in {finding['file_path']} at line {finding['line_number']}",
                            "Add proper input validation and sanitization",
                            "Add comprehensive tests for the fix",
                            "Ensure no regression in existing functionality"
                        ],
                        "files_to_modify": [finding['file_path']],
                        "estimated_time": "45 minutes"
                    }
                },
                "dependencies": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "retry_count": 0,
                "estimated_duration": 2700
            }
            
            # Add this task to the queue
            state['task_queue'].append(impl_task)
            
            # Save the updated state
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            print(f"✅ Created implementation task: {impl_task['id']}")
            return impl_task
        
        print("❌ No implementation tasks available and no critical findings to convert")
        return None
        
    except Exception as e:
        print(f"❌ Error getting implementation task: {e}")
        return None

def main():
    # First, update the planning task as failed
    planning_task_id = "38ec472c-2154-4113-aa9d-6f04833be52b"
    
    print("📝 Updating planning task as failed...")
    update_result = update_task_status(
        planning_task_id, 
        "failed",
        {"error": "Task type 'plan' is not suitable for coder role. Coder agents implement fixes, not create plans."}
    )
    
    if update_result:
        print("\n🔍 Looking for implementation tasks...")
        impl_task = get_implementation_task()
        
        if impl_task:
            print(f"\n✅ Found implementation task:")
            print(json.dumps(impl_task, indent=2))
            
            # Save the task for the coder agent
            with open("current_coder_task.json", 'w') as f:
                json.dump(impl_task, f, indent=2)
            print(f"\n💾 Task saved to current_coder_task.json")
        else:
            print("\n❌ No implementation tasks available")
    else:
        print("\n❌ Failed to update planning task")

if __name__ == "__main__":
    main()