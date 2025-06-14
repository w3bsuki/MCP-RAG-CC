#!/usr/bin/env python3
"""
Test core coordinator logic without external dependencies
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the MCP imports
class MockTypes:
    class Tool:
        def __init__(self, **kwargs):
            self.name = kwargs.get('name')
            self.description = kwargs.get('description')
    
    class TextContent:
        def __init__(self, **kwargs):
            self.type = kwargs.get('type')
            self.text = kwargs.get('text')

class MockServer:
    def __init__(self, name):
        self.name = name
    
    def list_tools(self):
        def decorator(func):
            return func
        return decorator
    
    def call_tool(self):
        def decorator(func):
            return func
        return decorator

class MockInitOptions:
    def __init__(self, **kwargs):
        self.server_name = kwargs.get('server_name')
        self.server_version = kwargs.get('server_version')

# Mock modules
sys.modules['mcp'] = type(sys)('mcp')
sys.modules['mcp.types'] = MockTypes()
sys.modules['mcp.server'] = type(sys)('mcp.server')
sys.modules['mcp.server'].Server = MockServer
sys.modules['mcp.server.models'] = type(sys)('mcp.server.models')
sys.modules['mcp.server.models'].InitializationOptions = MockInitOptions
sys.modules['mcp.server.stdio'] = type(sys)('mcp.server.stdio')

# Now we can import our coordinator
from mcp_coordinator.server import EnhancedAgentCoordinator, TaskPriority, AgentStatus

def test_coordinator():
    """Test the enhanced coordinator functionality"""
    print("🧪 Testing Enhanced MCP Coordinator Logic")
    print("="*50)
    
    # Create coordinator
    coordinator = EnhancedAgentCoordinator()
    print("✅ Coordinator created")
    
    # Test 1: Agent Registration
    print("\n📋 Test 1: Agent Registration")
    agent = coordinator.register_agent(
        agent_id="test-auditor-001",
        role="auditor",
        capabilities=["code_analysis", "security_scanning"]
    )
    assert agent['id'] == "test-auditor-001"
    assert agent['role'] == "auditor"
    assert agent['status'] == AgentStatus.ACTIVE.value
    print("✅ Agent registration working")
    
    # Test 2: Task Creation with Priority
    print("\n📋 Test 2: Task Creation & Prioritization")
    
    # Create tasks with different priorities
    low_task = coordinator.create_task("test", "Low priority task", priority="low")
    high_task = coordinator.create_task("test", "High priority task", priority="high")
    critical_task = coordinator.create_task("test", "Critical task", priority="critical")
    
    # Check ordering
    queue_priorities = [t['priority'] for t in coordinator.task_queue[:3]]
    assert queue_priorities == ['critical', 'high', 'low'], f"Wrong order: {queue_priorities}"
    print("✅ Task prioritization working")
    
    # Test 3: Duplicate Finding Detection
    print("\n📋 Test 3: Duplicate Finding Detection")
    
    finding1 = coordinator.submit_audit_finding({
        'title': 'SQL Injection in login',
        'description': 'User input not sanitized',
        'severity': 'critical',
        'category': 'security',
        'file_path': 'auth.py',
        'line_number': 42
    })
    
    # Submit duplicate
    finding2 = coordinator.submit_audit_finding({
        'title': 'SQL Injection in login',  # Same issue
        'description': 'User input not sanitized',
        'severity': 'critical',
        'category': 'security',
        'file_path': 'auth.py',
        'line_number': 42
    })
    
    assert finding1['status'] == 'new'
    assert finding2['status'] == 'duplicate'
    print("✅ Duplicate detection working")
    
    # Test 4: Task Assignment & Load Balancing
    print("\n📋 Test 4: Task Assignment")
    
    # Get task for auditor
    task = coordinator.get_next_task("test-auditor-001", "auditor")
    assert task is None  # No audit tasks available
    
    # Get task for planner (should get the finding task)
    planner = coordinator.register_agent("test-planner-001", "planner", ["planning"])
    task = coordinator.get_next_task("test-planner-001", "planner")
    assert task is not None
    assert task['type'] == 'plan'
    assert 'SQL Injection' in task['description']
    print("✅ Task assignment working")
    
    # Test 5: Task Retry Logic
    print("\n📋 Test 5: Task Retry Logic")
    
    # Fail the task
    coordinator.update_task(task['id'], "failed")
    
    # Check it's back to pending
    updated_task = next(t for t in coordinator.task_queue if t['id'] == task['id'])
    assert updated_task['status'] == 'pending'
    assert updated_task['retry_count'] == 1
    print("✅ Retry logic working")
    
    # Test 6: Health Monitoring
    print("\n📋 Test 6: Agent Health Monitoring")
    
    health = coordinator.get_agent_health_report("test-auditor-001")
    assert health['agent_id'] == "test-auditor-001"
    assert health['health'] in ['good', 'fair', 'poor', 'critical']
    assert 'metrics' in health
    print("✅ Health monitoring working")
    
    # Test 7: System Health
    print("\n📋 Test 7: System Health Check")
    
    system_health = coordinator.get_system_health()
    assert 'agents' in system_health
    assert 'tasks' in system_health
    assert 'findings' in system_health
    assert system_health['agents']['total'] == 2  # auditor + planner
    print("✅ System health check working")
    
    # Test 8: Context Enhancement
    print("\n📋 Test 8: RAG Context Features")
    
    # Create a task with description
    task_with_context = coordinator.create_task(
        "implement",
        "Fix SQL injection vulnerability in user authentication",
        context={"test": True}
    )
    
    # Check context was enhanced
    assert 'related_findings' in task_with_context['context']
    assert 'similar_tasks' in task_with_context['context']
    print("✅ Context enhancement working")
    
    # Test 9: Pattern Recognition
    print("\n📋 Test 9: Pattern Recognition")
    
    # Submit more findings to create patterns
    for i in range(3):
        coordinator.submit_audit_finding({
            'title': f'Another security issue {i}',
            'description': 'Security problem',
            'severity': 'high',
            'category': 'security',
            'file_path': f'file{i}.py',
            'line_number': i
        })
    
    # Check patterns
    assert len(coordinator.finding_patterns) > 0
    security_pattern_count = coordinator.finding_patterns.get('security:high', 0)
    assert security_pattern_count >= 3
    print("✅ Pattern recognition working")
    
    # Summary
    print("\n" + "="*50)
    print("✅ All core logic tests passed!")
    print(f"📊 Final Stats:")
    print(f"   Agents: {len(coordinator.agents)}")
    print(f"   Tasks: {len(coordinator.task_queue)}")
    print(f"   Findings: {len(coordinator.audit_findings)}")
    print(f"   Patterns: {len(coordinator.finding_patterns)}")
    
    return True

if __name__ == "__main__":
    try:
        test_coordinator()
        print("\n🎉 Coordinator logic verified successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)