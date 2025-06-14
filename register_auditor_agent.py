#!/usr/bin/env python3
"""
Register Auditor Agent with MCP Coordinator
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Registration data for auditor agent
registration_data = {
    "agent_id": "auditor-agent",
    "role": "auditor",
    "capabilities": [
        "code-analysis",
        "security-scanning",
        "performance-analysis",
        "quality-assessment",
        "documentation-review"
    ],
    "status": "active",
    "registered_at": datetime.utcnow().isoformat()
}

print("🔍 Registering AUDITOR Agent with MCP Coordinator")
print(f"Agent ID: {registration_data['agent_id']}")
print(f"Role: {registration_data['role']}")
print(f"Capabilities: {', '.join(registration_data['capabilities'])}")
print(f"Timestamp: {registration_data['registered_at']}")

# Save registration locally (as backup)
base_dir = Path(__file__).parent
reg_file = base_dir / "mcp-coordinator" / f"{registration_data['agent_id']}-registration.json"
reg_file.parent.mkdir(exist_ok=True)

with open(reg_file, 'w') as f:
    json.dump(registration_data, f, indent=2)

print(f"\n✅ Registration data saved to: {reg_file}")
print("\nTo complete registration, use the MCP tool:")
print(f"mcp-coordinator.register_agent(")
print(f'    agent_id="{registration_data["agent_id"]}",')
print(f'    role="{registration_data["role"]}",')
print(f'    capabilities={registration_data["capabilities"]}')
print(")")