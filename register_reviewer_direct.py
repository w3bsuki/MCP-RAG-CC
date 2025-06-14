#!/usr/bin/env python3
"""
Direct registration of REVIEWER-001 agent with MCP Coordinator
"""

import json
import asyncio
import mcp
from mcp.client import StdioClientSession
from mcp.transport.stdio import StdioTransport
from datetime import datetime
import sys
import subprocess

async def register_reviewer():
    """Register REVIEWER-001 agent with the MCP coordinator"""
    
    # Start the MCP coordinator server
    server_path = "/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/mcp-coordinator/server.py"
    python_path = "/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/venv/bin/python3"
    
    # Create the transport
    transport = StdioTransport(
        stdin=None,
        stdout=None,
        stderr=None,
        command=python_path,
        args=[server_path],
        env={
            "PYTHONPATH": "/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC",
            "PYTHONUNBUFFERED": "1"
        }
    )
    
    # Create the client session
    async with StdioClientSession(transport) as client:
        await client.initialize()
        
        # Register the REVIEWER-001 agent
        result = await client.call_tool(
            "register_agent",
            arguments={
                "agent_id": "reviewer-001",
                "role": "reviewer",
                "capabilities": [
                    "code_review",
                    "pr_creation",
                    "quality_checking",
                    "documentation_review",
                    "best_practices"
                ]
            }
        )
        
        print("✅ REVIEWER-001 agent registered successfully!")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        # Get the next task
        next_task = await client.call_tool(
            "get_next_task",
            arguments={
                "agent_id": "reviewer-001",
                "agent_role": "reviewer"
            }
        )
        
        print("\n📋 Next task for REVIEWER-001:")
        print(json.dumps(next_task, indent=2))
        
        return result, next_task

if __name__ == "__main__":
    result, task = asyncio.run(register_reviewer())