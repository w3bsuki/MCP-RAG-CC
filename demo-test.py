#!/usr/bin/env python3
"""
Demo Test - Simulates the MCP+RAG system functionality
Shows how the system would work with all dependencies installed
"""

import json
import time
from datetime import datetime
from pathlib import Path
import random

class DemoMCPCoordinator:
    """Simulated MCP Coordinator for demonstration"""
    
    def __init__(self):
        self.agents = {}
        self.task_queue = []
        self.audit_findings = []
        self.task_counter = 0
        self.finding_counter = 0
        
    def register_agent(self, agent_id: str, role: str, capabilities: list):
        """Register an agent"""
        self.agents[agent_id] = {
            'id': agent_id,
            'role': role,
            'capabilities': capabilities,
            'status': 'active',
            'registered_at': datetime.now().isoformat()
        }
        return self.agents[agent_id]
    
    def submit_audit_finding(self, finding: dict):
        """Submit an audit finding"""
        self.finding_counter += 1
        finding['id'] = f"finding-{self.finding_counter}"
        finding['submitted_at'] = datetime.now().isoformat()
        self.audit_findings.append(finding)
        
        # Auto-create planning task
        self.task_counter += 1
        task = {
            'id': f"task-{self.task_counter}",
            'type': 'plan',
            'description': f"Create plan for: {finding['title']}",
            'priority': finding['severity'],
            'status': 'pending',
            'finding_id': finding['id']
        }
        self.task_queue.append(task)
        
        return finding
    
    def get_next_task(self, agent_id: str, role: str):
        """Get next suitable task for agent"""
        for task in self.task_queue:
            if task['status'] == 'pending' and self._is_suitable(task, role):
                task['status'] = 'in_progress'
                task['assigned_to'] = agent_id
                return task
        return None
    
    def _is_suitable(self, task, role):
        """Check if task is suitable for role"""
        role_mapping = {
            'planner': ['plan'],
            'coder': ['implement', 'fix'],
            'tester': ['test'],
            'reviewer': ['review']
        }
        return task['type'] in role_mapping.get(role, [])
    
    def update_task(self, task_id: str, status: str, result=None):
        """Update task status"""
        for task in self.task_queue:
            if task['id'] == task_id:
                task['status'] = status
                if result:
                    task['result'] = result
                return task
        return None

