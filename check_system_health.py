#!/usr/bin/env python3
"""Check system health via MCP coordinator"""

import json
import subprocess
import sys
from datetime import datetime

def check_system_health():
    """Check the health of the MCP coordinator system"""
    print(f"🔍 Checking MCP Coordinator System Health at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # Check coordinator process
        result = subprocess.run(['pgrep', '-f', 'mcp-coordinator/server.py'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ MCP Coordinator process is running (PID: {})".format(result.stdout.strip()))
        else:
            print("❌ MCP Coordinator process is NOT running")
            
        # Check state file
        state_file = "/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/mcp-coordinator/state.json"
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
                
            print(f"\n📊 System State Summary:")
            print(f"   - Total Agents: {len(state.get('agents', {}))}")
            print(f"   - Total Tasks: {len(state.get('tasks', {}))}")
            print(f"   - Audit Findings: {len(state.get('findings', {}))}")
            
            # Count agents by role
            agents_by_role = {}
            for agent_id, agent_data in state.get('agents', {}).items():
                role = agent_data.get('role', 'unknown')
                agents_by_role[role] = agents_by_role.get(role, 0) + 1
                
            print(f"\n👥 Agents by Role:")
            for role, count in agents_by_role.items():
                print(f"   - {role}: {count}")
                
            # Count tasks by status
            tasks_by_status = {}
            for task_id, task_data in state.get('tasks', {}).items():
                status = task_data.get('status', 'unknown')
                tasks_by_status[status] = tasks_by_status.get(status, 0) + 1
                
            print(f"\n📋 Tasks by Status:")
            for status, count in tasks_by_status.items():
                print(f"   - {status}: {count}")
                
            # Show recent agents
            print(f"\n🕐 Recent Agent Activity:")
            recent_agents = sorted(
                state.get('agents', {}).items(),
                key=lambda x: x[1].get('last_seen', ''),
                reverse=True
            )[:5]
            
            for agent_id, agent_data in recent_agents:
                last_seen = agent_data.get('last_seen', 'Never')
                role = agent_data.get('role', 'unknown')
                status = agent_data.get('status', 'unknown')
                print(f"   - {agent_id} ({role}) - Status: {status}, Last seen: {last_seen}")
                
            # Show pending tasks
            print(f"\n📝 Pending Tasks:")
            pending_tasks = [
                (tid, tdata) for tid, tdata in state.get('tasks', {}).items()
                if tdata.get('status') == 'pending'
            ][:5]
            
            if pending_tasks:
                for task_id, task_data in pending_tasks:
                    task_type = task_data.get('type', 'unknown')
                    priority = task_data.get('priority', 'medium')
                    description = task_data.get('description', 'No description')[:60]
                    print(f"   - [{priority}] {task_type}: {description}...")
            else:
                print("   - No pending tasks")
                
        except FileNotFoundError:
            print("❌ State file not found")
        except json.JSONDecodeError:
            print("❌ State file is corrupted")
            
    except Exception as e:
        print(f"❌ Error checking system health: {e}")
        return False
        
    print("\n" + "=" * 80)
    return True

if __name__ == "__main__":
    success = check_system_health()
    sys.exit(0 if success else 1)