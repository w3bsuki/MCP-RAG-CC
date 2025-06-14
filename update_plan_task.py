#!/usr/bin/env python3
"""Update plan task status and create implementation task"""

import json
from datetime import datetime
from pathlib import Path

def update_task():
    # Load the plan
    with open('command_injection_plan.json', 'r') as f:
        plan = json.load(f)
    
    # Load current state
    state_file = Path("mcp-coordinator/state.json")
    with open(state_file, 'r') as f:
        state = json.load(f)
    
    # Find and update the task
    task_queue = state.get('task_queue', [])
    task_updated = False
    
    for i, task in enumerate(task_queue):
        if task['id'] == plan['task_id']:
            # Update task to completed
            task['status'] = 'completed'
            task['completed_at'] = datetime.now().isoformat()
            task['updated_at'] = datetime.now().isoformat()
            task['result'] = {
                'success': True,
                'plan': plan
            }
            # Remove the error from failed attempt
            if 'error' in task.get('result', {}):
                del task['result']['error']
            
            task_updated = True
            print(f"✓ Updated task {task['id']} to completed")
            break
    
    if not task_updated:
        print("⚠ Task not found in queue")
        return
    
    # Create implementation task
    impl_task = {
        "id": f"impl-{plan['finding_id'][:8]}-{int(datetime.now().timestamp())}",
        "type": "implementation",
        "description": f"Implement fix for: {plan['title']}",
        "priority": "critical",
        "priority_score": 4,
        "status": "pending",
        "assigned_to": None,  # Will be picked up by coder
        "context": {
            "finding_id": plan['finding_id'],
            "plan_id": plan['plan_id'],
            "plan": plan,
            "file_path": "autonomous-system.py",
            "line_number": 277
        },
        "dependencies": [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "retry_count": 0,
        "estimated_duration": int(3.5 * 3600)  # 3.5 hours in seconds
    }
    
    # Add to task queue
    task_queue.append(impl_task)
    
    # Update agent status to show work completed
    if 'agents' in state and 'planner-001' in state['agents']:
        state['agents']['planner-001']['last_seen'] = datetime.now().isoformat()
        state['agents']['planner-001']['tasks_completed'] = state['agents']['planner-001'].get('tasks_completed', 0) + 1
    
    # Save state with plan stored
    plans_dir = Path("mcp-coordinator/plans")
    plans_dir.mkdir(exist_ok=True)
    plan_file = plans_dir / f"{plan['plan_id']}.json"
    with open(plan_file, 'w') as f:
        json.dump(plan, f, indent=2)
    
    # Save updated state
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
    
    print(f"✓ Created implementation task: {impl_task['id']}")
    print(f"✓ Saved plan to: {plan_file}")
    print(f"\nPlan Summary:")
    print(f"  Title: {plan['title']}")
    print(f"  Steps: {len(plan['implementation_steps'])}")
    print(f"  Estimated Time: {plan['estimated_total_time']}")
    print(f"\nImplementation task is ready for coder agent")

if __name__ == "__main__":
    update_task()