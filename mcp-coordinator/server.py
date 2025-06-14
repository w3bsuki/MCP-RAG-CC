#!/usr/bin/env python3
"""
Enhanced MCP Coordinator Server v2 for Autonomous Multi-Agent System
Features: Advanced error handling, retry logic, health monitoring, RAG support
"""

import json
import logging
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
import subprocess
import os
import sys
import traceback
import time
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from enum import Enum
import time
import hashlib
import shlex

# MCP SDK imports
import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# Configure advanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('coordinator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("mcp-coordinator-v2")

class TaskPriority(Enum):
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1

class AgentStatus(Enum):
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    FAILED = "failed"
    RECOVERING = "recovering"

@dataclass
class AgentHealth:
    last_heartbeat: datetime
    tasks_completed: int
    tasks_failed: int
    average_task_time: float
    error_count: int
    recovery_count: int

class EnhancedAgentCoordinator:
    def __init__(self):
        self.agents: Dict[str, Dict] = {}
        self.agent_health: Dict[str, AgentHealth] = {}
        self.task_queue: List[Dict] = []
        self.audit_findings: List[Dict] = []
        self.worktrees: Dict[str, str] = {}
        self.base_dir = Path.cwd()
        self.data_dir = self.base_dir / "mcp-coordinator"
        self.data_dir.mkdir(exist_ok=True)
        
        # Security: Whitelist of allowed commands
        self.allowed_commands = {
            'git': ['init', 'add', 'commit', 'worktree', 'rev-parse'],
            # Add other commands as needed
        }
        
        # Enhanced features
        self.task_history: deque = deque(maxlen=1000)
        self.agent_capabilities_cache: Dict[str, Set[str]] = {}
        self.task_retry_count: Dict[str, int] = defaultdict(int)
        self.max_retries = 3
        self.agent_load_balance: Dict[str, int] = defaultdict(int)
        
        # RAG features
        self.knowledge_base: Dict[str, Any] = {}
        self.context_memory: Dict[str, List[Dict]] = defaultdict(list)
        self.finding_patterns: Dict[str, int] = defaultdict(int)
        
        # Load persistent data
        self.load_state()
        
        # Background tasks will be started when the server runs
        self._tasks = []
    
    def load_state(self):
        """Load persistent state with error recovery"""
        state_file = self.data_dir / "state.json"
        backup_file = self.data_dir / "state.backup.json"
        
        try:
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    self._restore_state(state)
                    logger.info("State loaded successfully")
            elif backup_file.exists():
                logger.warning("Loading from backup state")
                with open(backup_file, 'r') as f:
                    state = json.load(f)
                    self._restore_state(state)
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            logger.info("Starting with fresh state")
    
    def _restore_state(self, state: Dict):
        """Restore state from loaded data"""
        self.agents = state.get('agents', {})
        self.task_queue = state.get('task_queue', [])
        self.audit_findings = state.get('audit_findings', [])
        self.knowledge_base = state.get('knowledge_base', {})
        
        # Restore health data
        for agent_id, health_data in state.get('agent_health', {}).items():
            self.agent_health[agent_id] = AgentHealth(
                last_heartbeat=datetime.fromisoformat(health_data['last_heartbeat']),
                tasks_completed=health_data['tasks_completed'],
                tasks_failed=health_data['tasks_failed'],
                average_task_time=health_data['average_task_time'],
                error_count=health_data['error_count'],
                recovery_count=health_data['recovery_count']
            )
    
    def save_state(self):
        """Save state with backup and atomic write"""
        state = {
            'agents': self.agents,
            'task_queue': self.task_queue,
            'audit_findings': self.audit_findings,
            'knowledge_base': self.knowledge_base,
            'agent_health': {
                agent_id: {
                    'last_heartbeat': health.last_heartbeat.isoformat(),
                    'tasks_completed': health.tasks_completed,
                    'tasks_failed': health.tasks_failed,
                    'average_task_time': health.average_task_time,
                    'error_count': health.error_count,
                    'recovery_count': health.recovery_count
                }
                for agent_id, health in self.agent_health.items()
            },
            'saved_at': datetime.now().isoformat()
        }
        
        state_file = self.data_dir / "state.json"
        temp_file = self.data_dir / "state.tmp.json"
        backup_file = self.data_dir / "state.backup.json"
        
        try:
            # Write to temp file
            with open(temp_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            # Backup current state
            if state_file.exists():
                state_file.rename(backup_file)
            
            # Atomic rename
            temp_file.rename(state_file)
            
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            if temp_file.exists():
                temp_file.unlink()
    
    def register_agent(self, agent_id: str, role: str, capabilities: List[str]) -> Dict:
        """Register agent with health monitoring"""
        now = datetime.now()
        
        self.agents[agent_id] = {
            'id': agent_id,
            'role': role,
            'capabilities': capabilities,
            'status': AgentStatus.ACTIVE.value,
            'registered_at': now.isoformat(),
            'last_seen': now.isoformat(),
            'version': '2.0'
        }
        
        # Initialize health tracking
        self.agent_health[agent_id] = AgentHealth(
            last_heartbeat=now,
            tasks_completed=0,
            tasks_failed=0,
            average_task_time=0.0,
            error_count=0,
            recovery_count=0
        )
        
        # Cache capabilities
        self.agent_capabilities_cache[agent_id] = set(capabilities)
        
        self.save_state()
        logger.info(f"Agent registered: {agent_id} ({role}) with capabilities: {capabilities}")
        
        # Add to knowledge base
        self._update_knowledge_base('agent_registry', agent_id, {
            'role': role,
            'capabilities': capabilities,
            'registered': now.isoformat()
        })
        
        return self.agents[agent_id]
    
    def create_task(self, task_type: str, description: str, priority: str = 'medium', 
                   assigned_to: Optional[str] = None, context: Optional[Dict] = None,
                   dependencies: Optional[List[str]] = None) -> Dict:
        """Create task with dependencies and smart assignment"""
        task_id = str(uuid.uuid4())
        now = datetime.now()
        
        # Calculate priority score
        priority_score = TaskPriority[priority.upper()].value
        
        # Smart context enhancement
        enhanced_context = context or {}
        enhanced_context['related_findings'] = self._find_related_findings(description)
        enhanced_context['similar_tasks'] = self._find_similar_tasks(description)
        
        task = {
            'id': task_id,
            'type': task_type,
            'description': description,
            'priority': priority,
            'priority_score': priority_score,
            'status': 'pending',
            'assigned_to': assigned_to,
            'context': enhanced_context,
            'dependencies': dependencies or [],
            'created_at': now.isoformat(),
            'updated_at': now.isoformat(),
            'retry_count': 0,
            'estimated_duration': self._estimate_task_duration(task_type, description)
        }
        
        # Add to queue with smart positioning
        self._insert_task_by_priority(task)
        
        self.save_state()
        logger.info(f"Task created: {task_id} - {description} (priority: {priority})")
        
        # Update knowledge base
        self._update_knowledge_base('task_patterns', task_type, {
            'count': self.knowledge_base.get('task_patterns', {}).get(task_type, {}).get('count', 0) + 1,
            'last_created': now.isoformat()
        })
        
        return task
    
    def _insert_task_by_priority(self, task: Dict):
        """Insert task in queue based on priority and dependencies"""
        if not self.task_queue:
            self.task_queue.append(task)
            return
        
        # Find insertion point
        insert_index = len(self.task_queue)
        for i, existing_task in enumerate(self.task_queue):
            if existing_task['status'] == 'pending':
                if task['priority_score'] > existing_task.get('priority_score', 2):
                    insert_index = i
                    break
        
        self.task_queue.insert(insert_index, task)
    
    def get_next_task(self, agent_id: str, agent_role: str) -> Optional[Dict]:
        """Get next task with load balancing and capability matching"""
        # Update agent status
        if agent_id in self.agents:
            self.agents[agent_id]['last_seen'] = datetime.now().isoformat()
            self.agents[agent_id]['status'] = AgentStatus.BUSY.value
            self.agent_health[agent_id].last_heartbeat = datetime.now()
        
        # Find suitable task with smart matching and PRIORITY SORTING
        agent_capabilities = self.agent_capabilities_cache.get(agent_id, set())
        
        # CRITICAL FIX: Sort tasks by priority score (highest first)
        sorted_tasks = sorted(self.task_queue, key=lambda x: x.get('priority_score', 0), reverse=True)
        
        for task in sorted_tasks:
            if task['status'] == 'pending':
                # Check role suitability
                if not self._is_task_suitable_for_role(task, agent_role):
                    continue
                
                # Check dependencies
                if not self._are_dependencies_met(task):
                    continue
                
                # Check agent capabilities
                if not self._agent_has_required_capabilities(task, agent_capabilities):
                    continue
                
                # Check load balancing
                if self._is_agent_overloaded(agent_id):
                    logger.info(f"Agent {agent_id} is overloaded, skipping assignment")
                    continue
                
                # Assign task
                task['status'] = 'in_progress'
                task['assigned_to'] = agent_id
                task['started_at'] = datetime.now().isoformat()
                task['updated_at'] = datetime.now().isoformat()
                
                # Update load balance
                self.agent_load_balance[agent_id] += 1
                
                # Add to agent context memory
                self.context_memory[agent_id].append({
                    'task_id': task['id'],
                    'type': task['type'],
                    'started': task['started_at']
                })
                
                self.save_state()
                logger.info(f"Task {task['id']} assigned to {agent_id}")
                return task
        
        # No suitable task found
        if agent_id in self.agents:
            self.agents[agent_id]['status'] = AgentStatus.IDLE.value
        
        return None
    
    def _is_task_suitable_for_role(self, task: Dict, role: str) -> bool:
        """Enhanced role matching with fuzzy logic"""
        role_task_mapping = {
            'auditor': ['audit', 'scan', 'check', 'review', 'analyze', 'inspect', 'security'],
            'planner': ['plan', 'design', 'architect', 'breakdown', 'strategy', 'organize'],
            'coder': ['implement', 'code', 'fix', 'refactor', 'develop', 'build', 'create'],
            'tester': ['test', 'verify', 'validate', 'qa', 'check', 'assert'],
            'reviewer': ['review', 'approve', 'check_pr', 'merge', 'feedback', 'comment']
        }
        
        task_keywords = role_task_mapping.get(role, [])
        task_type_lower = task['type'].lower()
        task_desc_lower = task['description'].lower()
        
        # Check task type and description
        return any(keyword in task_type_lower or keyword in task_desc_lower 
                  for keyword in task_keywords)
    
    def _are_dependencies_met(self, task: Dict) -> bool:
        """Check if task dependencies are completed"""
        if not task.get('dependencies'):
            return True
        
        for dep_id in task['dependencies']:
            dep_task = next((t for t in self.task_queue if t['id'] == dep_id), None)
            if not dep_task or dep_task['status'] != 'completed':
                return False
        
        return True
    
    def _agent_has_required_capabilities(self, task: Dict, agent_capabilities: Set[str]) -> bool:
        """Check if agent has required capabilities for task"""
        required_caps = task.get('context', {}).get('required_capabilities', [])
        if not required_caps:
            return True
        
        return all(cap in agent_capabilities for cap in required_caps)
    
    def _is_agent_overloaded(self, agent_id: str) -> bool:
        """Check if agent is handling too many tasks"""
        current_load = self.agent_load_balance.get(agent_id, 0)
        
        # Dynamic threshold based on agent performance
        health = self.agent_health.get(agent_id)
        if health:
            if health.error_count > 5:
                return current_load >= 1  # Reduce load for struggling agents
            elif health.average_task_time > 3600:  # Tasks taking > 1 hour
                return current_load >= 2
        
        return current_load >= 3  # Default max concurrent tasks
    
    def update_task(self, task_id: str, status: str, result: Optional[Dict] = None) -> Dict:
        """Update task with retry logic and learning"""
        task = None
        for t in self.task_queue:
            if t['id'] == task_id:
                task = t
                break
        
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        previous_status = task['status']
        task['status'] = status
        task['updated_at'] = datetime.now().isoformat()
        
        if status == 'completed':
            task['completed_at'] = datetime.now().isoformat()
            
            # Calculate duration
            if 'started_at' in task:
                duration = (datetime.now() - datetime.fromisoformat(task['started_at'])).total_seconds()
                task['actual_duration'] = duration
                
                # Update agent health
                agent_id = task.get('assigned_to')
                if agent_id and agent_id in self.agent_health:
                    health = self.agent_health[agent_id]
                    health.tasks_completed += 1
                    # Update average task time
                    total_time = health.average_task_time * (health.tasks_completed - 1) + duration
                    health.average_task_time = total_time / health.tasks_completed
            
            # Update load balance
            if task.get('assigned_to'):
                self.agent_load_balance[task['assigned_to']] = max(0, self.agent_load_balance[task['assigned_to']] - 1)
            
            # Learn from completion
            self._learn_from_task_completion(task)
            
        elif status == 'failed':
            task['failed_at'] = datetime.now().isoformat()
            
            # Update agent health
            agent_id = task.get('assigned_to')
            if agent_id and agent_id in self.agent_health:
                self.agent_health[agent_id].tasks_failed += 1
                self.agent_health[agent_id].error_count += 1
            
            # Retry logic
            retry_count = task.get('retry_count', 0)
            if retry_count < self.max_retries:
                task['retry_count'] = retry_count + 1
                task['status'] = 'pending'  # Reset to pending for retry
                task['assigned_to'] = None  # Unassign for fresh assignment
                
                # Update load balance
                if task.get('assigned_to'):
                    self.agent_load_balance[task['assigned_to']] = max(0, self.agent_load_balance[task['assigned_to']] - 1)
                
                logger.info(f"Task {task_id} failed, retrying ({retry_count + 1}/{self.max_retries})")
            else:
                logger.error(f"Task {task_id} failed after {self.max_retries} retries")
        
        if result:
            task['result'] = result
        
        # Add to history
        self.task_history.append({
            'task_id': task_id,
            'status_change': f"{previous_status} -> {status}",
            'timestamp': datetime.now().isoformat()
        })
        
        self.save_state()
        logger.info(f"Task updated: {task_id} - {status}")
        return task
    
    def submit_audit_finding(self, finding: Dict) -> Dict:
        """Submit audit finding with pattern recognition"""
        finding['id'] = str(uuid.uuid4())
        finding['submitted_at'] = datetime.now().isoformat()
        finding['status'] = 'new'
        
        # Generate hash for duplicate detection
        finding_hash = self._generate_finding_hash(finding)
        finding['hash'] = finding_hash
        
        # Check for duplicates
        if self._is_duplicate_finding(finding_hash):
            logger.info(f"Duplicate finding detected: {finding['title']}")
            finding['status'] = 'duplicate'
        else:
            # Pattern recognition
            pattern = self._extract_finding_pattern(finding)
            self.finding_patterns[pattern] += 1
            finding['pattern'] = pattern
            finding['pattern_count'] = self.finding_patterns[pattern]
            
            # Add to findings
            self.audit_findings.append(finding)
            
            # Create task with enhanced context
            task = self.create_task(
                task_type='plan',
                description=f"Create implementation plan for: {finding['title']}",
                priority=finding.get('severity', 'medium'),
                context={
                    'finding_id': finding['id'],
                    'finding': finding,
                    'pattern': pattern,
                    'similar_findings': self._find_similar_findings(finding)
                }
            )
            
            finding['task_id'] = task['id']
        
        self.save_state()
        logger.info(f"Audit finding submitted: {finding['title']} (status: {finding['status']})")
        return finding
    
    def _generate_finding_hash(self, finding: Dict) -> str:
        """Generate hash for finding deduplication"""
        key_parts = [
            finding.get('category', ''),
            finding.get('file_path', ''),
            str(finding.get('line_number', '')),
            finding.get('title', '')[:50]  # First 50 chars of title
        ]
        
        return hashlib.md5('|'.join(key_parts).encode()).hexdigest()
    
    def _is_duplicate_finding(self, finding_hash: str) -> bool:
        """Check if finding is duplicate"""
        for existing in self.audit_findings:
            if existing.get('hash') == finding_hash and existing.get('status') != 'resolved':
                return True
        return False
    
    def _extract_finding_pattern(self, finding: Dict) -> str:
        """Extract pattern from finding for learning"""
        return f"{finding.get('category', 'unknown')}:{finding.get('severity', 'unknown')}"
    
    def _find_similar_findings(self, finding: Dict) -> List[Dict]:
        """Find similar past findings"""
        similar = []
        finding_category = finding.get('category', '')
        
        for past_finding in self.audit_findings[-50:]:  # Check last 50 findings
            if past_finding.get('category') == finding_category:
                similar.append({
                    'id': past_finding['id'],
                    'title': past_finding['title'],
                    'resolution': past_finding.get('resolution', 'pending')
                })
        
        return similar[:5]  # Return top 5 similar
    
    def _find_related_findings(self, description: str) -> List[str]:
        """Find findings related to task description"""
        related = []
        desc_lower = description.lower()
        
        for finding in self.audit_findings:
            if any(word in finding.get('title', '').lower() or 
                   word in finding.get('description', '').lower()
                   for word in desc_lower.split()[:5]):  # Check first 5 words
                related.append(finding['id'])
        
        return related[:3]
    
    def _find_similar_tasks(self, description: str) -> List[Dict]:
        """Find similar completed tasks for context"""
        similar = []
        desc_words = set(description.lower().split())
        
        for task in self.task_history:
            if isinstance(task, dict) and 'description' in task:
                task_words = set(task['description'].lower().split())
                similarity = len(desc_words & task_words) / len(desc_words | task_words)
                
                if similarity > 0.3:  # 30% similarity threshold
                    similar.append({
                        'task_id': task.get('id'),
                        'description': task.get('description'),
                        'duration': task.get('actual_duration'),
                        'similarity': similarity
                    })
        
        # Sort by similarity and return top 3
        similar.sort(key=lambda x: x['similarity'], reverse=True)
        return similar[:3]
    
    def _estimate_task_duration(self, task_type: str, description: str) -> float:
        """Estimate task duration based on historical data"""
        # Get similar tasks
        similar_tasks = self._find_similar_tasks(description)
        
        if similar_tasks and any(t.get('duration') for t in similar_tasks):
            # Average duration of similar tasks
            durations = [t['duration'] for t in similar_tasks if t.get('duration')]
            return sum(durations) / len(durations)
        
        # Default estimates by type
        default_estimates = {
            'audit': 300,      # 5 minutes
            'plan': 600,       # 10 minutes
            'implement': 1800, # 30 minutes
            'test': 900,       # 15 minutes
            'review': 600      # 10 minutes
        }
        
        return default_estimates.get(task_type.lower(), 600)
    
    def _learn_from_task_completion(self, task: Dict):
        """Learn from completed tasks to improve estimates"""
        task_type = task['type']
        actual_duration = task.get('actual_duration', 0)
        
        if actual_duration > 0:
            # Update knowledge base
            self._update_knowledge_base('task_durations', task_type, {
                'count': self.knowledge_base.get('task_durations', {}).get(task_type, {}).get('count', 0) + 1,
                'total_duration': self.knowledge_base.get('task_durations', {}).get(task_type, {}).get('total_duration', 0) + actual_duration,
                'average_duration': (self.knowledge_base.get('task_durations', {}).get(task_type, {}).get('total_duration', 0) + actual_duration) / 
                                  (self.knowledge_base.get('task_durations', {}).get(task_type, {}).get('count', 0) + 1)
            })
    
    def _update_knowledge_base(self, category: str, key: str, value: Any):
        """Update knowledge base with new information"""
        if category not in self.knowledge_base:
            self.knowledge_base[category] = {}
        
        self.knowledge_base[category][key] = value
    
    def get_agent_health_report(self, agent_id: str) -> Dict:
        """Get detailed health report for an agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent not found: {agent_id}")
        
        agent = self.agents[agent_id]
        health = self.agent_health.get(agent_id)
        
        report = {
            'agent_id': agent_id,
            'role': agent['role'],
            'status': agent['status'],
            'health': 'unknown'
        }
        
        if health:
            # Calculate health score
            time_since_heartbeat = (datetime.now() - health.last_heartbeat).total_seconds()
            
            if time_since_heartbeat > 300:  # 5 minutes
                report['health'] = 'critical'
            elif health.error_count > 10 or health.tasks_failed > health.tasks_completed * 0.3:
                report['health'] = 'poor'
            elif health.error_count > 5 or health.tasks_failed > health.tasks_completed * 0.1:
                report['health'] = 'fair'
            else:
                report['health'] = 'good'
            
            report['metrics'] = {
                'last_heartbeat': health.last_heartbeat.isoformat(),
                'time_since_heartbeat': time_since_heartbeat,
                'tasks_completed': health.tasks_completed,
                'tasks_failed': health.tasks_failed,
                'success_rate': health.tasks_completed / max(1, health.tasks_completed + health.tasks_failed),
                'average_task_time': health.average_task_time,
                'error_count': health.error_count,
                'recovery_count': health.recovery_count,
                'current_load': self.agent_load_balance.get(agent_id, 0)
            }
        
        return report
    
    def get_system_health(self) -> Dict:
        """Get overall system health report"""
        total_agents = len(self.agents)
        active_agents = len([a for a in self.agents.values() if a['status'] == AgentStatus.ACTIVE.value])
        
        total_tasks = len(self.task_queue)
        pending_tasks = len([t for t in self.task_queue if t['status'] == 'pending'])
        in_progress_tasks = len([t for t in self.task_queue if t['status'] == 'in_progress'])
        completed_tasks = len([t for t in self.task_queue if t['status'] == 'completed'])
        failed_tasks = len([t for t in self.task_queue if t['status'] == 'failed'])
        
        # Calculate task completion rate
        completion_rate = completed_tasks / max(1, completed_tasks + failed_tasks)
        
        # Check agent health
        unhealthy_agents = 0
        for agent_id in self.agents:
            try:
                health_report = self.get_agent_health_report(agent_id)
                if health_report['health'] in ['poor', 'critical']:
                    unhealthy_agents += 1
            except:
                pass
        
        return {
            'status': 'healthy' if unhealthy_agents == 0 and completion_rate > 0.8 else 'degraded',
            'timestamp': datetime.now().isoformat(),
            'agents': {
                'total': total_agents,
                'active': active_agents,
                'unhealthy': unhealthy_agents
            },
            'tasks': {
                'total': total_tasks,
                'pending': pending_tasks,
                'in_progress': in_progress_tasks,
                'completed': completed_tasks,
                'failed': failed_tasks,
                'completion_rate': completion_rate
            },
            'findings': {
                'total': len(self.audit_findings),
                'patterns': dict(self.finding_patterns)
            },
            'knowledge_base': {
                'categories': list(self.knowledge_base.keys()),
                'size': len(json.dumps(self.knowledge_base))
            }
        }
    
    def recover_agent(self, agent_id: str) -> bool:
        """Attempt to recover a failed agent"""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        health = self.agent_health.get(agent_id)
        
        # Reset agent status
        agent['status'] = AgentStatus.RECOVERING.value
        
        # Clear agent's current tasks
        for task in self.task_queue:
            if task.get('assigned_to') == agent_id and task['status'] == 'in_progress':
                task['status'] = 'pending'
                task['assigned_to'] = None
                logger.info(f"Unassigned task {task['id']} from recovering agent {agent_id}")
        
        # Reset load balance
        self.agent_load_balance[agent_id] = 0
        
        # Update health
        if health:
            health.recovery_count += 1
            health.error_count = 0
            health.last_heartbeat = datetime.now()
        
        # Schedule status update
        asyncio.create_task(self._complete_recovery(agent_id))
        
        self.save_state()
        logger.info(f"Agent {agent_id} recovery initiated")
        return True
    
    async def _complete_recovery(self, agent_id: str):
        """Complete agent recovery after delay"""
        await asyncio.sleep(30)  # 30 second recovery period
        
        if agent_id in self.agents:
            self.agents[agent_id]['status'] = AgentStatus.ACTIVE.value
            logger.info(f"Agent {agent_id} recovery completed")
    
    async def _health_monitor_loop(self):
        """Background task to monitor agent health"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                for agent_id, agent in list(self.agents.items()):
                    health = self.agent_health.get(agent_id)
                    if health:
                        time_since_heartbeat = (datetime.now() - health.last_heartbeat).total_seconds()
                        
                        if time_since_heartbeat > 300:  # 5 minutes
                            if agent['status'] != AgentStatus.FAILED.value:
                                logger.warning(f"Agent {agent_id} appears to be unresponsive")
                                agent['status'] = AgentStatus.FAILED.value
                                
                                # Attempt recovery
                                self.recover_agent(agent_id)
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
    
    async def _task_optimizer_loop(self):
        """Background task to optimize task queue"""
        while True:
            try:
                await asyncio.sleep(120)  # Optimize every 2 minutes
                
                # Re-prioritize stale tasks
                for task in self.task_queue:
                    if task['status'] == 'pending':
                        created_time = datetime.fromisoformat(task['created_at'])
                        age_minutes = (datetime.now() - created_time).total_seconds() / 60
                        
                        # Boost priority of old tasks
                        if age_minutes > 30 and task.get('priority_score', 2) < 4:
                            task['priority_score'] = min(4, task.get('priority_score', 2) + 1)
                            logger.info(f"Boosted priority of stale task {task['id']}")
                
                # Re-sort queue
                self.task_queue.sort(key=lambda t: (
                    t['status'] != 'pending',  # Pending first
                    -t.get('priority_score', 2),  # Higher priority first
                    t['created_at']  # Older first
                ))
                
            except Exception as e:
                logger.error(f"Task optimizer error: {e}")
    
    async def _knowledge_sync_loop(self):
        """Background task to sync knowledge base"""
        while True:
            try:
                await asyncio.sleep(300)  # Sync every 5 minutes
                
                # Save knowledge base separately for backup
                kb_file = self.data_dir / "knowledge_base.json"
                with open(kb_file, 'w') as f:
                    json.dump(self.knowledge_base, f, indent=2)
                
                logger.info("Knowledge base synced")
                
            except Exception as e:
                logger.error(f"Knowledge sync error: {e}")
    
    def create_worktree(self, branch_name: str) -> str:
        """Create a git worktree with enhanced error handling"""
        # Validate branch name to prevent command injection
        if not self._validate_branch_name(branch_name):
            raise ValueError(f"Invalid branch name: {branch_name}")
        
        worktree_path = self.base_dir / "agent-workspaces" / branch_name
        
        if worktree_path.exists():
            logger.info(f"Worktree already exists: {worktree_path}")
            return str(worktree_path)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Ensure parent directory exists
                worktree_path.parent.mkdir(exist_ok=True)
                
                # Check if we're in a git repository
                result = self._execute_command(
                    ['git', 'rev-parse', '--git-dir'],
                    cwd=self.base_dir
                )
                
                if result.returncode != 0:
                    # Initialize git if not present
                    self._execute_command(['git', 'init'], cwd=self.base_dir, check=True)
                    self._execute_command(['git', 'add', '.'], cwd=self.base_dir, check=True)
                    self._execute_command(['git', 'commit', '-m', 'Initial commit'], cwd=self.base_dir, check=True)
                
                # Create worktree with proper escaping
                # Use shlex.quote for shell-safe parameters
                safe_path = shlex.quote(str(worktree_path))
                safe_branch = shlex.quote(branch_name)
                
                # Log the command for security auditing
                logger.info(f"Executing git worktree command: path={safe_path}, branch={safe_branch}")
                
                result = self._execute_command([
                    'git', 'worktree', 'add', 
                    str(worktree_path), 
                    '-b', branch_name
                ], cwd=self.base_dir)
                
                if result.returncode == 0:
                    self.worktrees[branch_name] = str(worktree_path)
                    logger.info(f"Created worktree: {branch_name} at {worktree_path}")
                    return str(worktree_path)
                else:
                    # Sanitize error message to prevent information leakage
                    sanitized_error = self._sanitize_error_message(result.stderr)
                    logger.error(f"Failed to create worktree: {sanitized_error}")
                    
                    # Try to clean up and retry
                    if attempt < max_retries - 1:
                        self._execute_command(['git', 'worktree', 'prune'], cwd=self.base_dir)
                        time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Worktree creation error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        raise RuntimeError(f"Failed to create worktree after {max_retries} attempts")
    
    def get_project_context(self) -> Dict:
        """Get enhanced project context with insights"""
        context = {
            'base_dir': str(self.base_dir),
            'timestamp': datetime.now().isoformat(),
            'agents': {
                'total': len(self.agents),
                'by_role': defaultdict(int),
                'by_status': defaultdict(int),
                'health_summary': {}
            },
            'tasks': {
                'total': len(self.task_queue),
                'by_status': defaultdict(int),
                'by_type': defaultdict(int),
                'by_priority': defaultdict(int),
                'average_completion_time': 0
            },
            'findings': {
                'total': len(self.audit_findings),
                'by_severity': defaultdict(int),
                'by_category': defaultdict(int),
                'top_patterns': []
            },
            'system_health': self.get_system_health(),
            'recent_activity': list(self.task_history)[-10:]
        }
        
        # Aggregate agent data
        for agent in self.agents.values():
            context['agents']['by_role'][agent['role']] += 1
            context['agents']['by_status'][agent['status']] += 1
        
        # Aggregate task data
        completed_durations = []
        for task in self.task_queue:
            context['tasks']['by_status'][task['status']] += 1
            context['tasks']['by_type'][task['type']] += 1
            context['tasks']['by_priority'][task['priority']] += 1
            
            if task['status'] == 'completed' and 'actual_duration' in task:
                completed_durations.append(task['actual_duration'])
        
        if completed_durations:
            context['tasks']['average_completion_time'] = sum(completed_durations) / len(completed_durations)
        
        # Aggregate findings data
        for finding in self.audit_findings:
            context['findings']['by_severity'][finding.get('severity', 'unknown')] += 1
            context['findings']['by_category'][finding.get('category', 'unknown')] += 1
        
        # Top patterns
        top_patterns = sorted(self.finding_patterns.items(), key=lambda x: x[1], reverse=True)[:5]
        context['findings']['top_patterns'] = [{'pattern': p[0], 'count': p[1]} for p in top_patterns]
        
        # Read project goals if exists
        goals_file = self.base_dir / "PROJECT_GOALS.md"
        if goals_file.exists():
            context['project_goals'] = goals_file.read_text()
        
        # Add insights
        context['insights'] = self._generate_insights(context)
        
        return context
    
    def _generate_insights(self, context: Dict) -> List[str]:
        """Generate actionable insights from context"""
        insights = []
        
        # Task insights
        if context['tasks']['by_status']['failed'] > context['tasks']['total'] * 0.2:
            insights.append("High task failure rate detected. Consider reviewing task complexity or agent capabilities.")
        
        if context['tasks']['by_status']['pending'] > 50:
            insights.append("Large task backlog. Consider scaling up agents or optimizing task processing.")
        
        # Agent insights
        if context['agents']['by_status']['failed'] > 0:
            insights.append(f"{context['agents']['by_status']['failed']} agents in failed state. Recovery initiated.")
        
        # Finding insights
        if context['findings']['by_severity']['critical'] > 0:
            insights.append(f"{context['findings']['by_severity']['critical']} critical findings require immediate attention.")
        
        # Pattern insights
        if context['findings']['top_patterns']:
            top_pattern = context['findings']['top_patterns'][0]
            insights.append(f"Most common issue pattern: {top_pattern['pattern']} ({top_pattern['count']} occurrences)")
        
        return insights
    
    def _validate_branch_name(self, branch_name: str) -> bool:
        """Validate branch name to prevent command injection"""
        # Allow only alphanumeric, hyphens, underscores, and forward slashes
        import re
        
        if not branch_name:
            return False
        
        # Check length
        if len(branch_name) > 100:
            return False
        
        # Check for dangerous patterns
        dangerous_patterns = [
            '..',  # Directory traversal
            '~',   # Home directory
            '$',   # Variable expansion
            '`',   # Command substitution
            ';',   # Command separator
            '&',   # Background execution
            '|',   # Pipe
            '>',   # Redirect
            '<',   # Redirect
            '\n',  # Newline
            '\r',  # Carriage return
            '\x00' # Null byte
        ]
        
        for pattern in dangerous_patterns:
            if pattern in branch_name:
                logger.warning(f"Rejected branch name containing dangerous pattern: {pattern}")
                return False
        
        # Allow only safe characters
        if not re.match(r'^[a-zA-Z0-9/_-]+$', branch_name):
            logger.warning(f"Rejected branch name with invalid characters: {branch_name}")
            return False
        
        return True
    
    def _execute_command(self, cmd: List[str], cwd: Optional[Path] = None, check: bool = False) -> subprocess.CompletedProcess:
        """Execute command with security checks and logging"""
        if not cmd:
            raise ValueError("Empty command")
        
        # Validate command against whitelist
        command_name = cmd[0]
        if command_name not in self.allowed_commands:
            raise SecurityError(f"Command not allowed: {command_name}")
        
        # Check if specific subcommand is allowed
        if len(cmd) > 1:
            subcommand = cmd[1]
            allowed_subcommands = self.allowed_commands[command_name]
            if allowed_subcommands and subcommand not in allowed_subcommands:
                raise SecurityError(f"Subcommand not allowed: {command_name} {subcommand}")
        
        # Log command execution for security auditing
        safe_cmd = ' '.join(shlex.quote(arg) for arg in cmd)
        logger.info(f"Executing command: {safe_cmd} in {cwd or 'current directory'}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd,
                check=check,
                timeout=30  # 30 second timeout for safety
            )
            
            # Log result for auditing
            if result.returncode != 0:
                logger.warning(f"Command failed with code {result.returncode}")
            
            return result
            
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {safe_cmd}")
            raise
        except Exception as e:
            logger.error(f"Command execution error: {type(e).__name__}")
            raise
    
    def _sanitize_error_message(self, error_msg: str) -> str:
        """Sanitize error messages to prevent information leakage"""
        if not error_msg:
            return "Unknown error"
        
        # Remove sensitive paths
        import re
        
        # Replace absolute paths with relative ones
        error_msg = re.sub(r'/[a-zA-Z0-9/_.-]+/', '<path>/', error_msg)
        
        # Remove user-specific information
        error_msg = re.sub(r'/home/[^/]+/', '/home/<user>/', error_msg)
        error_msg = re.sub(r'/Users/[^/]+/', '/Users/<user>/', error_msg)
        
        # Truncate if too long
        if len(error_msg) > 200:
            error_msg = error_msg[:200] + '...'
        
        return error_msg


class SecurityError(Exception):
    """Raised when a security policy is violated"""
    pass


# Create enhanced coordinator instance
coordinator = EnhancedAgentCoordinator()

# Create MCP server
server = Server("mcp-coordinator-v2")

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
            description="Update task status with automatic retry logic",
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
            description="Submit a new audit finding with deduplication",
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
            description="Get comprehensive project context with insights",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="create_task",
            description="Create a new task with smart prioritization",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_type": {"type": "string", "description": "Task type (audit, plan, implement, test, review)"},
                    "description": {"type": "string", "description": "Task description"},
                    "priority": {"type": "string", "description": "Priority level (low, medium, high, critical)"},
                    "assigned_to": {"type": "string", "description": "Optional agent ID to assign to"},
                    "context": {"type": "object", "description": "Additional context data"},
                    "dependencies": {"type": "array", "items": {"type": "string"}, "description": "Task IDs this task depends on"}
                },
                "required": ["task_type", "description"]
            }
        ),
        types.Tool(
            name="get_agent_health",
            description="Get detailed health report for an agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Agent identifier"}
                },
                "required": ["agent_id"]
            }
        ),
        types.Tool(
            name="get_system_health",
            description="Get overall system health report",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="recover_agent",
            description="Attempt to recover a failed agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Agent identifier to recover"}
                },
                "required": ["agent_id"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls with enhanced error handling"""
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
            path = await asyncio.get_event_loop().run_in_executor(
                None, coordinator.create_worktree, arguments["branch_name"]
            )
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
                context=arguments.get("context"),
                dependencies=arguments.get("dependencies")
            )
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_agent_health":
            result = coordinator.get_agent_health_report(arguments["agent_id"])
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_system_health":
            result = coordinator.get_system_health()
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "recover_agent":
            success = coordinator.recover_agent(arguments["agent_id"])
            return [types.TextContent(type="text", text=json.dumps({
                "success": success,
                "message": "Agent recovery initiated" if success else "Agent not found"
            }))]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"Tool execution error: {e}\n{traceback.format_exc()}")
        return [types.TextContent(type="text", text=json.dumps({
            "error": str(e),
            "type": type(e).__name__,
            "tool": name
        }, indent=2))]

async def main():
    """Run the enhanced MCP server"""
    from mcp.server.stdio import stdio_server
    
    logger.info("Enhanced MCP Coordinator Server v2 starting...")
    logger.info(f"Base directory: {coordinator.base_dir}")
    logger.info(f"Data directory: {coordinator.data_dir}")
    
    # Start background tasks
    coordinator._tasks = [
        asyncio.create_task(coordinator._health_monitor_loop()),
        asyncio.create_task(coordinator._task_optimizer_loop()),
        asyncio.create_task(coordinator._knowledge_sync_loop())
    ]
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-coordinator-v2",
                server_version="2.0.0",
                capabilities={}
            )
        )

if __name__ == "__main__":
    asyncio.run(main())