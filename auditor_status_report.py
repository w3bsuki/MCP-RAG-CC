#!/usr/bin/env python3
"""
Auditor Agent Status Report - Simulates MCP tool interactions
"""

import json
from pathlib import Path
from datetime import datetime

def get_auditor_status():
    """Get the complete status of the auditor agent and system"""
    
    print("=== AUDITOR AGENT STATUS REPORT ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # 1. Registration Status
    print("1. AGENT REGISTRATION STATUS:")
    state_file = Path("mcp-coordinator/state.json")
    if state_file.exists():
        with open(state_file) as f:
            state = json.load(f)
        
        auditor_data = state.get("agents", {}).get("auditor-001", {})
        if auditor_data:
            print("   ✅ Auditor agent is registered")
            print(f"   - Agent ID: {auditor_data.get('id')}")
            print(f"   - Role: {auditor_data.get('role')}")
            print(f"   - Status: {auditor_data.get('status')}")
            print(f"   - Registered at: {auditor_data.get('registered_at')}")
            print(f"   - Capabilities: {', '.join(auditor_data.get('capabilities', []))}")
        else:
            print("   ❌ Auditor agent not found in registry")
    
    # 2. Project Context
    print("\n2. PROJECT CONTEXT:")
    print(f"   - Total registered agents: {len(state.get('agents', {}))}")
    print(f"   - Active agents: {[aid for aid, agent in state.get('agents', {}).items() if agent.get('status') == 'active']}")
    print(f"   - Tasks in queue: {len([t for t in state.get('task_queue', []) if t.get('status') == 'pending'])}")
    print(f"   - Total audit findings: {len(state.get('audit_findings', []))}")
    
    # Analyze findings by severity
    findings = state.get('audit_findings', [])
    severity_count = {}
    category_count = {}
    for finding in findings:
        sev = finding.get('severity', 'unknown')
        cat = finding.get('category', 'unknown')
        severity_count[sev] = severity_count.get(sev, 0) + 1
        category_count[cat] = category_count.get(cat, 0) + 1
    
    print("\n   Findings by severity:")
    for sev, count in sorted(severity_count.items()):
        print(f"     - {sev}: {count}")
    
    print("\n   Findings by category:")
    for cat, count in sorted(category_count.items()):
        print(f"     - {cat}: {count}")
    
    # 3. Pending Tasks
    print("\n3. PENDING TASKS:")
    task_queue = state.get('task_queue', [])
    pending_tasks = [t for t in task_queue if t.get('status') == 'pending']
    
    if pending_tasks:
        print(f"   Found {len(pending_tasks)} pending tasks:")
        for i, task in enumerate(pending_tasks[:5]):  # Show first 5
            print(f"   {i+1}. {task.get('id')}")
            print(f"      Type: {task.get('type')}")
            print(f"      Priority: {task.get('priority')} (score: {task.get('priority_score', 0)})")
            print(f"      Description: {task.get('description')[:80]}...")
            if task.get('assigned_to'):
                print(f"      Assigned to: {task.get('assigned_to')}")
    else:
        print("   No pending tasks in queue")
    
    # 4. System Health
    print("\n4. SYSTEM HEALTH:")
    health = state.get('agent_health', {}).get('auditor-001', {})
    if health:
        print(f"   - Last heartbeat: {health.get('last_heartbeat', 'N/A')}")
        print(f"   - Tasks completed: {health.get('tasks_completed', 0)}")
        print(f"   - Tasks failed: {health.get('tasks_failed', 0)}")
        print(f"   - Error count: {health.get('error_count', 0)}")
    
    # 5. Recent Audit Activity
    print("\n5. RECENT AUDIT ACTIVITY:")
    completed_audit = next((t for t in task_queue if t.get('id') == 'audit-001' and t.get('status') == 'completed'), None)
    if completed_audit:
        print("   ✅ Initial audit completed")
        result = completed_audit.get('result', {})
        summary = result.get('findings_summary', {})
        print(f"   - Total findings: {result.get('audit_metadata', {}).get('total_findings', 0)}")
        print(f"   - Files analyzed: {result.get('audit_metadata', {}).get('files_analyzed', 0)}")
        print(f"   - Critical security issues: {len(result.get('critical_security_vulnerabilities', []))}")
        print(f"   - System health: {result.get('system_health_assessment', {}).get('overall_status', 'N/A')}")
    else:
        print("   ⏳ Initial audit pending or in progress")
    
    # 6. Next Recommended Action
    print("\n6. RECOMMENDED NEXT ACTION:")
    if pending_tasks:
        # Find highest priority task suitable for auditor
        audit_tasks = [t for t in pending_tasks if t.get('type') == 'audit' and not t.get('assigned_to')]
        if audit_tasks:
            next_task = sorted(audit_tasks, key=lambda x: x.get('priority_score', 0), reverse=True)[0]
            print(f"   - Take task: {next_task.get('id')}")
            print(f"   - Type: {next_task.get('type')}")
            print(f"   - Description: {next_task.get('description')}")
        else:
            print("   - No audit tasks available. Consider:")
            print("     • Perform follow-up audit on fixed issues")
            print("     • Deep-dive analysis on critical findings")
            print("     • Pattern analysis across codebase")
    else:
        print("   - Create new audit task for continuous monitoring")
    
    print("\n=== END OF STATUS REPORT ===")
    
    return {
        "registration_status": "registered" if auditor_data else "not_registered",
        "project_context": {
            "total_agents": len(state.get('agents', {})),
            "pending_tasks": len(pending_tasks),
            "total_findings": len(findings),
            "severity_breakdown": severity_count,
            "category_breakdown": category_count
        },
        "assigned_task": None  # Would be populated if task was assigned
    }

if __name__ == "__main__":
    status = get_auditor_status()