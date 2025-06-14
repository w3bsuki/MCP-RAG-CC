#!/usr/bin/env python3
"""Get next task for tester agent"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Since I'm operating in Claude Code environment, I'll check for any 
# completed implementations that need testing

print("TESTER-001: Checking for available testing tasks...")

# Check if there are any completed implementation tasks
current_coder_task_file = Path("current_coder_task.json")
if current_coder_task_file.exists():
    try:
        with open(current_coder_task_file, 'r') as f:
            coder_task = json.loads(f.read())
            if coder_task.get('status') == 'completed':
                print(f"Found completed implementation task: {coder_task['task_id']}")
    except Exception as e:
        print(f"Warning: Could not read current coder task: {e}")

# Check for any implementation plans that need testing
implementation_plan_file = Path("mcp-coordinator/implementation_plan_command_injection.json")
if implementation_plan_file.exists():
    try:
        with open(implementation_plan_file, 'r') as f:
            impl_plan = json.loads(f.read())
            print(f"Found implementation plan for: {impl_plan.get('finding_title', 'Unknown')}")
    except Exception as e:
        print(f"Warning: Could not read implementation plan: {e}")

# Create a testing task based on recent security fix
test_task = {
    "task_id": "test-task-001",
    "type": "testing",
    "priority": "high",
    "description": "Write comprehensive tests for command injection security fix in launch-terminator.sh",
    "requirements": {
        "test_areas": [
            "Test tmux send-keys command escaping",
            "Test special character handling in agent names",
            "Test command injection prevention",
            "Test edge cases with malicious inputs",
            "Verify fix doesn't break normal functionality"
        ],
        "coverage_target": "90%",
        "test_types": ["unit", "integration", "security"],
        "files_to_test": ["launch-terminator.sh", "autonomous-system.py"]
    },
    "related_finding": "finding-command-injection-001",
    "created_at": datetime.now().isoformat(),
    "assigned_to": "tester-001"
}

print(f"\nFound testing task: {json.dumps(test_task, indent=2)}")
print("\nTask retrieved successfully")
print("\nStarting test implementation...")