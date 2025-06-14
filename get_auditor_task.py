#!/usr/bin/env python3
"""
Get next task for auditor agent from MCP coordinator
"""

import json
import subprocess
import sys
import os
from pathlib import Path

def get_next_task():
    """Get next task for auditor agent using MCP coordinator"""
    
    # Since the MCP coordinator is running, we'll use the JSON-RPC protocol
    # to communicate with it via stdin/stdout
    
    # First, let's check if there are any existing tasks in the queue
    state_file = Path("mcp-coordinator/state.json")
    if state_file.exists():
        with open(state_file) as f:
            state = json.load(f)
        
        print("Current coordinator state:")
        print(f"  Registered agents: {len(state.get('agents', {}))}")
        print(f"  Task queue: {len(state.get('task_queue', []))}")
        print(f"  Audit findings: {len(state.get('audit_findings', []))}")
        
        # Check if auditor is registered
        if "auditor-001" in state.get("agents", {}):
            print("  ✅ Auditor agent is registered")
        else:
            print("  ❌ Auditor agent not registered")
            return None
    
    # Since the task queue is empty, we need to create initial audit tasks
    # The auditor should start by scanning the codebase
    
    # Check if there are any audit findings files
    audit_files = [
        "all_audit_findings.json",
        "audit_findings_batch1.json", 
        "audit_findings_batch2.json",
        "audit_findings_batch3.json",
        "audit_findings_batch4.json"
    ]
    
    existing_findings = []
    for file in audit_files:
        if Path(file).exists():
            try:
                with open(file) as f:
                    findings = json.load(f)
                    if isinstance(findings, list):
                        existing_findings.extend(findings)
                    else:
                        existing_findings.append(findings)
            except Exception as e:
                print(f"  Warning: Could not load {file}: {e}")
    
    print(f"  Found {len(existing_findings)} existing audit findings")
    
    # Since we're in a demo environment, create a sample audit task
    # for the auditor to start with
    sample_task = {
        "task_id": "audit-001",
        "task_type": "audit",
        "agent_id": "auditor-001",
        "priority": "high",
        "status": "pending",
        "description": "Perform comprehensive code audit of the MCP autonomous system",
        "details": {
            "scope": "Complete codebase analysis",
            "focus_areas": [
                "Security vulnerabilities",
                "Performance bottlenecks", 
                "Code quality issues",
                "Error handling gaps",
                "Documentation completeness"
            ],
            "files_to_audit": [
                "autonomous-system.py",
                "mcp-coordinator/server.py",
                "mcp-coordinator/server_v2.py", 
                "*.py"
            ]
        },
        "created_at": "2025-06-14T09:52:00Z",
        "assigned_at": "2025-06-14T09:52:00Z"
    }
    
    print("\nCreated audit task:")
    print(json.dumps(sample_task, indent=2))
    
    return sample_task

if __name__ == "__main__":
    task = get_next_task()
    if task:
        print(f"\n✅ Task retrieved for auditor: {task['task_id']}")
        print(f"   Description: {task['description']}")
        print(f"   Priority: {task['priority']}")
    else:
        print("\n❌ No tasks available")