#!/usr/bin/env python3
"""Register coder-001 agent with MCP coordinator using MCP protocol."""

import sys
import json
import asyncio
from pathlib import Path

# Add the MCP-RAG-CC directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def register_and_get_task():
    """Register coder-001 and get a task."""
    
    # Create server parameters for the coordinator
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(Path(__file__).parent / "mcp-coordinator" / "server.py")],
        env={
            "PYTHONPATH": str(Path(__file__).parent),
            "PYTHONUNBUFFERED": "1"
        }
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            # Register the agent
            print("Registering coder-001...")
            try:
                register_result = await session.call_tool(
                    "register_agent",
                    arguments={
                        "agent_id": "coder-001",
                        "role": "coder",
                        "capabilities": ["code_implementation", "bug_fixing", "refactoring", "feature_development", "code_generation"]
                    }
                )
                print(f"Registration result: {register_result}")
            except Exception as e:
                print(f"Registration error: {e}")
                return
            
            # Get next task
            print("\nGetting next task for coder-001...")
            try:
                task_result = await session.call_tool(
                    "get_next_task",
                    arguments={
                        "agent_id": "coder-001",
                        "agent_role": "coder"
                    }
                )
                if task_result and task_result.content:
                    print(f"Task received: {task_result.content[0].text}")
                else:
                    print("No task available")
            except Exception as e:
                print(f"Get task error: {e}")

if __name__ == "__main__":
    asyncio.run(register_and_get_task())