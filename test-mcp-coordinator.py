#!/usr/bin/env python3
"""Test script to verify MCP coordinator functionality"""

import asyncio
import json
from pathlib import Path

# Simulate agent behavior
async def test_coordinator():
    print("🧪 Testing MCP Coordinator functionality...")
    
    # Test 1: Check if coordinator files exist
    coordinator_path = Path("mcp-coordinator/server.py")
    if coordinator_path.exists():
        print("✅ Coordinator server file exists")
    else:
        print("❌ Coordinator server file not found")
        return
    
    # Test 2: Check MCP settings
    settings_path = Path("claude_mcp_settings.json")
    if settings_path.exists():
        with open(settings_path) as f:
            settings = json.load(f)
        print("✅ MCP settings configured")
        print(f"   - Python path: {settings['mcpServers']['mcp-coordinator']['command']}")
        print(f"   - Server path: {settings['mcpServers']['mcp-coordinator']['args'][0]}")
    else:
        print("❌ MCP settings file not found")
        return
    
    # Test 3: Simulate task creation
    print("\n📝 Simulating task creation...")
    sample_task = {
        "task_type": "audit",
        "description": "Audit codebase for security issues",
        "priority": "high",
        "status": "pending"
    }
    print(f"   Task: {sample_task['description']}")
    print(f"   Type: {sample_task['task_type']}")
    print(f"   Priority: {sample_task['priority']}")
    
    # Test 4: Check agent instructions
    print("\n📚 Checking agent instructions...")
    for role in ["auditor", "planner", "coder", "tester", "reviewer"]:
        instruction_file = Path(f".claude/agents/{role}.md")
        if instruction_file.exists():
            print(f"✅ {role.capitalize()} instructions found")
        else:
            print(f"⚠️  {role.capitalize()} instructions missing")
    
    # Test 5: Check COORDINATION.md
    coord_file = Path("../COORDINATION.md")
    if coord_file.exists():
        print("\n📋 COORDINATION.md found - agents can read tasks from here")
        with open(coord_file) as f:
            lines = f.readlines()[:10]
        print("   First few lines:")
        for line in lines[:5]:
            print(f"   {line.strip()}")
    
    print("\n✅ MCP Coordinator test complete!")
    print("\nℹ️  Note: Actual agents require OAuth authentication to run")
    print("   - Each agent needs manual authentication via browser")
    print("   - Or use API keys if supported by your Claude Code version")

if __name__ == "__main__":
    asyncio.run(test_coordinator())