#!/usr/bin/env python3
"""Register CODER-2 agent with MCP coordinator"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Agent configuration
AGENT_ID = "CODER-2"
ROLE = "coder"
CAPABILITIES = [
    "code implementation",
    "bug fixes", 
    "refactoring",
    "git operations",
    "code optimization"
]

def register_agent():
    """Register CODER-2 agent with the coordinator"""
    try:
        # Create registration data
        registration_data = {
            "agent_id": AGENT_ID,
            "role": ROLE,
            "capabilities": CAPABILITIES,
            "status": "active",
            "registered_at": datetime.utcnow().isoformat()
        }
        
        # Ensure mcp-coordinator directory exists
        coord_dir = Path("mcp-coordinator")
        coord_dir.mkdir(exist_ok=True)
        
        # Save registration file
        reg_file = coord_dir / f"{AGENT_ID}-registration.json"
        with open(reg_file, 'w') as f:
            json.dump(registration_data, f, indent=2)
        
        print(f"Agent registration data:")
        print(json.dumps(registration_data, indent=2))
        print(f"\n✅ Agent {AGENT_ID} registered successfully")
        print(f"Registration saved to: {reg_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to register agent: {e}")
        return False

if __name__ == "__main__":
    success = register_agent()
    sys.exit(0 if success else 1)