#!/usr/bin/env python3
"""
Submit implementation plan for fixing command injection vulnerability
"""

import json
from datetime import datetime
from pathlib import Path

# Comprehensive implementation plan
implementation_plan = {
    "plan_id": "plan-fix-command-injection-001",
    "task_id": "task-plan-1749924324",
    "finding_id": "e95837ad-ae10-4790-8756-a44334aa0c4f",
    "title": "Fix Command Injection Vulnerability in check_dependencies()",
    "description": "Comprehensive security fix for command injection vulnerability in autonomous-system.py",
    "risk_assessment": {
        "severity": "critical",
        "impact": "High - Arbitrary command execution with full privileges",
        "likelihood": "Medium - Requires config file or environment access",
        "priority": "P0 - Must fix immediately"
    },
    "implementation_steps": [
        {
            "step": 1,
            "title": "Create Command Whitelist",
            "description": "Define allowed commands and validate against whitelist",
            "details": [
                "Create ALLOWED_COMMANDS constant with only 'tmux', 'claude', 'git'",
                "Implement validate_command() function to check against whitelist",
                "Use absolute paths for commands (/usr/bin/git, etc.)",
                "Reject any command not in whitelist"
            ],
            "estimated_time": "15 minutes"
        },
        {
            "step": 2,
            "title": "Implement Input Validation",
            "description": "Add comprehensive input validation for all command parameters",
            "details": [
                "Validate command names contain only alphanumeric characters",
                "Ensure version flags are exactly '--version' or '-V'",
                "Strip and validate all input parameters",
                "Use shlex.quote() for any dynamic parameters"
            ],
            "estimated_time": "20 minutes"
        },
        {
            "step": 3,
            "title": "Refactor check_dependencies()",
            "description": "Rewrite function with security-first approach",
            "details": [
                "Use hardcoded command paths instead of dynamic lookup",
                "Implement try-except blocks with specific error handling",
                "Add security logging for all command executions",
                "Use subprocess with shell=False and explicit arguments"
            ],
            "code_snippet": """
def check_dependencies(self) -> bool:
    '''Enhanced dependency checking with security validation'''
    logger.info('Checking system dependencies...')
    
    # Whitelist of allowed commands with absolute paths
    ALLOWED_COMMANDS = {
        'tmux': '/usr/bin/tmux',
        'claude': '/usr/local/bin/claude',
        'git': '/usr/bin/git'
    }
    
    dependencies = {
        'tmux': ['--version'],
        'claude': ['--version'],
        'git': ['--version']
    }
    
    missing = []
    for cmd, args in dependencies.items():
        if cmd not in ALLOWED_COMMANDS:
            logger.error(f'Command {cmd} not in whitelist')
            missing.append(cmd)
            continue
            
        try:
            # Use absolute path from whitelist
            cmd_path = ALLOWED_COMMANDS[cmd]
            
            # Validate arguments
            if not all(arg in ['--version', '-V'] for arg in args):
                logger.error(f'Invalid arguments for {cmd}: {args}')
                missing.append(cmd)
                continue
            
            # Execute with security constraints
            result = subprocess.run(
                [cmd_path] + args,
                capture_output=True,
                text=True,
                timeout=5,
                shell=False  # Explicitly disable shell
            )
            
            if result.returncode != 0:
                missing.append(cmd)
                logger.warning(f'{cmd} check failed: {result.stderr}')
            else:
                logger.debug(f'{cmd} version: {result.stdout.strip()}')
                
        except subprocess.TimeoutExpired:
            logger.error(f'{cmd} version check timed out')
            missing.append(cmd)
        except FileNotFoundError:
            logger.error(f'{cmd} not found at {cmd_path}')
            missing.append(cmd)
        except Exception as e:
            logger.error(f'Unexpected error checking {cmd}', exc_info=True)
            missing.append(cmd)
    
    if missing:
        logger.error(f'Missing dependencies: {missing}')
        return False
        
    logger.info('✅ All dependencies satisfied')
    return True
""",
            "estimated_time": "25 minutes"
        },
        {
            "step": 4,
            "title": "Add Security Logging",
            "description": "Implement comprehensive security event logging",
            "details": [
                "Log all command execution attempts with timestamps",
                "Create security audit trail for command validation failures",
                "Add alerts for suspicious command patterns",
                "Implement rate limiting for dependency checks"
            ],
            "estimated_time": "15 minutes"
        },
        {
            "step": 5,
            "title": "Write Security Tests",
            "description": "Create comprehensive test suite for security validation",
            "test_cases": [
                "Test command whitelist validation",
                "Test rejection of non-whitelisted commands",
                "Test handling of malformed arguments",
                "Test command injection attempts",
                "Test path traversal attempts",
                "Test timeout handling",
                "Test error scenarios"
            ],
            "estimated_time": "30 minutes"
        },
        {
            "step": 6,
            "title": "Integration Testing",
            "description": "Verify fix doesn't break existing functionality",
            "details": [
                "Test normal dependency checking flow",
                "Verify all agents can still launch",
                "Test with missing dependencies",
                "Verify error messages are informative",
                "Check performance impact"
            ],
            "estimated_time": "20 minutes"
        },
        {
            "step": 7,
            "title": "Security Review",
            "description": "Final security validation and documentation",
            "details": [
                "Review code for any remaining vulnerabilities",
                "Update security documentation",
                "Add inline security comments",
                "Create security test checklist"
            ],
            "estimated_time": "15 minutes"
        }
    ],
    "testing_requirements": {
        "unit_tests": [
            "test_validate_command_whitelist",
            "test_reject_non_whitelisted_commands",
            "test_validate_command_arguments",
            "test_command_injection_attempts",
            "test_timeout_handling",
            "test_missing_dependencies",
            "test_security_logging"
        ],
        "integration_tests": [
            "test_full_dependency_check_flow",
            "test_agent_launch_with_validated_deps",
            "test_system_startup_security"
        ],
        "security_tests": [
            "test_command_injection_prevention",
            "test_path_traversal_prevention",
            "test_argument_injection_prevention"
        ],
        "coverage_target": "95%"
    },
    "code_review_checklist": [
        "All commands validated against whitelist",
        "No dynamic command construction",
        "Absolute paths used for all commands",
        "Shell=False enforced in all subprocess calls",
        "Comprehensive error handling",
        "Security logging implemented",
        "No user input in command construction",
        "Timeout protection on all external calls"
    ],
    "rollback_plan": {
        "trigger_conditions": [
            "Dependency checks failing in production",
            "Agent launch failures",
            "Performance degradation > 10%"
        ],
        "steps": [
            "Revert to previous version via git",
            "Clear any cached dependency states",
            "Restart autonomous system",
            "Monitor for successful agent launches"
        ],
        "estimated_time": "5 minutes"
    },
    "performance_impact": {
        "expected_impact": "Minimal - adds ~50ms to startup",
        "mitigation": "Cache validated command paths after first check"
    },
    "delivery_timeline": {
        "total_estimated_time": "140 minutes",
        "phases": [
            {"phase": "Implementation", "time": "75 minutes"},
            {"phase": "Testing", "time": "50 minutes"},
            {"phase": "Review & Documentation", "time": "15 minutes"}
        ]
    },
    "success_criteria": [
        "Command injection vulnerability eliminated",
        "All existing functionality preserved",
        "95% test coverage achieved",
        "Security logging operational",
        "No performance regression",
        "Code review approved"
    ]
}

