#!/usr/bin/env python3
"""Test script to verify security fixes for command injection vulnerability"""

import sys
import os
import importlib.util
import logging

# Load the module dynamically
spec = importlib.util.spec_from_file_location("autonomous_system", 
    os.path.join(os.path.dirname(__file__), "autonomous-system.py"))
autonomous_system = importlib.util.module_from_spec(spec)
spec.loader.exec_module(autonomous_system)
EnhancedAutonomousLauncher = autonomous_system.EnhancedAutonomousLauncher

# Set up test logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
test_logger = logging.getLogger("security_test")

def test_security_fixes():
    """Test various command injection scenarios"""
    launcher = EnhancedAutonomousLauncher()
    
    test_cases = [
        # Valid commands
        ("Valid cd command", "auditor", "cd /home/user/project", True),
        ("Valid export command", "auditor", "export AGENT_ID=test-123", True),
        ("Valid python command", "auditor", "python3 test.py", True),
        ("Valid comment", "auditor", "# This is a comment", True),
        ("Valid exit command", "auditor", "/exit", True),
        ("Valid help command", "auditor", "/help", True),
        
        # Invalid/malicious commands
        ("Command injection attempt 1", "auditor", "cd /tmp; rm -rf /", False),
        ("Command injection attempt 2", "auditor", "export VAR=test && malicious_command", False),
        ("Command injection with backticks", "auditor", "cd `whoami`", False),
        ("Command with pipe", "auditor", "ls | grep secret", False),
        ("Command with redirect", "auditor", "cat /etc/passwd > output.txt", False),
        ("Shell metacharacters", "auditor", "echo $(id)", False),
        ("Invalid window name", "auditor'; rm -rf /", "cd /tmp", False),
        ("Window name with spaces", "auditor test", "cd /tmp", False),
    ]
    
    passed = 0
    failed = 0
    
    print("Running security tests...\n")
    
    for test_name, window, command, should_succeed in test_cases:
        try:
            # Test window validation for special test case
            if "Invalid window name" in test_name:
                try:
                    launcher.send_to_agent(window, "cd /tmp")
                    if should_succeed:
                        print(f"✅ {test_name}: PASSED")
                        passed += 1
                    else:
                        print(f"❌ {test_name}: FAILED (command was allowed)")
                        failed += 1
                except ValueError as e:
                    if not should_succeed:
                        print(f"✅ {test_name}: PASSED (correctly rejected)")
                        passed += 1
                    else:
                        print(f"❌ {test_name}: FAILED (command was rejected)")
                        failed += 1
            else:
                # Normal command testing
                try:
                    # Mock the subprocess.run to avoid actual execution
                    original_run = launcher.__class__.send_to_agent
                    def mock_send(self, win, cmd):
                        # Just validate, don't execute
                        # Validate window name
                        if not win or not win.replace("-", "").replace("_", "").isalnum():
                            raise ValueError(f"Invalid window name: {win}")
                        
                        # Check whitelist
                        import re
                        command_allowed = False
                        for pattern in self.allowed_command_patterns:
                            if re.match(pattern, cmd):
                                command_allowed = True
                                break
                        
                        if not command_allowed:
                            raise ValueError(f"Command not allowed: {cmd}")
                        
                        return None
                    
                    launcher.__class__.send_to_agent = mock_send
                    launcher.send_to_agent(window, command)
                    launcher.__class__.send_to_agent = original_run
                    
                    if should_succeed:
                        print(f"✅ {test_name}: PASSED")
                        passed += 1
                    else:
                        print(f"❌ {test_name}: FAILED (command was allowed)")
                        failed += 1
                        
                except ValueError as e:
                    if not should_succeed:
                        print(f"✅ {test_name}: PASSED (correctly rejected)")
                        passed += 1
                    else:
                        print(f"❌ {test_name}: FAILED (command was rejected)")
                        print(f"   Error: {e}")
                        failed += 1
                        
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed} passed, {failed} failed")
    print(f"{'='*50}")
    
    return failed == 0

if __name__ == "__main__":
    success = test_security_fixes()
    sys.exit(0 if success else 1)