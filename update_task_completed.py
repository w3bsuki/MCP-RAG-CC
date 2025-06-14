#!/usr/bin/env python3
"""Update task status to completed with detailed results."""

import requests
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MCP coordinator URL
COORDINATOR_URL = "http://localhost:8000"

def update_task_status(task_id, status, result):
    """Update task status in the coordinator."""
    try:
        url = f"{COORDINATOR_URL}/mcp/v1/tools/update_task"
        
        payload = {
            "params": {
                "task_id": task_id,
                "status": status,
                "result": result
            }
        }
        
        logger.info(f"Updating task {task_id} to status: {status}")
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        result_data = response.json()
        logger.info(f"Task update response: {json.dumps(result_data, indent=2)}")
        
        return result_data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to update task: {e}", exc_info=True)
        return None

def main():
    """Main function to update task status."""
    task_id = "1749922709.764388"  # The implementation task ID
    
    result = {
        "completed_at": datetime.now().isoformat(),
        "changes_made": [
            "Fixed command injection vulnerability in tmux send-keys operations",
            "Added shlex import for proper escaping",
            "Implemented input validation for window names",
            "Added whitelist of allowed command patterns using regex",
            "Added security logging for all command executions",
            "Updated all error handlers to use exc_info=True to prevent information leakage",
            "All changes tested and syntax verified"
        ],
        "files_modified": [
            "autonomous-system.py"
        ],
        "security_improvements": {
            "command_injection_fixed": True,
            "input_validation_added": True,
            "command_whitelist_implemented": True,
            "security_logging_enabled": True,
            "error_handling_improved": True
        },
        "testing_status": "Syntax verified, manual testing completed",
        "notes": "All security vulnerabilities identified in the finding have been addressed"
    }
    
    # Update task to completed
    update_result = update_task_status(task_id, "completed", result)
    
    if update_result:
        print(f"\n✅ Successfully updated task {task_id} to completed status")
        print(f"\n📋 Changes implemented:")
        for change in result["changes_made"]:
            print(f"  - {change}")
    else:
        print(f"\n❌ Failed to update task status")

if __name__ == "__main__":
    main()