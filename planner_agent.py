#!/usr/bin/env python3
"""Planner Agent - Creates implementation plans from audit findings"""

import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('planner_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("planner-agent")

class PlannerAgent:
    def __init__(self):
        self.agent_id = "planner-001"
        self.role = "planner"
        self.capabilities = [
            "create_implementation_plans",
            "break_down_tasks",
            "analyze_dependencies",
            "design_solutions",
            "prioritize_work"
        ]
        self.base_dir = Path.cwd()
        
    def register(self):
        """Register with the coordinator"""
        logger.info(f"Registering agent: {self.agent_id}")
        
        # In a real MCP environment, this would use mcp-coordinator.register_agent()
        # For now, we'll update the state file directly
        state_file = self.base_dir / "mcp-coordinator" / "state.json"
        
        try:
            # Load current state
            state = {}
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state = json.load(f)
            
            # Register agent
            if 'agents' not in state:
                state['agents'] = {}
                
            state['agents'][self.agent_id] = {
                "id": self.agent_id,
                "role": self.role,
                "capabilities": self.capabilities,
                "status": "active",
                "registered_at": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "version": "2.0"
            }
            
            # Initialize agent health
            if 'agent_health' not in state:
                state['agent_health'] = {}
                
            state['agent_health'][self.agent_id] = {
                "last_heartbeat": datetime.now().isoformat(),
                "tasks_completed": 0,
                "tasks_failed": 0,
                "average_task_time": 0.0,
                "error_count": 0,
                "recovery_count": 0
            }
            
            # Save updated state
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
                
            logger.info("Successfully registered with coordinator")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register: {e}")
            return False
    
    def get_next_task(self):
        """Get the next planning task from the queue"""
        state_file = self.base_dir / "mcp-coordinator" / "state.json"
        
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
            
            # Find next pending planning task
            for task in state.get('task_queue', []):
                if (task['type'] == 'plan' and 
                    task['status'] == 'pending' and
                    task.get('assigned_to') is None):
                    
                    # Assign task to this agent
                    task['assigned_to'] = self.agent_id
                    task['status'] = 'in_progress'
                    task['updated_at'] = datetime.now().isoformat()
                    
                    # Update agent status
                    if self.agent_id in state['agents']:
                        state['agents'][self.agent_id]['status'] = 'busy'
                        state['agents'][self.agent_id]['last_seen'] = datetime.now().isoformat()
                    
                    # Save state
                    with open(state_file, 'w') as f:
                        json.dump(state, f, indent=2)
                    
                    logger.info(f"Got task: {task['id']} - {task['description']}")
                    return task
                    
            logger.info("No pending planning tasks found")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get task: {e}")
            return None
    
    def create_implementation_plan(self, task):
        """Create a detailed implementation plan for a finding"""
        finding = task['context'].get('finding', {})
        
        plan = {
            "task_id": task['id'],
            "finding_id": finding.get('id'),
            "title": f"Implementation Plan: {finding.get('title', 'Unknown Issue')}",
            "severity": finding.get('severity', 'medium'),
            "created_at": datetime.now().isoformat(),
            "steps": [],
            "estimated_time": 0,
            "dependencies": [],
            "files_to_modify": [],
            "testing_requirements": [],
            "rollback_plan": ""
        }
        
        # Analyze the finding and create specific steps
        if finding.get('category') == 'security':
            if 'command injection' in finding.get('description', '').lower():
                plan['steps'] = [
                    "1. Import shlex module for proper command escaping",
                    "2. Identify all subprocess.run() calls with user input",
                    "3. Apply shlex.quote() to all user-controlled parameters",
                    "4. Add input validation for command arguments",
                    "5. Implement whitelist of allowed commands",
                    "6. Add security logging for command execution",
                    "7. Update error handling to prevent information leakage"
                ]
                plan['estimated_time'] = 45
                plan['files_to_modify'] = [finding.get('file_path', 'unknown')]
                plan['testing_requirements'] = [
                    "Unit tests for command escaping",
                    "Integration tests with malicious input",
                    "Security scan verification"
                ]
                plan['rollback_plan'] = "Revert changes to subprocess calls if issues arise"
                
            elif 'path traversal' in finding.get('description', '').lower():
                plan['steps'] = [
                    "1. Import os.path for path validation",
                    "2. Implement path sanitization function",
                    "3. Add validation to ensure paths stay within base directory",
                    "4. Use Path.resolve() to get absolute paths",
                    "5. Check resolved path starts with expected base path",
                    "6. Add logging for rejected path attempts",
                    "7. Update documentation with security notes"
                ]
                plan['estimated_time'] = 30
                plan['files_to_modify'] = [finding.get('file_path', 'unknown')]
                plan['testing_requirements'] = [
                    "Unit tests for path validation",
                    "Tests with various path traversal attempts",
                    "Boundary tests for edge cases"
                ]
                plan['rollback_plan'] = "Remove path validation if it breaks existing functionality"
                
        elif finding.get('category') == 'error_handling':
            plan['steps'] = [
                "1. Identify all unprotected operations",
                "2. Add try-except blocks with specific exception types",
                "3. Implement proper error logging with context",
                "4. Add error recovery mechanisms where appropriate",
                "5. Ensure errors are propagated correctly",
                "6. Add error metrics collection",
                "7. Update documentation with error scenarios"
            ]
            plan['estimated_time'] = 40
            plan['files_to_modify'] = [finding.get('file_path', 'unknown')]
            plan['testing_requirements'] = [
                "Unit tests for error scenarios",
                "Integration tests for error propagation",
                "Stress tests for error recovery"
            ]
            
        elif finding.get('category') == 'performance':
            plan['steps'] = [
                "1. Profile current implementation",
                "2. Identify performance bottlenecks",
                "3. Implement caching where appropriate",
                "4. Optimize database queries or file operations",
                "5. Add performance monitoring",
                "6. Implement rate limiting if needed",
                "7. Document performance improvements"
            ]
            plan['estimated_time'] = 60
            plan['files_to_modify'] = [finding.get('file_path', 'unknown')]
            plan['testing_requirements'] = [
                "Performance benchmarks",
                "Load tests",
                "Memory usage tests"
            ]
            
        else:
            # Generic plan for other categories
            plan['steps'] = [
                "1. Analyze the specific issue in detail",
                "2. Research best practices for this type of issue",
                "3. Design a solution that follows coding standards",
                "4. Implement the fix with minimal disruption",
                "5. Add appropriate tests",
                "6. Update documentation",
                "7. Verify the fix resolves the issue"
            ]
            plan['estimated_time'] = 30
            plan['files_to_modify'] = [finding.get('file_path', 'unknown')]
            
        return plan
    
    def submit_plan(self, plan, task):
        """Submit the implementation plan"""
        state_file = self.base_dir / "mcp-coordinator" / "state.json"
        
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
            
            # Create implementation task
            impl_task = {
                "id": str(datetime.now().timestamp()),
                "type": "implementation",
                "description": f"Implement fix for: {plan['title']}",
                "priority": plan['severity'],
                "priority_score": {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}.get(plan['severity'], 2),
                "status": "pending",
                "assigned_to": None,
                "context": {
                    "plan": plan,
                    "finding_id": plan['finding_id'],
                    "planner_task_id": task['id']
                },
                "dependencies": plan.get('dependencies', []),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "retry_count": 0,
                "estimated_duration": plan['estimated_time'] * 60  # Convert to seconds
            }
            
            # Add to task queue
            if 'task_queue' not in state:
                state['task_queue'] = []
            state['task_queue'].append(impl_task)
            
            # Update original task
            for i, t in enumerate(state['task_queue']):
                if t['id'] == task['id']:
                    state['task_queue'][i]['status'] = 'completed'
                    state['task_queue'][i]['result'] = {
                        'plan_created': True,
                        'implementation_task_id': impl_task['id']
                    }
                    state['task_queue'][i]['completed_at'] = datetime.now().isoformat()
                    break
            
            # Update agent stats
            if self.agent_id in state['agent_health']:
                state['agent_health'][self.agent_id]['tasks_completed'] += 1
            
            # Save state
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            logger.info(f"Created implementation task: {impl_task['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to submit plan: {e}")
            return False
    
    def run(self):
        """Main agent loop"""
        logger.info("Starting Planner Agent")
        
        # Register with coordinator
        if not self.register():
            logger.error("Failed to register with coordinator")
            return
        
        # Main work loop
        while True:
            try:
                # Get next task
                task = self.get_next_task()
                
                if task:
                    logger.info(f"Processing task: {task['description']}")
                    
                    # Create implementation plan
                    plan = self.create_implementation_plan(task)
                    logger.info(f"Created plan with {len(plan['steps'])} steps")
                    
                    # Submit plan
                    if self.submit_plan(plan, task):
                        logger.info("Successfully submitted plan")
                    else:
                        logger.error("Failed to submit plan")
                else:
                    logger.info("No tasks available, waiting...")
                    time.sleep(10)
                    
            except KeyboardInterrupt:
                logger.info("Shutting down gracefully...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(5)

if __name__ == "__main__":
    agent = PlannerAgent()
    agent.run()