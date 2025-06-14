#!/usr/bin/env python3
"""
Test the MCP Coordinator Server
"""

import asyncio
import json
import sys
from pathlib import Path

# Test if we can import MCP
try:
    import mcp.types as types
    from mcp.client import Client
    from mcp.client.stdio import stdio_client
    print("✅ MCP imports successful")
except ImportError as e:
    print(f"❌ Failed to import MCP: {e}")
    print("Install with: pip install mcp")
    sys.exit(1)

async def test_mcp_server():
    """Test basic MCP server functionality"""
    print("\n🧪 Testing MCP Coordinator Server")
    print("=" * 40)
    
    try:
        # Create a test client
        print("📡 Connecting to MCP server...")
        
        server_path = Path(__file__).parent / "mcp-coordinator" / "server.py"
        
        async with stdio_client(
            server_path=str(server_path),
            server_args=[]
        ) as (read_stream, write_stream):
            async with Client(
                name="test-client",
                version="1.0.0"
            ) as client:
                # Initialize connection
                await client.initialize(read_stream, write_stream)
                print("✅ Connected to MCP server")
                
                # List available tools
                print("\n📋 Available tools:")
                tools_response = await client.list_tools()
                for tool in tools_response.tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                # Test agent registration
                print("\n🤖 Testing agent registration...")
                result = await client.call_tool(
                    "register_agent",
                    {
                        "agent_id": "test-agent-001",
                        "role": "auditor",
                        "capabilities": ["test_capability"]
                    }
                )
                print(f"✅ Agent registered: {result.content[0].text}")
                
                # Test project context
                print("\n🌍 Testing project context retrieval...")
                result = await client.call_tool("get_project_context", {})
                context = json.loads(result.content[0].text)
                print(f"✅ Project context retrieved:")
                print(f"  - Base dir: {context['base_dir']}")
                print(f"  - Active agents: {context['active_agents']}")
                
                # Test task creation
                print("\n📝 Testing task creation...")
                result = await client.call_tool(
                    "create_task",
                    {
                        "task_type": "test",
                        "description": "Test task from test script",
                        "priority": "low"
                    }
                )
                task = json.loads(result.content[0].text)
                print(f"✅ Task created: {task['id']}")
                
                # Test getting next task
                print("\n📥 Testing task retrieval...")
                result = await client.call_tool(
                    "get_next_task",
                    {
                        "agent_id": "test-agent-001",
                        "agent_role": "tester"
                    }
                )
                if result.content[0].text != "No tasks available":
                    print(f"✅ Retrieved task: {result.content[0].text}")
                else:
                    print("ℹ️  No tasks available for tester role")
                
                print("\n✅ All tests passed!")
                
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_file_structure():
    """Test that all required files exist"""
    print("\n📁 Testing file structure")
    print("=" * 40)
    
    required_files = [
        "mcp-coordinator/server.py",
        ".claude/config.json",
        "claude_mcp_settings.json",
        ".claude/agents/auditor.md",
        ".claude/agents/planner.md",
        ".claude/agents/coder.md",
        ".claude/agents/tester.md",
        ".claude/agents/reviewer.md",
        "autonomous-system.py",
        "start.sh",
        "stop.sh",
        "status.sh"
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            all_exist = False
    
    return all_exist

def test_dependencies():
    """Test that all dependencies are available"""
    print("\n🔧 Testing dependencies")
    print("=" * 40)
    
    # Test Python version
    import sys
    py_version = sys.version_info
    if py_version.major >= 3 and py_version.minor >= 8:
        print(f"✅ Python {py_version.major}.{py_version.minor}.{py_version.micro}")
    else:
        print(f"❌ Python {py_version.major}.{py_version.minor} (need 3.8+)")
        return False
    
    # Test imports
    try:
        import mcp
        print("✅ MCP module available")
    except ImportError:
        print("❌ MCP module not found")
        return False
    
    # Test commands
    import subprocess
    
    commands = {
        "tmux": "tmux -V",
        "claude": "claude --version",
        "git": "git --version"
    }
    
    all_available = True
    for cmd, test_cmd in commands.items():
        try:
            result = subprocess.run(test_cmd.split(), capture_output=True, check=True)
            print(f"✅ {cmd} available")
        except:
            print(f"❌ {cmd} not found")
            all_available = False
    
    return all_available

async def main():
    """Run all tests"""
    print("🚀 Autonomous Multi-Agent System Test Suite")
    print("=" * 50)
    
    # Test dependencies
    if not test_dependencies():
        print("\n❌ Dependency test failed")
        return
    
    # Test file structure
    if not test_file_structure():
        print("\n❌ File structure test failed")
        return
    
    # Test MCP server
    if not await test_mcp_server():
        print("\n❌ MCP server test failed")
        return
    
    print("\n" + "=" * 50)
    print("✅ All tests passed! System is ready to use.")
    print("\n🚀 To start the system, run:")
    print("   ./start.sh")

if __name__ == "__main__":
    asyncio.run(main())