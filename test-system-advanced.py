#!/usr/bin/env python3
"""
Advanced System Testing Suite
Tests edge cases, failure scenarios, and system resilience
"""

import asyncio
import json
import sys
import subprocess
import time
import os
from pathlib import Path
from datetime import datetime
import logging
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test-suite")

class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.message = ""
        self.duration = 0.0
        self.details = {}

class AdvancedTestSuite:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.results = []
        self.test_data_dir = self.base_dir / "test-data"
        self.test_data_dir.mkdir(exist_ok=True)
    
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧪 Advanced MCP+RAG System Test Suite")
        print("="*50)
        
        test_categories = [
            ("System Requirements", self.test_system_requirements),
            ("MCP Server", self.test_mcp_server),
            ("Error Handling", self.test_error_handling),
            ("Performance", self.test_performance),
            ("Concurrency", self.test_concurrency),
            ("Recovery", self.test_recovery),
            ("Edge Cases", self.test_edge_cases),
            ("Integration", self.test_integration)
        ]
        
        for category, test_func in test_categories:
            print(f"\n📋 Testing {category}...")
            try:
                await test_func()
            except Exception as e:
                logger.error(f"Test category {category} failed: {e}")
        
        # Generate report
        self.generate_report()
    
    async def test_system_requirements(self):
        """Test system requirements and dependencies"""
        tests = []
        
        # Test 1: Python version
        result = TestResult("Python Version Check")
        start = time.time()
        try:
            import sys
            version = sys.version_info
            if version.major >= 3 and version.minor >= 8:
                result.passed = True
                result.message = f"Python {version.major}.{version.minor}.{version.micro}"
            else:
                result.message = f"Python {version.major}.{version.minor} (need 3.8+)"
        except Exception as e:
            result.message = str(e)
        result.duration = time.time() - start
        tests.append(result)
        
        # Test 2: Required packages with versions
        packages = {
            'mcp': 'MCP SDK',
            'psutil': 'System monitoring',
            'asyncio': 'Async support'
        }
        
        for package, description in packages.items():
            result = TestResult(f"{description} ({package})")
            start = time.time()
            try:
                module = __import__(package)
                version = getattr(module, '__version__', 'installed')
                result.passed = True
                result.message = f"Version: {version}"
            except ImportError:
                result.message = "Not installed"
            result.duration = time.time() - start
            tests.append(result)
        
        # Test 3: System commands
        commands = ['tmux', 'git', 'claude']
        for cmd in commands:
            result = TestResult(f"Command: {cmd}")
            start = time.time()
            try:
                subprocess.run([cmd, '--version'], capture_output=True, check=True)
                result.passed = True
                result.message = "Available"
            except:
                result.message = "Not found"
            result.duration = time.time() - start
            tests.append(result)
        
        self.results.extend(tests)
    
    async def test_mcp_server(self):
        """Test MCP server functionality"""
        tests = []
        
        # Test 1: Server startup
        result = TestResult("MCP Server Startup")
        start = time.time()
        try:
            # Try importing and creating server instance
            from mcp.server import Server
            from mcp.server.models import InitializationOptions
            
            server = Server("test-server")
            result.passed = True
            result.message = "Server instance created"
        except Exception as e:
            result.message = f"Failed: {str(e)}"
        result.duration = time.time() - start
        tests.append(result)
        
        # Test 2: Coordinator class
        result = TestResult("Coordinator Initialization")
        start = time.time()
        try:
            # Import and test coordinator
            sys.path.insert(0, str(self.base_dir))
            from mcp_coordinator.server import EnhancedAgentCoordinator
            
            coordinator = EnhancedAgentCoordinator()
            result.passed = True
            result.message = "Coordinator initialized"
            result.details = {
                'data_dir': str(coordinator.data_dir),
                'max_retries': coordinator.max_retries
            }
        except Exception as e:
            result.message = f"Failed: {str(e)}"
        result.duration = time.time() - start
        tests.append(result)
        
        # Test 3: State persistence
        result = TestResult("State Persistence")
        start = time.time()
        try:
            test_state = {
                'test': True,
                'timestamp': datetime.now().isoformat()
            }
            
            state_file = self.test_data_dir / "test_state.json"
            with open(state_file, 'w') as f:
                json.dump(test_state, f)
            
            with open(state_file, 'r') as f:
                loaded = json.load(f)
            
            if loaded['test'] == True:
                result.passed = True
                result.message = "State save/load working"
            else:
                result.message = "State mismatch"
                
            state_file.unlink()  # Cleanup
            
        except Exception as e:
            result.message = f"Failed: {str(e)}"
        result.duration = time.time() - start
        tests.append(result)
        
        self.results.extend(tests)
    
    async def test_error_handling(self):
        """Test error handling and recovery"""
        tests = []
        
        # Test 1: Invalid task handling
        result = TestResult("Invalid Task Handling")
        start = time.time()
        try:
            from mcp_coordinator.server import EnhancedAgentCoordinator
            coordinator = EnhancedAgentCoordinator()
            
            # Try updating non-existent task
            try:
                coordinator.update_task("non-existent-id", "completed")
                result.message = "Should have raised error"
            except ValueError as e:
                if "Task not found" in str(e):
                    result.passed = True
                    result.message = "Correctly raised ValueError"
                else:
                    result.message = f"Wrong error: {e}"
            
        except Exception as e:
            result.message = f"Setup failed: {str(e)}"
        result.duration = time.time() - start
        tests.append(result)
        
        # Test 2: Duplicate finding detection
        result = TestResult("Duplicate Finding Detection")
        start = time.time()
        try:
            from mcp_coordinator.server import EnhancedAgentCoordinator
            coordinator = EnhancedAgentCoordinator()
            
            finding = {
                'title': 'Test Finding',
                'description': 'Test',
                'severity': 'low',
                'category': 'test',
                'file_path': 'test.py',
                'line_number': 42
            }
            
            # Submit twice
            first = coordinator.submit_audit_finding(finding.copy())
            second = coordinator.submit_audit_finding(finding.copy())
            
            if second['status'] == 'duplicate':
                result.passed = True
                result.message = "Duplicate correctly detected"
            else:
                result.message = "Duplicate not detected"
                
        except Exception as e:
            result.message = f"Failed: {str(e)}"
        result.duration = time.time() - start
        tests.append(result)
        
        # Test 3: Retry logic
        result = TestResult("Task Retry Logic")
        start = time.time()
        try:
            from mcp_coordinator.server import EnhancedAgentCoordinator
            coordinator = EnhancedAgentCoordinator()
            
            # Create and fail a task multiple times
            task = coordinator.create_task("test", "Test retry logic")
            task_id = task['id']
            
            # Fail it
            coordinator.update_task(task_id, "failed")
            updated = next(t for t in coordinator.task_queue if t['id'] == task_id)
            
            if updated['status'] == 'pending' and updated['retry_count'] == 1:
                result.passed = True
                result.message = "Task correctly reset for retry"
                result.details = {'retry_count': updated['retry_count']}
            else:
                result.message = f"Unexpected state: {updated['status']}"
                
        except Exception as e:
            result.message = f"Failed: {str(e)}"
        result.duration = time.time() - start
        tests.append(result)
        
        self.results.extend(tests)
    
    async def test_performance(self):
        """Test system performance"""
        tests = []
        
        # Test 1: Task creation performance
        result = TestResult("Task Creation Performance")
        start = time.time()
        try:
            from mcp_coordinator.server import EnhancedAgentCoordinator
            coordinator = EnhancedAgentCoordinator()
            
            num_tasks = 100
            task_start = time.time()
            
            for i in range(num_tasks):
                coordinator.create_task(
                    task_type="test",
                    description=f"Performance test task {i}",
                    priority=random.choice(['low', 'medium', 'high'])
                )
            
            duration = time.time() - task_start
            tasks_per_second = num_tasks / duration
            
            if tasks_per_second > 50:  # Should create >50 tasks/second
                result.passed = True
                result.message = f"{tasks_per_second:.1f} tasks/second"
            else:
                result.message = f"Too slow: {tasks_per_second:.1f} tasks/second"
                
            result.details = {
                'total_tasks': num_tasks,
                'duration': duration,
                'rate': tasks_per_second
            }
            
        except Exception as e:
            result.message = f"Failed: {str(e)}"
        result.duration = time.time() - start
        tests.append(result)
        
        # Test 2: Memory usage
        result = TestResult("Memory Usage")
        start = time.time()
        try:
            import psutil
            process = psutil.Process()
            
            initial_memory = process.memory_info().rss / (1024 * 1024)  # MB
            
            # Create many objects
            from mcp_coordinator.server import EnhancedAgentCoordinator
            coordinators = []
            for i in range(10):
                coordinators.append(EnhancedAgentCoordinator())
            
            final_memory = process.memory_info().rss / (1024 * 1024)  # MB
            memory_increase = final_memory - initial_memory
            
            if memory_increase < 100:  # Should use less than 100MB for 10 instances
                result.passed = True
                result.message = f"Memory increase: {memory_increase:.1f}MB"
            else:
                result.message = f"High memory usage: {memory_increase:.1f}MB"
                
            result.details = {
                'initial_mb': initial_memory,
                'final_mb': final_memory,
                'increase_mb': memory_increase
            }
            
        except Exception as e:
            result.message = f"Failed: {str(e)}"
        result.duration = time.time() - start
        tests.append(result)
        
        self.results.extend(tests)
    
    async def test_concurrency(self):
        """Test concurrent operations"""
        tests = []
        
        # Test 1: Concurrent task creation
        result = TestResult("Concurrent Task Creation")
        start = time.time()
        try:
            from mcp_coordinator.server import EnhancedAgentCoordinator
            coordinator = EnhancedAgentCoordinator()
            
            async def create_tasks(prefix: str, count: int):
                tasks = []
                for i in range(count):
                    task = coordinator.create_task(
                        task_type="test",
                        description=f"{prefix} task {i}"
                    )
                    tasks.append(task)
                return tasks
            
            # Create tasks concurrently
            results = await asyncio.gather(
                create_tasks("A", 20),
                create_tasks("B", 20),
                create_tasks("C", 20)
            )
            
            total_created = sum(len(r) for r in results)
            if total_created == 60:
                result.passed = True
                result.message = f"Created {total_created} tasks concurrently"
            else:
                result.message = f"Expected 60, got {total_created}"
                
        except Exception as e:
            result.message = f"Failed: {str(e)}"
        result.duration = time.time() - start
        tests.append(result)
        
        # Test 2: Concurrent agent operations
        result = TestResult("Concurrent Agent Registration")
        start = time.time()
        try:
            from mcp_coordinator.server import EnhancedAgentCoordinator
            coordinator = EnhancedAgentCoordinator()
            
            async def register_agent(index: int):
                return coordinator.register_agent(
                    agent_id=f"test-agent-{index}",
                    role="tester",
                    capabilities=["testing"]
                )
            
            # Register agents concurrently
            agents = await asyncio.gather(*[
                register_agent(i) for i in range(10)
            ])
            
            if len(agents) == 10 and all(a['id'].startswith('test-agent-') for a in agents):
                result.passed = True
                result.message = "10 agents registered concurrently"
            else:
                result.message = "Agent registration failed"
                
        except Exception as e:
            result.message = f"Failed: {str(e)}"
        result.duration = time.time() - start
        tests.append(result)
        
        self.results.extend(tests)
    
    async def test_recovery(self):
        """Test recovery mechanisms"""
        tests = []
        
        # Test 1: Agent recovery
        result = TestResult("Agent Recovery")
        start = time.time()
        try:
            from mcp_coordinator.server import EnhancedAgentCoordinator
            coordinator = EnhancedAgentCoordinator()
            
            # Register agent
            agent = coordinator.register_agent(
                agent_id="recovery-test",
                role="tester",
                capabilities=["testing"]
            )
            
            # Simulate failure
            coordinator.agents["recovery-test"]['status'] = "failed"
            
            # Trigger recovery
            success = coordinator.recover_agent("recovery-test")
            
            if success and coordinator.agents["recovery-test"]['status'] == "recovering":
                result.passed = True
                result.message = "Agent recovery initiated"
            else:
                result.message = "Recovery failed"
                
        except Exception as e:
            result.message = f"Failed: {str(e)}"
        result.duration = time.time() - start
        tests.append(result)
        
        # Test 2: State recovery from backup
        result = TestResult("State Recovery from Backup")
        start = time.time()
        try:
            # Create test state files
            state_file = self.test_data_dir / "state.json"
            backup_file = self.test_data_dir / "state.backup.json"
            
            test_state = {
                'agents': {'test': {'id': 'test', 'role': 'tester'}},
                'task_queue': [],
                'audit_findings': []
            }
            
            # Save backup
            with open(backup_file, 'w') as f:
                json.dump(test_state, f)
            
            # Test loading from backup
            from mcp_coordinator.server import EnhancedAgentCoordinator
            
            # Temporarily change data dir
            original_cwd = os.getcwd()
            os.chdir(self.test_data_dir)
            
            coordinator = EnhancedAgentCoordinator()
            
            os.chdir(original_cwd)
            
            if 'test' in coordinator.agents:
                result.passed = True
                result.message = "Successfully loaded from backup"
            else:
                result.message = "Backup load failed"
                
            # Cleanup
            backup_file.unlink(missing_ok=True)
            state_file.unlink(missing_ok=True)
            
        except Exception as e:
            result.message = f"Failed: {str(e)}"
        result.duration = time.time() - start
        tests.append(result)
        
        self.results.extend(tests)
    
    async def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        tests = []
        
        # Test 1: Empty task queue handling
        result = TestResult("Empty Task Queue")
        start = time.time()
        try:
            from mcp_coordinator.server import EnhancedAgentCoordinator
            coordinator = EnhancedAgentCoordinator()
            
            # Clear task queue
            coordinator.task_queue = []
            
            # Try to get task
            task = coordinator.get_next_task("test-agent", "tester")
            
            if task is None:
                result.passed = True
                result.message = "Correctly returned None"
            else:
                result.message = "Should return None for empty queue"
                
        except Exception as e:
            result.message = f"Failed: {str(e)}"
        result.duration = time.time() - start
        tests.append(result)
        
        # Test 2: Large description handling
        result = TestResult("Large Description Handling")
        start = time.time()
        try:
            from mcp_coordinator.server import EnhancedAgentCoordinator
            coordinator = EnhancedAgentCoordinator()
            
            # Create task with very long description
            large_desc = "x" * 10000  # 10K characters
            task = coordinator.create_task(
                task_type="test",
                description=large_desc
            )
            
            if len(task['description']) == 10000:
                result.passed = True
                result.message = "Handled 10K character description"
            else:
                result.message = "Description truncated"
                
        except Exception as e:
            result.message = f"Failed: {str(e)}"
        result.duration = time.time() - start
        tests.append(result)
        
        # Test 3: Priority queue ordering
        result = TestResult("Priority Queue Ordering")
        start = time.time()
        try:
            from mcp_coordinator.server import EnhancedAgentCoordinator
            coordinator = EnhancedAgentCoordinator()
            
            # Clear queue
            coordinator.task_queue = []
            
            # Add tasks with different priorities
            low = coordinator.create_task("test", "Low priority", priority="low")
            critical = coordinator.create_task("test", "Critical", priority="critical")
            medium = coordinator.create_task("test", "Medium", priority="medium")
            high = coordinator.create_task("test", "High", priority="high")
            
            # Check order
            queue_order = [t['priority'] for t in coordinator.task_queue]
            expected = ['critical', 'high', 'medium', 'low']
            
            if queue_order == expected:
                result.passed = True
                result.message = "Correct priority ordering"
            else:
                result.message = f"Wrong order: {queue_order}"
                
        except Exception as e:
            result.message = f"Failed: {str(e)}"
        result.duration = time.time() - start
        tests.append(result)
        
        self.results.extend(tests)
    
    async def test_integration(self):
        """Test full system integration"""
        tests = []
        
        # Test 1: End-to-end workflow
        result = TestResult("End-to-End Workflow")
        start = time.time()
        try:
            from mcp_coordinator.server import EnhancedAgentCoordinator
            coordinator = EnhancedAgentCoordinator()
            
            # 1. Register auditor
            auditor = coordinator.register_agent(
                agent_id="test-auditor",
                role="auditor",
                capabilities=["audit", "scan"]
            )
            
            # 2. Submit finding
            finding = coordinator.submit_audit_finding({
                'title': 'Test Security Issue',
                'description': 'SQL injection vulnerability',
                'severity': 'high',
                'category': 'security',
                'file_path': 'app.py',
                'line_number': 100
            })
            
            # 3. Check task was created
            tasks = [t for t in coordinator.task_queue if t['type'] == 'plan']
            
            if len(tasks) > 0:
                # 4. Register planner
                planner = coordinator.register_agent(
                    agent_id="test-planner",
                    role="planner",
                    capabilities=["plan", "design"]
                )
                
                # 5. Planner gets task
                task = coordinator.get_next_task("test-planner", "planner")
                
                if task and task['type'] == 'plan':
                    # 6. Complete task
                    coordinator.update_task(task['id'], "completed", {
                        'plan': 'Fix SQL injection by using parameterized queries'
                    })
                    
                    result.passed = True
                    result.message = "Complete workflow executed"
                    result.details = {
                        'finding_id': finding['id'],
                        'task_id': task['id'],
                        'workflow': 'auditor -> finding -> task -> planner -> completed'
                    }
                else:
                    result.message = "Task assignment failed"
            else:
                result.message = "No task created from finding"
                
        except Exception as e:
            result.message = f"Failed: {str(e)}"
        result.duration = time.time() - start
        tests.append(result)
        
        self.results.extend(tests)
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*60)
        print("📊 TEST RESULTS SUMMARY")
        print("="*60)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.results:
                if not result.passed:
                    print(f"\n   {result.name}")
                    print(f"   Message: {result.message}")
                    if result.details:
                        print(f"   Details: {json.dumps(result.details, indent=6)}")
        
        print("\n📈 Performance Metrics:")
        for result in self.results:
            if result.passed and 'Performance' in result.name:
                print(f"   {result.name}: {result.message}")
        
        # Save detailed report
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total': total,
                'passed': passed,
                'failed': failed,
                'success_rate': passed/total*100
            },
            'results': [
                {
                    'name': r.name,
                    'passed': r.passed,
                    'message': r.message,
                    'duration': r.duration,
                    'details': r.details
                }
                for r in self.results
            ]
        }
        
        report_file = self.base_dir / f"test-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        # Return exit code
        return 0 if failed == 0 else 1

async def main():
    """Run test suite"""
    suite = AdvancedTestSuite()
    await suite.run_all_tests()
    return suite.generate_report()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)