def run_demo():
    """Run a demonstration of the system"""
    print("🎭 MCP+RAG System Demonstration")
    print("="*50)
    print("This demo simulates how the system works\n")
    
    # Create coordinator
    coordinator = DemoMCPCoordinator()
    
    # Phase 1: Agent Registration
    print("📋 Phase 1: Agent Registration")
    print("-"*30)
    
    agents = [
        ("auditor-001", "auditor", ["code_analysis", "security_scanning"]),
        ("planner-001", "planner", ["architecture", "task_breakdown"]),
        ("coder-001", "coder", ["implementation", "refactoring"]),
        ("tester-001", "tester", ["unit_testing", "integration_testing"]),
        ("reviewer-001", "reviewer", ["code_review", "pr_approval"])
    ]
    
    for agent_id, role, capabilities in agents:
        agent = coordinator.register_agent(agent_id, role, capabilities)
        print(f"✅ Registered {role}: {agent_id}")
        time.sleep(0.5)
    
    print(f"\nTotal agents registered: {len(coordinator.agents)}")
    
    # Phase 2: Auditor finds issues
    print("\n📋 Phase 2: Auditor Scans Codebase")
    print("-"*30)
    
    findings = [
        {
            'title': 'SQL Injection Vulnerability',
            'description': 'User input not sanitized in login function',
            'severity': 'critical',
            'category': 'security',
            'file_path': 'auth/login.py',
            'line_number': 45
        },
        {
            'title': 'N+1 Query Problem',
            'description': 'Inefficient database queries in user listing',
            'severity': 'high',
            'category': 'performance',
            'file_path': 'api/users.py',
            'line_number': 78
        },
        {
            'title': 'Missing Test Coverage',
            'description': 'Payment module has only 40% test coverage',
            'severity': 'medium',
            'category': 'testing',
            'file_path': 'payments/processor.py',
            'line_number': None
        }
    ]
    
    for finding in findings:
        result = coordinator.submit_audit_finding(finding)
        print(f"🔍 Found: {finding['title']} ({finding['severity']})")
        time.sleep(0.5)
    
    print(f"\nTotal findings: {len(coordinator.audit_findings)}")
    print(f"Tasks created: {len(coordinator.task_queue)}")
    
    # Phase 3: Planner creates plans
    print("\n📋 Phase 3: Planner Creates Implementation Plans")
    print("-"*30)
    
    planner_id = "planner-001"
    plans_created = 0
    
    while True:
        task = coordinator.get_next_task(planner_id, "planner")
        if not task:
            break
        
        print(f"📝 Planning: {task['description']}")
        time.sleep(1)
        
        # Simulate planning
        plan = {
            'steps': [
                'Analyze current implementation',
                'Design secure solution',
                'Implement fixes',
                'Add comprehensive tests',
                'Update documentation'
            ],
            'estimated_hours': random.randint(2, 8)
        }
        
        coordinator.update_task(task['id'], 'completed', plan)
        
        # Create implementation tasks
        coordinator.task_counter += 1
        impl_task = {
            'id': f"task-{coordinator.task_counter}",
            'type': 'implement',
            'description': f"Implement fix for: {task['description']}",
            'priority': task['priority'],
            'status': 'pending',
            'plan': plan
        }
        coordinator.task_queue.append(impl_task)
        
        plans_created += 1
        print(f"✅ Plan created with {len(plan['steps'])} steps")
    
    print(f"\nPlans created: {plans_created}")
    
    # Phase 4: Show system status
    print("\n📋 Phase 4: System Status")
    print("-"*30)
    
    # Count task statuses
    status_count = {}
    for task in coordinator.task_queue:
        status = task['status']
        status_count[status] = status_count.get(status, 0) + 1
    
    print("Task Queue Status:")
    for status, count in status_count.items():
        print(f"  {status}: {count}")
    
    print("\nAgent Status:")
    for agent_id, agent in coordinator.agents.items():
        assigned_tasks = sum(1 for t in coordinator.task_queue 
                           if t.get('assigned_to') == agent_id)
        print(f"  {agent['role']}: {agent_id} - {assigned_tasks} tasks")
    
    # Phase 5: Demonstrate RAG features
    print("\n📋 Phase 5: RAG Intelligence Features")
    print("-"*30)
    
    # Pattern recognition
    patterns = {}
    for finding in coordinator.audit_findings:
        pattern = f"{finding['category']}:{finding['severity']}"
        patterns[pattern] = patterns.get(pattern, 0) + 1
    
    print("Pattern Recognition:")
    for pattern, count in patterns.items():
        print(f"  {pattern}: {count} occurrences")
    
    # Similar findings
    print("\nSimilar Finding Detection:")
    test_finding = {
        'title': 'Another SQL Injection',
        'category': 'security',
        'severity': 'critical'
    }
    
    similar = [f for f in coordinator.audit_findings 
               if f['category'] == test_finding['category']]
    
    if similar:
        print(f"  Found {len(similar)} similar security issues")
        print("  System would suggest unified fix approach")
    
    # Performance metrics
    print("\nPerformance Metrics:")
    print(f"  Findings processed: {len(coordinator.audit_findings)}")
    print(f"  Tasks created: {len(coordinator.task_queue)}")
    print(f"  Avg response time: {random.uniform(0.1, 0.5):.2f}s")
    
    print("\n✨ Demo Complete!")
    print("="*50)
    print("\nIn a real deployment:")
    print("- Agents would run continuously in tmux sessions")
    print("- MCP protocol would handle all communication")
    print("- Git worktrees would isolate changes")
    print("- Health monitoring would ensure reliability")
    print("- RAG would provide intelligent context")

if __name__ == "__main__":
    run_demo()