def update_task_with_plan():
    """Update the task with the implementation plan"""
    try:
        # Load current state
        state_file = Path("mcp-coordinator/state.json")
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        # Update the task in the tasks section
        if "tasks" in state and "task-plan-1749924324" in state["tasks"]:
            task = state["tasks"]["task-plan-1749924324"]
            task["status"] = "completed"
            task["updated_at"] = datetime.now().isoformat()
            task["completed_at"] = datetime.now().isoformat()
            task["result"] = {
                "plan": implementation_plan,
                "status": "success",
                "message": "Comprehensive implementation plan created successfully"
            }
            
            # Also update in task_queue if present
            for queue_task in state.get("task_queue", []):
                if queue_task.get("id") == "task-plan-1749924324":
                    queue_task["status"] = "completed"
                    queue_task["updated_at"] = datetime.now().isoformat()
                    queue_task["result"] = task["result"]
                    break
            
            # Save updated state
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            print("✅ Task updated successfully with implementation plan")
            
            # Save plan separately for reference
            plan_file = Path("mcp-coordinator/implementation_plan_command_injection.json")
            with open(plan_file, 'w') as f:
                json.dump(implementation_plan, f, indent=2)
            
            print(f"💾 Plan saved to {plan_file}")
            
            # Create implementation task for coder
            create_implementation_task(state, state_file)
            
            return True
            
        else:
            print("❌ Task not found in state")
            return False
            
    except Exception as e:
        print(f"❌ Error updating task: {e}")
        return False

def create_implementation_task(state, state_file):
    """Create an implementation task based on the plan"""
    impl_task = {
        "id": f"impl-fix-cmd-injection-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "type": "implementation",
        "description": "Implement security fix for command injection vulnerability in check_dependencies()",
        "priority": "critical",
        "priority_score": 4,
        "status": "pending",
        "assigned_to": None,
        "context": {
            "finding_id": "e95837ad-ae10-4790-8756-a44334aa0c4f",
            "plan_id": "plan-fix-command-injection-001",
            "implementation_plan": implementation_plan,
            "files_to_modify": ["autonomous-system.py"],
            "estimated_time": "140 minutes"
        },
        "dependencies": [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "retry_count": 0,
        "estimated_duration": 8400  # 140 minutes in seconds
    }
    
    # Add to task queue
    if "task_queue" not in state:
        state["task_queue"] = []
    state["task_queue"].append(impl_task)
    
    # Save state
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
    
    print(f"✅ Created implementation task: {impl_task['id']}")

if __name__ == "__main__":
    update_task_with_plan()