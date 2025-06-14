#!/usr/bin/env python3
"""
MCP Coordinator Server for Autonomous Multi-Agent System
Handles agent registration, task management, and coordination
"""

import json
import logging
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import subprocess
import os

# MCP SDK imports
import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-coordinator")

class AgentCoordinator:
    def __init__(self):
        self.agents: Dict[str, Dict] = {}
        self.task_queue: List[Dict] = []
        self.audit_findings: List[Dict] = []
        self.worktrees: Dict[str, str] = {}
        self.base_dir = Path.cwd()
        self.data_dir = self.base_dir / "mcp-coordinator"
        self.data_dir.mkdir(exist_ok=True)
        
        # Load persistent data
        self.load_state()
    
    def load_state(self):
        """Load persistent state from files"""
        state_file = self.data_dir / "state.json"
        if state_file.exists():
            with open(state_file, 'r') as f:
                state = json.load(f)
                self.agents = state.get('agents', {})
                self.task_queue = state.get('task_queue', [])
                self.audit_findings = state.get('audit_findings', [])
    
    def save_state(self):
        """Save state to persistent storage"""
        state = {
            'agents': self.agents,
            'task_queue': self.task_queue,
            'audit_findings': self.audit_findings
        }
        state_file = self.data_dir / "state.json"
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def register_agent(self, agent_id: str, role: str, capabilities: List[str]) -> Dict:
        """Register a new agent"""
        self.agents[agent_id] = {
            'id': agent_id,
            'role': role,
            'capabilities': capabilities,
            'status': 'active',
            'registered_at': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat()
        }
        self.save_state()
        logger.info(f"Agent registered: {agent_id} ({role})")
        return self.agents[agent_id]
    
    def create_task(self, task_type: str, description: str, priority: str = 'medium', 
                   assigned_to: Optional[str] = None, context: Optional[Dict] = None) -> Dict:
        """Create a new task"""
        task = {
            'id': str(uuid.uuid4()),
            'type': task_type,
            'description': description,
            'priority': priority,
            'status': 'pending',
            'assigned_to': assigned_to,
            'context': context or {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        self.task_queue.append(task)
        self.save_state()
        logger.info(f"Task created: {task['id']} - {description}")
        return task
    
    def get_next_task(self, agent_id: str, agent_role: str) -> Optional[Dict]:
        """Get the next available task for an agent"""
        # Update agent last seen
        if agent_id in self.agents:
            self.agents[agent_id]['last_seen'] = datetime.now().isoformat()
        
        # Find suitable task
        for task in self.task_queue:
            if task['status'] == 'pending':
                # Check if task is suitable for agent role
                if self._is_task_suitable_for_role(task, agent_role):
                    task['status'] = 'in_progress'
                    task['assigned_to'] = agent_id
                    task['updated_at'] = datetime.now().isoformat()
                    self.save_state()
                    return task
        return None
    
    def _is_task_suitable_for_role(self, task: Dict, role: str) -> bool:
        """Check if a task is suitable for a specific agent role"""
        role_task_mapping = {
            'auditor': ['audit', 'scan', 'check', 'review_security'],
            'planner': ['plan', 'design', 'architect', 'breakdown'],
            'coder': ['implement', 'code', 'fix', 'refactor'],
            'tester': ['test', 'verify', 'validate'],
            'reviewer': ['review', 'approve', 'check_pr']
        }
        
        task_types = role_task_mapping.get(role, [])
        return any(t in task['type'].lower() for t in task_types)
    
    def update_task(self, task_id: str, status: str, result: Optional[Dict] = None) -> Dict:
        """Update task status"""
        for task in self.task_queue:
            if task['id'] == task_id:
                task['status'] = status
                task['updated_at'] = datetime.now().isoformat()
                if result:
                    task['result'] = result
                self.save_state()
                logger.info(f"Task updated: {task_id} - {status}")
                return task
        raise ValueError(f"Task not found: {task_id}")
    
    def submit_audit_finding(self, finding: Dict) -> Dict:
        """Submit an audit finding"""
        finding['id'] = str(uuid.uuid4())
        finding['submitted_at'] = datetime.now().isoformat()
        finding['status'] = 'new'
        self.audit_findings.append(finding)
        
        # Automatically create a task for the finding
        task = self.create_task(
            task_type='plan',
            description=f"Create implementation plan for: {finding['title']}",
            priority=finding.get('severity', 'medium'),
            context={'finding_id': finding['id'], 'finding': finding}
        )
        
        self.save_state()
        logger.info(f"Audit finding submitted: {finding['title']}")
        return finding
    
    def create_worktree(self, branch_name: str) -> str:
        """Create a git worktree for isolated agent work"""
        worktree_path = self.base_dir / "agent-workspaces" / branch_name
        
        if worktree_path.exists():
            return str(worktree_path)
        
        try:
            # Create worktree
            subprocess.run([
                'git', 'worktree', 'add', 
                str(worktree_path), 
                '-b', branch_name
            ], check=True, capture_output=True, text=True)
            
            self.worktrees[branch_name] = str(worktree_path)
            logger.info(f"Created worktree: {branch_name} at {worktree_path}")
            return str(worktree_path)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create worktree: {e}")
            raise
    
    def get_project_context(self) -> Dict:
        """Get project context information"""
        context = {
            'base_dir': str(self.base_dir),
            'active_agents': len([a for a in self.agents.values() if a['status'] == 'active']),
            'pending_tasks': len([t for t in self.task_queue if t['status'] == 'pending']),
            'in_progress_tasks': len([t for t in self.task_queue if t['status'] == 'in_progress']),
            'recent_findings': self.audit_findings[-10:] if self.audit_findings else []
        }
        
        # Read project goals if exists
        goals_file = self.base_dir / "PROJECT_GOALS.md"
        if goals_file.exists():
            context['project_goals'] = goals_file.read_text()
        
        return context

# Create coordinator instance
coordinator = AgentCoordinator()

# Create MCP server
server = Server("mcp-coordinator")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="register_agent",
            description="Register a new agent with the coordinator",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Unique agent identifier"},
                    "role": {"type": "string", "description": "Agent role (auditor, planner, coder, tester, reviewer)"},
                    "capabilities": {"type": "array", "items": {"type": "string"}, "description": "List of agent capabilities"}
                },
                "required": ["agent_id", "role", "capabilities"]
            }
        ),
        types.Tool(
            name="get_next_task",
            description="Get the next available task for an agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Agent identifier"},
                    "agent_role": {"type": "string", "description": "Agent role"}
                },
                "required": ["agent_id", "agent_role"]
            }
        ),
        types.Tool(
            name="update_task",
            description="Update task status",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task identifier"},
                    "status": {"type": "string", "description": "New status (in_progress, completed, failed)"},
                    "result": {"type": "object", "description": "Optional task result data"}
                },
                "required": ["task_id", "status"]
            }
        ),
        types.Tool(
            name="submit_audit_finding",
            description="Submit a new audit finding",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Finding title"},
                    "description": {"type": "string", "description": "Detailed description"},
                    "severity": {"type": "string", "description": "Severity level (low, medium, high, critical)"},
                    "category": {"type": "string", "description": "Finding category"},
                    "file_path": {"type": "string", "description": "Affected file path"},
                    "line_number": {"type": "integer", "description": "Line number if applicable"}
                },
                "required": ["title", "description", "severity", "category"]
            }
        ),
        types.Tool(
            name="create_worktree",
            description="Create a git worktree for isolated work",
            inputSchema={
                "type": "object",
                "properties": {
                    "branch_name": {"type": "string", "description": "Branch name for the worktree"}
                },
                "required": ["branch_name"]
            }
        ),
        types.Tool(
            name="get_project_context",
            description="Get current project context and status",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="create_task",
            description="Create a new task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_type": {"type": "string", "description": "Task type (audit, plan, implement, test, review)"},
                    "description": {"type": "string", "description": "Task description"},
                    "priority": {"type": "string", "description": "Priority level (low, medium, high)"},
                    "assigned_to": {"type": "string", "description": "Optional agent ID to assign to"},
                    "context": {"type": "object", "description": "Additional context data"}
                },
                "required": ["task_type", "description"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls"""
    try:
        if name == "register_agent":
            result = coordinator.register_agent(
                agent_id=arguments["agent_id"],
                role=arguments["role"],
                capabilities=arguments["capabilities"]
            )
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_next_task":
            task = coordinator.get_next_task(
                agent_id=arguments["agent_id"],
                agent_role=arguments["agent_role"]
            )
            if task:
                return [types.TextContent(type="text", text=json.dumps(task, indent=2))]
            else:
                return [types.TextContent(type="text", text="No tasks available")]
        
        elif name == "update_task":
            result = coordinator.update_task(
                task_id=arguments["task_id"],
                status=arguments["status"],
                result=arguments.get("result")
            )
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "submit_audit_finding":
            result = coordinator.submit_audit_finding(arguments)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "create_worktree":
            path = coordinator.create_worktree(arguments["branch_name"])
            return [types.TextContent(type="text", text=f"Worktree created at: {path}")]
        
        elif name == "get_project_context":
            context = coordinator.get_project_context()
            return [types.TextContent(type="text", text=json.dumps(context, indent=2))]
        
        elif name == "create_task":
            result = coordinator.create_task(
                task_type=arguments["task_type"],
                description=arguments["description"],
                priority=arguments.get("priority", "medium"),
                assigned_to=arguments.get("assigned_to"),
                context=arguments.get("context")
            )
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Run the MCP server"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        logger.info("MCP Coordinator Server starting...")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-coordinator",
                server_version="1.0.0"
            )
        )

if __name__ == "__main__":
    asyncio.run(main())