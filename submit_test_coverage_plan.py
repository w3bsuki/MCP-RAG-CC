#!/usr/bin/env python3
"""Submit test coverage improvement plan to coordinator"""

import json
from datetime import datetime
from pathlib import Path
import hashlib

def submit_plan():
    # Load the plan
    with open('test_coverage_plan.json', 'r') as f:
        plan = json.load(f)
    
    # Load current state
    state_file = Path("mcp-coordinator/state.json")
    with open(state_file, 'r') as f:
        state = json.load(f)
    
    # Create a new plan task
    task_id = f"task-plan-{int(datetime.now().timestamp())}"
    
    task = {
        "id": task_id,
        "type": "plan",
        "status": "completed",
        "created_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
        "assigned_to": "planner-001",
        "finding_id": plan["finding_id"],
        "description": f"Create implementation plan for: {plan['title']}",
        "priority": "medium",
        "result": {
            "plan": plan,
            "success": True
        },
        "updated_at": datetime.now().isoformat()
    }
    
    # Add task to state
    if "tasks" not in state:
        state["tasks"] = {}
    state["tasks"][task_id] = task
    
    # Update finding status
    if plan["finding_id"] in state.get("audit_findings", {}):
        state["audit_findings"][plan["finding_id"]]["status"] = "planning_complete"
        state["audit_findings"][plan["finding_id"]]["plan_id"] = plan["plan_id"]
        state["audit_findings"][plan["finding_id"]]["updated_at"] = datetime.now().isoformat()
    
    # Create implementation task for coder
    impl_task_id = f"task-impl-{int(datetime.now().timestamp())}"
    impl_task = {
        "id": impl_task_id,
        "type": "implementation",
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "assigned_to": "coder",
        "finding_id": plan["finding_id"],
        "plan_id": plan["plan_id"],
        "description": f"Implement: {plan['title']}",
        "priority": "medium",
        "details": {
            "plan": plan,
            "finding": state.get("audit_findings", {}).get(plan["finding_id"], {})
        },
        "updated_at": datetime.now().isoformat()
    }
    
    state["tasks"][impl_task_id] = impl_task
    
    # Save updated state
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
    
    print(f"✓ Plan submitted successfully!")
    print(f"  Plan ID: {plan['plan_id']}")
    print(f"  Task ID: {task_id}")
    print(f"  Implementation Task: {impl_task_id}")
    print(f"\nPlan Summary:")
    print(f"  Title: {plan['title']}")
    print(f"  Steps: {len(plan['implementation_steps'])}")
    print(f"  Estimated Time: {plan['estimated_total_time']}")
    print(f"\nImplementation task created for coder agent")

if __name__ == "__main__":
    submit_plan()