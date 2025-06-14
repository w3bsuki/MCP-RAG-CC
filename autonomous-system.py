#!/usr/bin/env python3
"""
Enhanced Autonomous Multi-Agent System Launcher v2
Advanced agent orchestration with fault tolerance and intelligent monitoring
"""

import subprocess
import time
import os
import json
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
import signal
import atexit
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue
import psutil
import random
import math
import shlex
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('autonomous-system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("autonomous-launcher-v2")

class AgentState(Enum):
    STARTING = "starting"
    RUNNING = "running"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    STOPPED = "stopped"

@dataclass
class AgentInfo:
    id: str
    role: str
    window: str
    pid: Optional[int] = None
    state: AgentState = AgentState.STARTING
    started_at: str = ""
    last_activity: str = ""
    error_count: int = 0
    restart_count: int = 0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0

class EnhancedAutonomousLauncher:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.config_file = self.base_dir / ".claude" / "config.json"
        self.mcp_settings = self.base_dir / "claude_mcp_settings.json"
        self.session_name = "autonomous-claude"
        self.agents: Dict[str, AgentInfo] = {}
        self.monitoring_thread = None
        self.stop_event = threading.Event()
        self.message_queue = queue.Queue()
        
        # Performance settings
        self.max_agent_memory = 2048  # MB
        self.max_agent_cpu = 80  # %
        self.health_check_interval = 30  # seconds
        self.agent_startup_delay = 5  # seconds between agent launches
        
        # Retry settings
        self.max_retries = 3
        self.base_retry_delay = 1  # seconds
        self.max_retry_delay = 60  # seconds
        self.retry_multiplier = 2
        
        # Security: Whitelist of allowed command patterns
        self.allowed_command_patterns = [
            r'^claude\s+--dangerously-skip-permissions\s+"[^"]*"$',  # Claude launch command
            r'^/exit$',  # Exit command
            r'^/help$',  # Help command
            r'^cd\s+[\w/.-]+$',  # Change directory command
            r'^export\s+\w+=[\w/.-]+$',  # Environment variable exports
            r'^source\s+[\w/.]+/activate$',  # Virtual environment activation
            r'^#\s+.*$',  # Comments
            r'^python3?\s+[\w/.-]+\.py(\s+[\w\s-]+)?$',  # Python script execution with args
            r'^read\s+[\w/.-]+$',  # Read file command
            r'^I am agent .* with role .*\.$',  # Agent identification
            r'^Let me begin by reading my instructions now\.$',  # Startup message
            r'^# Agent Startup Sequence$',  # Startup sequence header
            r'^## Step \d+: .*$',  # Startup sequence steps
            r'^First, I\'ll read my detailed role instructions:$',  # Startup instruction
            r'^After reading instructions, I\'ll register with the MCP coordinator:$',  # Startup instruction
            r'^Use mcp-coordinator\.register_agent with my ID and capabilities\.$',  # Startup instruction
            r'^Set up my working environment and memory\.$',  # Startup instruction
            r'^Start my continuous work cycle as defined in my instructions\.$',  # Startup instruction
            r'^IMPORTANT: .*$',  # Important messages
            r'^\d+\. .*$',  # Numbered lists
            r'^Starting initialization\.\.\.$'  # Initialization message
        ]
        
        # Load configuration
        self.load_config()
        
        # Initialize state directory
        self.state_dir = self.base_dir / "mcp-coordinator" / "launcher"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Register cleanup handlers
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def load_config(self):
        """Load and validate configuration"""
        if not self.config_file.exists():
            logger.error("Configuration file not found at .claude/config.json")
            self.create_default_config()
        
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
                
            # Validate configuration
            self.validate_config()
            logger.info("Configuration loaded successfully")
            
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in config file", exc_info=True)
            sys.exit(1)
        except Exception as e:
            logger.error("Failed to load config", exc_info=True)
            sys.exit(1)
    
    def validate_config(self):
        """Validate configuration structure"""
        required_sections = ['agents', 'automation', 'git']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required config section: {section}")
        
        # Validate agent roles
        if 'roles' not in self.config['agents']:
            raise ValueError("No agent roles defined in config")
    
    def create_default_config(self):
        """Create a default configuration file"""
        default_config = {
            "project": {
                "name": "Autonomous System",
                "description": "Multi-agent development system"
            },
            "agents": {
                "roles": {
                    "auditor": {
                        "description": "Code quality auditor",
                        "capabilities": ["code_analysis"],
                        "max_instances": 1
                    }
                }
            },
            "automation": {
                "audit_interval": 300,
                "auto_create_prs": false
            },
            "git": {
                "branch_prefix": "auto/"
            }
        }
        
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        logger.info(f"Created default config at {self.config_file}")
    
    def signal_handler(self, signum, frame):
        """Enhanced signal handling"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.stop_event.set()
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Enhanced cleanup with state persistence"""
        logger.info("Starting cleanup process...")
        
        # Stop monitoring
        self.stop_event.set()
        
        # Save complete system state
        self.save_system_state()
        
        # Gracefully stop all agents
        for agent_id, agent in self.agents.items():
            try:
                self.stop_agent_gracefully(agent)
            except Exception as e:
                logger.error(f"Error stopping agent {agent_id}", exc_info=True)
        
        # Wait for monitoring thread
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        logger.info("Cleanup completed")
    
    def save_system_state(self):
        """Save comprehensive system state"""
        state = {
            'shutdown_time': datetime.now().isoformat(),
            'system_info': {
                'uptime': self.get_system_uptime(),
                'total_agents_launched': len(self.agents),
                'successful_runs': sum(1 for a in self.agents.values() if a.error_count == 0),
                'total_restarts': sum(a.restart_count for a in self.agents.values())
            },
            'agents': {
                agent_id: {
                    'id': agent.id,
                    'role': agent.role,
                    'state': agent.state.value,
                    'started_at': agent.started_at,
                    'last_activity': agent.last_activity,
                    'error_count': agent.error_count,
                    'restart_count': agent.restart_count,
                    'final_memory': agent.memory_usage,
                    'final_cpu': agent.cpu_usage
                }
                for agent_id, agent in self.agents.items()
            },
            'performance_stats': self.collect_performance_stats()
        }
        
        state_file = self.state_dir / f"state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        # Also save as latest
        latest_file = self.state_dir / "latest_state.json"
        with open(latest_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"System state saved to {state_file}")
    
    def get_system_uptime(self) -> str:
        """Calculate system uptime"""
        if not self.agents:
            return "0:00:00"
        
        earliest_start = min(
            datetime.fromisoformat(a.started_at) 
            for a in self.agents.values() 
            if a.started_at
        )
        uptime = datetime.now() - earliest_start
        return str(uptime).split('.')[0]  # Remove microseconds
    
    def collect_performance_stats(self) -> Dict:
        """Collect system-wide performance statistics"""
        try:
            return {
                'total_memory_usage': sum(a.memory_usage for a in self.agents.values()),
                'average_cpu_usage': sum(a.cpu_usage for a in self.agents.values()) / max(len(self.agents), 1),
                'system_memory_available': psutil.virtual_memory().available / (1024 * 1024),
                'system_cpu_percent': psutil.cpu_percent(interval=1)
            }
        except:
            return {}
    
    def check_dependencies(self) -> bool:
        """Enhanced dependency checking with version validation"""
        logger.info("Checking system dependencies...")
        
        dependencies = {
            'tmux': {
                'command': ['tmux', '-V'],
                'min_version': '2.0',
                'install': 'sudo apt-get install tmux'
            },
            'claude': {
                'command': ['claude', '--version'],
                'min_version': None,
                'install': 'npm install -g @anthropic-ai/claude-code'
            },
            'git': {
                'command': ['git', '--version'],
                'min_version': '2.0',
                'install': 'sudo apt-get install git'
            }
        }
        
        all_ok = True
        
        for dep_name, dep_info in dependencies.items():
            try:
                result = subprocess.run(
                    dep_info['command'], 
                    capture_output=True, 
                    text=True, 
                    check=True,
                    timeout=10
                )
                version = result.stdout.strip()
                
                # Version checking could be enhanced here
                logger.info(f"✅ {dep_name} installed: {version}")
                
            except subprocess.TimeoutExpired:
                logger.error(f"❌ {dep_name} check timed out. Install with: {dep_info['install']}")
                all_ok = False
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ {dep_name} not found or failed. Install with: {dep_info['install']}")
                logger.debug(f"Command failed with return code {e.returncode}: {e.stderr}")
                all_ok = False
            except FileNotFoundError:
                logger.error(f"❌ {dep_name} command not found. Install with: {dep_info['install']}")
                all_ok = False
            except Exception as e:
                logger.error(f"❌ Error checking {dep_name}: {e}", exc_info=True)
                all_ok = False
        
        # Check Python packages
        required_packages = {
            'mcp': '0.1.0',
            'psutil': '5.0.0'
        }
        
        for package, min_version in required_packages.items():
            try:
                module = __import__(package)
                version = getattr(module, '__version__', 'unknown')
                logger.info(f"✅ {package} installed: {version}")
            except ImportError as e:
                logger.error(f"❌ {package} not found. Install with: pip install {package}>={min_version}")
                logger.debug(f"Import error details: {e}")
                all_ok = False
            except Exception as e:
                logger.error(f"❌ Error checking {package}: {e}", exc_info=True)
                all_ok = False
        
        # Check system resources
        try:
            if not self.check_system_resources():
                all_ok = False
        except Exception as e:
            logger.error(f"❌ System resource check failed: {e}", exc_info=True)
            all_ok = False
        
        return all_ok
    
    def check_system_resources(self) -> bool:
        """Check if system has adequate resources"""
        try:
            memory = psutil.virtual_memory()
            cpu_count = psutil.cpu_count()
            
            # Minimum requirements
            min_memory_gb = 4
            min_cpu_cores = 2
            
            memory_gb = memory.total / (1024**3)
            
            if memory_gb < min_memory_gb:
                logger.warning(f"⚠️  Low memory: {memory_gb:.1f}GB (recommended: {min_memory_gb}GB+)")
                return False
            
            if cpu_count < min_cpu_cores:
                logger.warning(f"⚠️  Low CPU cores: {cpu_count} (recommended: {min_cpu_cores}+)")
                return False
            
            logger.info(f"✅ System resources: {memory_gb:.1f}GB RAM, {cpu_count} CPU cores")
            return True
            
        except Exception as e:
            logger.error(f"Failed to check system resources: {e}")
            return True  # Continue anyway
    
    def setup_tmux_session(self) -> bool:
        """Enhanced tmux session setup with validation"""
        logger.info(f"Setting up tmux session: {self.session_name}")
        
        try:
            # Check for existing session
            result = subprocess.run(
                ['tmux', 'has-session', '-t', self.session_name],
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.warning("Existing session found, killing it...")
                try:
                    subprocess.run(['tmux', 'kill-session', '-t', self.session_name], 
                                 check=True, timeout=10)
                    time.sleep(1)
                except subprocess.CalledProcessError as e:
                    logger.error("Failed to kill existing session", exc_info=True)
                    return False
            
            # Create new session with specific settings
            subprocess.run([
                'tmux', 'new-session', '-d', '-s', self.session_name,
                '-x', '120', '-y', '40'  # Set initial size
            ], check=True, timeout=10)
            
            # Set tmux options for better agent handling
            tmux_options = [
                ('set-option', '-g', 'history-limit', '10000'),
                ('set-option', '-g', 'mouse', 'on'),
                ('set-window-option', '-g', 'monitor-activity', 'on')
            ]
            
            for option in tmux_options:
                try:
                    subprocess.run(['tmux'] + list(option) + ['-t', self.session_name], 
                                 check=True, timeout=5)
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Failed to set tmux option {option}", exc_info=True)
            
            logger.info("✅ Tmux session created successfully")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("Tmux session setup timed out")
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create tmux session: {e}")
            logger.debug(f"Command failed with return code {e.returncode}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error setting up tmux session: {e}", exc_info=True)
            return False
    
    def create_agent_window(self, role: str, index: int = 0) -> Optional[str]:
        """Create tmux window with error handling"""
        window_name = f"{role}-{index}" if index > 0 else role
        
        try:
            # Create window
            subprocess.run([
                'tmux', 'new-window', '-t', f'{self.session_name}:', 
                '-n', window_name, '-d'
            ], check=True)
            
            # Set window options
            subprocess.run([
                'tmux', 'set-window-option', '-t', 
                f'{self.session_name}:{window_name}',
                'remain-on-exit', 'on'
            ])
            
            logger.info(f"Created window: {window_name}")
            return window_name
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create window {window_name}: {e}")
            return None
    
    def send_to_agent(self, window: str, command: str):
        """Send command with exponential backoff retry logic"""
        # Validate window name to prevent injection
        if not window or not window.replace("-", "").replace("_", "").isalnum():
            logger.error(f"Invalid window name: {window}")
            raise ValueError(f"Invalid window name: {window}")
        
        # Check command against whitelist
        command_allowed = False
        for pattern in self.allowed_command_patterns:
            if re.match(pattern, command):
                command_allowed = True
                break
        
        if not command_allowed:
            logger.error(f"Command not in whitelist: {command}")
            raise ValueError(f"Command not allowed: {command}")
        
        # Security logging for command execution
        logger.info(f"Executing command for window {window}: {command[:50]}...")
        
        for attempt in range(self.max_retries):
            try:
                # Clear any existing input
                subprocess.run([
                    'tmux', 'send-keys', '-t', f'{self.session_name}:{window}',
                    'C-c'  # Cancel any ongoing input
                ], capture_output=True, timeout=5)
                
                time.sleep(0.5)
                
                # Send the command with proper escaping
                # Note: tmux send-keys takes the command as literal text, not shell commands
                # So we don't need shlex.quote() here, but we validate the input
                subprocess.run([
                    'tmux', 'send-keys', '-t', f'{self.session_name}:{window}',
                    command, 'Enter'
                ], check=True, timeout=10)
                
                return
                
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                if attempt < self.max_retries - 1:
                    # Calculate exponential backoff delay
                    delay = self.base_retry_delay * (self.retry_multiplier ** attempt)
                    jitter = random.uniform(0.1, 0.3) * delay
                    total_delay = delay + jitter
                    
                    logger.warning(f"Retry {attempt + 1}/{self.max_retries} sending to {window} after {total_delay:.1f}s: {e}")
                    time.sleep(total_delay)
                else:
                    logger.error(f"Failed to send command to {window} after {self.max_retries} attempts: {e}")
                    raise
    
    def launch_agent(self, role: str, index: int = 0) -> Optional[str]:
        """Enhanced agent launch with health checks"""
        agent_id = f"{role}-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{index}"
        
        logger.info(f"Launching agent: {agent_id}")
        
        try:
            # Create window
            window = self.create_agent_window(role, index)
            if not window:
                logger.error(f"Failed to create window for agent {agent_id}")
                return None
            
            # Create agent info
            agent = AgentInfo(
                id=agent_id,
                role=role,
                window=window,
                started_at=datetime.now().isoformat(),
                state=AgentState.STARTING
            )
            
            # Store agent early for tracking
            self.agents[agent_id] = agent
            # Set up environment with error handling
            try:
                env_commands = [
                    f"cd {self.base_dir}",
                    f"export CLAUDE_MCP_SETTINGS_PATH={self.mcp_settings}",
                    f"export AGENT_ID={agent_id}",
                    f"export AGENT_ROLE={role}",
                    "export PYTHONUNBUFFERED=1"
                ]
                
                for cmd in env_commands:
                    self.send_to_agent(window, cmd)
                    time.sleep(0.2)
            except Exception as e:
                logger.error(f"Failed to set up environment for {agent_id}: {e}")
                raise
            
            # Prepare initialization prompt
            instructions_file = self.base_dir / ".claude" / "agents" / f"{role}.md"
            
            init_prompt = f"""I am agent {agent_id} with role {role}.

IMPORTANT: I will operate autonomously following my instructions. I will:
1. Read my role instructions
2. Register with the MCP coordinator
3. Begin my continuous work loop
4. Monitor my own health and report issues

Starting initialization..."""
            
            # Launch Claude with comprehensive initial setup
            try:
                launch_command = f'claude --dangerously-skip-permissions "{init_prompt}"'
                self.send_to_agent(window, launch_command)
                
                # Wait for Claude to start
                time.sleep(3)
            except Exception as e:
                logger.error(f"Failed to launch Claude for {agent_id}: {e}")
                raise
            
            # Send detailed startup instructions
            startup_sequence = f"""# Agent Startup Sequence

## Step 1: Read Instructions
First, I'll read my detailed role instructions:

read {instructions_file}

## Step 2: Register with Coordinator
After reading instructions, I'll register with the MCP coordinator:

Use mcp-coordinator.register_agent with my ID and capabilities.

## Step 3: Initialize Working State
Set up my working environment and memory.

## Step 4: Begin Autonomous Loop
Start my continuous work cycle as defined in my instructions.

Let me begin by reading my instructions now."""
            
            self.send_to_agent(window, startup_sequence)
            
            # Get process ID with retry
            time.sleep(2)
            try:
                agent.pid = self.get_agent_pid(window)
                if not agent.pid:
                    logger.warning(f"Could not get PID for {agent_id}, will retry later")
            except Exception as e:
                logger.warning(f"Error getting PID for {agent_id}: {e}")
            
            # Update state
            agent.state = AgentState.RUNNING
            agent.last_activity = datetime.now().isoformat()
            
            logger.info(f"✅ Agent {agent_id} launched successfully (PID: {agent.pid})")
            return agent_id
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed while launching agent {agent_id}: {e}")
            logger.error(f"Command output: {e.output if hasattr(e, 'output') else 'N/A'}")
            if agent_id in self.agents:
                self.agents[agent_id].state = AgentState.ERROR
                self.agents[agent_id].error_count += 1
            return None
        except Exception as e:
            logger.error(f"Unexpected error launching agent {agent_id}: {e}", exc_info=True)
            if agent_id in self.agents:
                self.agents[agent_id].state = AgentState.ERROR
                self.agents[agent_id].error_count += 1
            return None
    
    def get_agent_pid(self, window: str) -> Optional[int]:
        """Get PID of agent process"""
        try:
            result = subprocess.run([
                'tmux', 'list-panes', '-t', f'{self.session_name}:{window}',
                '-F', '#{pane_pid}'
            ], capture_output=True, text=True, check=True)
            
            pid = int(result.stdout.strip())
            return pid
            
        except Exception as e:
            logger.error(f"Failed to get PID for {window}: {e}")
            return None
    
    def stop_agent_gracefully(self, agent: AgentInfo):
        """Gracefully stop an agent"""
        logger.info(f"Stopping agent {agent.id}...")
        
        try:
            # Send exit command
            self.send_to_agent(agent.window, "/exit")
            time.sleep(2)
            
            # Send Ctrl+D to close Claude
            subprocess.run([
                'tmux', 'send-keys', '-t', 
                f'{self.session_name}:{agent.window}', 'C-d'
            ])
            
            # Update state
            agent.state = AgentState.STOPPED
            
        except Exception as e:
            logger.error(f"Error stopping agent {agent.id}", exc_info=True)
    
    def launch_all_agents(self):
        """Launch all configured agents with intelligent scheduling"""
        logger.info("Launching all configured agents...")
        
        roles = self.config.get('agents', {}).get('roles', {})
        total_agents = 0
        
        for role, role_config in roles.items():
            max_instances = role_config.get('max_instances', 1)
            priority = role_config.get('priority', 'medium')
            
            # Launch high priority agents first
            if priority == 'high':
                for i in range(max_instances):
                    agent_id = self.launch_agent(role, i)
                    if agent_id:
                        total_agents += 1
                    time.sleep(self.agent_startup_delay)
        
        # Then launch medium and low priority
        for priority_level in ['medium', 'low']:
            for role, role_config in roles.items():
                if role_config.get('priority', 'medium') == priority_level:
                    max_instances = role_config.get('max_instances', 1)
                    for i in range(max_instances):
                        agent_id = self.launch_agent(role, i)
                        if agent_id:
                            total_agents += 1
                        time.sleep(self.agent_startup_delay)
        
        logger.info(f"✅ Launched {total_agents} agents successfully")
    
    def monitor_agent_health(self, agent_id: str, agent: AgentInfo) -> Dict[str, Any]:
        """Monitor individual agent health"""
        health = {
            'healthy': True,
            'issues': [],
            'metrics': {}
        }
        
        try:
            # Check if process is alive
            if agent.pid and not psutil.pid_exists(agent.pid):
                health['healthy'] = False
                health['issues'].append('Process not found')
                return health
            
            # Get process info
            if agent.pid:
                try:
                    process = psutil.Process(agent.pid)
                    
                    # Memory check
                    memory_mb = process.memory_info().rss / (1024 * 1024)
                    agent.memory_usage = memory_mb
                    health['metrics']['memory_mb'] = memory_mb
                    
                    if memory_mb > self.max_agent_memory:
                        health['healthy'] = False
                        health['issues'].append(f'High memory usage: {memory_mb:.1f}MB')
                    
                    # CPU check
                    cpu_percent = process.cpu_percent(interval=1)
                    agent.cpu_usage = cpu_percent
                    health['metrics']['cpu_percent'] = cpu_percent
                    
                    if cpu_percent > self.max_agent_cpu:
                        health['issues'].append(f'High CPU usage: {cpu_percent:.1f}%')
                    
                except psutil.NoSuchProcess:
                    health['healthy'] = False
                    health['issues'].append('Process terminated')
            
            # Check window responsiveness
            try:
                result = subprocess.run([
                    'tmux', 'capture-pane', '-t', 
                    f'{self.session_name}:{agent.window}', '-p'
                ], capture_output=True, text=True)
                
                last_output = result.stdout.strip()
                
                # Check for error patterns
                error_patterns = [
                    'Error:', 'Exception:', 'Failed:', 
                    'Traceback', 'Claude Code has stopped'
                ]
                
                for pattern in error_patterns:
                    if pattern in last_output:
                        health['issues'].append(f'Error detected: {pattern}')
                        agent.error_count += 1
                
            except Exception as e:
                logger.error(f"Failed to capture pane for {agent_id}: {e}")
            
            # Check last activity
            if agent.last_activity:
                last_active = datetime.fromisoformat(agent.last_activity)
                inactive_time = (datetime.now() - last_active).total_seconds()
                
                if inactive_time > 600:  # 10 minutes
                    health['issues'].append(f'Inactive for {inactive_time/60:.1f} minutes')
            
            # Update agent state based on health
            if not health['healthy']:
                agent.state = AgentState.ERROR
            elif health['issues']:
                agent.state = AgentState.BUSY
            else:
                agent.state = AgentState.RUNNING
                
        except Exception as e:
            logger.error(f"Health check failed for {agent_id}: {e}")
            health['healthy'] = False
            health['issues'].append(f'Health check error: {str(e)}')
        
        return health
    
    def restart_agent(self, agent_id: str):
        """Restart a failed agent with exponential backoff"""
        if agent_id not in self.agents:
            logger.error(f"Agent {agent_id} not found")
            return
        
        agent = self.agents[agent_id]
        restart_attempt = agent.restart_count + 1
        
        # Check if we've exceeded max restarts
        if restart_attempt > self.max_retries:
            logger.error(f"Agent {agent_id} exceeded max restart attempts ({self.max_retries})")
            agent.state = AgentState.ERROR
            return
        
        # Calculate exponential backoff delay
        delay = min(
            self.base_retry_delay * (self.retry_multiplier ** (restart_attempt - 1)),
            self.max_retry_delay
        )
        
        # Add jitter to prevent thundering herd
        jitter = random.uniform(0.1, 0.3) * delay
        total_delay = delay + jitter
        
        logger.info(f"Restarting agent {agent_id} (attempt {restart_attempt}/{self.max_retries}) after {total_delay:.1f}s")
        
        # Stop the agent
        self.stop_agent_gracefully(agent)
        time.sleep(2)
        
        # Wait with exponential backoff
        time.sleep(total_delay)
        
        # Remove from tracking
        del self.agents[agent_id]
        
        # Relaunch
        new_agent_id = self.launch_agent(agent.role, restart_attempt)
        
        if new_agent_id and new_agent_id in self.agents:
            # Update restart count
            self.agents[new_agent_id].restart_count = restart_attempt
            logger.info(f"Agent {agent_id} restarted as {new_agent_id}")
        else:
            logger.error(f"Failed to restart agent {agent_id}")
    
    def monitoring_loop(self):
        """Background monitoring thread with error recovery"""
        logger.info("Starting health monitoring loop")
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while not self.stop_event.is_set():
            try:
                # Check each agent
                for agent_id, agent in list(self.agents.items()):
                    if agent.state == AgentState.STOPPED:
                        continue
                    
                    try:
                        health = self.monitor_agent_health(agent_id, agent)
                        
                        # Handle unhealthy agents with recovery strategies
                        if not health['healthy']:
                            logger.warning(f"Agent {agent_id} unhealthy: {health['issues']}")
                            
                            # Implement graduated recovery responses
                            if agent.error_count <= 2:
                                # Light recovery: just log and continue
                                logger.info(f"Agent {agent_id} experiencing minor issues, monitoring...")
                            elif agent.error_count <= 5:
                                # Medium recovery: try to refresh the agent
                                logger.info(f"Agent {agent_id} needs attention, attempting refresh...")
                                self.refresh_agent(agent_id)
                            elif agent.restart_count < self.max_retries:
                                # Heavy recovery: restart the agent
                                logger.warning(f"Agent {agent_id} critical, restarting...")
                                self.restart_agent(agent_id)
                            else:
                                # Final recovery: mark as permanently failed
                                logger.error(f"Agent {agent_id} failed permanently, marking as error")
                                agent.state = AgentState.ERROR
                        
                        # Log metrics periodically
                        if health['metrics']:
                            logger.debug(f"Agent {agent_id} metrics: {health['metrics']}")
                            
                    except Exception as agent_error:
                        logger.error(f"Error monitoring agent {agent_id}: {agent_error}")
                        agent.error_count += 1
                
                # Save state periodically
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    try:
                        self.save_system_state()
                    except Exception as e:
                        logger.error(f"Failed to save system state: {e}")
                
                # Check system resources
                try:
                    self.check_system_health()
                except Exception as e:
                    logger.error(f"System health check failed: {e}")
                
                # Reset consecutive error counter on successful iteration
                consecutive_errors = 0
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Monitoring error ({consecutive_errors}/{max_consecutive_errors}): {e}", exc_info=True)
                
                # Emergency stop if too many consecutive errors
                if consecutive_errors >= max_consecutive_errors:
                    logger.critical("Too many consecutive monitoring errors, initiating emergency shutdown")
                    self.emergency_shutdown()
                    break
            
            # Wait before next check
            self.stop_event.wait(self.health_check_interval)
        
        logger.info("Monitoring loop stopped")
    
    def refresh_agent(self, agent_id: str):
        """Attempt to refresh an agent without full restart"""
        if agent_id not in self.agents:
            logger.warning(f"Cannot refresh non-existent agent {agent_id}")
            return
            
        agent = self.agents[agent_id]
        logger.info(f"Refreshing agent {agent_id}")
        
        try:
            # Send a gentle refresh command
            self.send_to_agent(agent.window, "/help")
            time.sleep(1)
            
            # Update last activity
            agent.last_activity = datetime.now().isoformat()
            
            # Reset error count if refresh succeeds
            if agent.error_count > 0:
                agent.error_count = max(0, agent.error_count - 1)
                
        except Exception as e:
            logger.error(f"Failed to refresh agent {agent_id}: {e}")
            agent.error_count += 1
    
    def emergency_memory_recovery(self):
        """Emergency actions when system memory is critical"""
        logger.critical("Initiating emergency memory recovery")
        
        # Stop non-essential agents
        stopped_agents = []
        for agent_id, agent in list(self.agents.items()):
            if agent.memory_usage > 500:  # Stop high-memory agents
                logger.warning(f"Stopping high-memory agent {agent_id} ({agent.memory_usage:.1f}MB)")
                self.stop_agent_gracefully(agent)
                stopped_agents.append(agent_id)
                
        if stopped_agents:
            logger.info(f"Stopped {len(stopped_agents)} agents for memory recovery")
    
    def throttle_agents(self):
        """Reduce agent activity to conserve resources"""
        logger.info("Throttling agent activity due to high resource usage")
        
        # Increase health check interval temporarily
        original_interval = self.health_check_interval
        self.health_check_interval = min(original_interval * 2, 120)
        
        # Log the change
        logger.info(f"Health check interval increased from {original_interval}s to {self.health_check_interval}s")
    
    def reduce_agent_activity(self):
        """Reduce agent activity during high CPU usage"""
        logger.info("Reducing agent activity due to high CPU usage")
        
        # Could send pause commands to agents here
        for agent_id, agent in self.agents.items():
            if agent.state == AgentState.RUNNING:
                try:
                    # Send a command to reduce activity
                    self.send_to_agent(agent.window, "# Reducing activity due to high CPU")
                except Exception as e:
                    logger.error(f"Failed to reduce activity for {agent_id}: {e}")
    
    def emergency_shutdown(self):
        """Emergency shutdown procedure"""
        logger.critical("Initiating emergency shutdown due to critical errors")
        
        # Set stop event
        self.stop_event.set()
        
        # Force save current state
        try:
            self.save_system_state()
        except Exception as e:
            logger.error(f"Failed to save state during emergency shutdown: {e}")
        
        # Stop all agents immediately
        for agent_id in list(self.agents.keys()):
            try:
                agent = self.agents[agent_id]
                agent.state = AgentState.ERROR
                logger.warning(f"Emergency stop for agent {agent_id}")
            except Exception as e:
                logger.error(f"Error during emergency stop of {agent_id}: {e}")
    
    def check_system_health(self):
        """Check overall system health with recovery actions"""
        try:
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            
            if memory.percent > 95:
                logger.critical(f"System memory critical: {memory.percent}% - Triggering emergency actions")
                self.emergency_memory_recovery()
            elif memory.percent > 90:
                logger.warning(f"System memory high: {memory.percent}% - Throttling agents")
                self.throttle_agents()
            
            if cpu > 95:
                logger.critical(f"System CPU critical: {cpu}% - Reducing agent activity")
                self.reduce_agent_activity()
            elif cpu > 90:
                logger.warning(f"System CPU high: {cpu}%")
                
        except Exception as e:
            logger.error(f"System health check failed: {e}", exc_info=True)
    
    def show_dashboard(self):
        """Display system status dashboard"""
        print("\n" + "="*60)
        print("🤖 AUTONOMOUS MULTI-AGENT SYSTEM DASHBOARD")
        print("="*60)
        
        # System info
        print(f"\n📊 System Status:")
        print(f"   Uptime: {self.get_system_uptime()}")
        print(f"   Total Agents: {len(self.agents)}")
        print(f"   Active: {sum(1 for a in self.agents.values() if a.state == AgentState.RUNNING)}")
        print(f"   Errors: {sum(1 for a in self.agents.values() if a.state == AgentState.ERROR)}")
        
        # Agent details
        print(f"\n👥 Agent Status:")
        for agent_id, agent in self.agents.items():
            status_icon = "🟢" if agent.state == AgentState.RUNNING else "🔴"
            print(f"   {status_icon} {agent_id}")
            print(f"      State: {agent.state.value}")
            print(f"      Memory: {agent.memory_usage:.1f}MB")
            print(f"      CPU: {agent.cpu_usage:.1f}%")
            print(f"      Errors: {agent.error_count}")
        
        # Instructions
        print(f"\n📚 Commands:")
        print(f"   View agents: tmux attach -t {self.session_name}")
        print(f"   Switch agents: Ctrl+B, then window number")
        print(f"   Stop system: Ctrl+C or ./stop.sh")
        print(f"   View logs: tail -f autonomous-system.log")
        print("="*60 + "\n")
    
    def run(self):
        """Main execution flow with comprehensive error handling"""
        print("🚀 Enhanced Autonomous Multi-Agent System v2")
        print("="*50)
        
        try:
            # Check dependencies
            if not self.check_dependencies():
                logger.error("Missing dependencies. Please install them and try again.")
                sys.exit(1)
            
            # Setup tmux
            if not self.setup_tmux_session():
                logger.error("Failed to setup tmux session")
                sys.exit(1)
            
            # Start monitoring thread
            try:
                self.monitoring_thread = threading.Thread(target=self.monitoring_loop)
                self.monitoring_thread.daemon = True  # Ensure thread dies with main process
                self.monitoring_thread.start()
                logger.info("Monitoring thread started")
            except Exception as e:
                logger.error(f"Failed to start monitoring thread: {e}")
                sys.exit(1)
            
            # Launch agents
            try:
                self.launch_all_agents()
            except Exception as e:
                logger.error(f"Failed to launch agents: {e}")
                # Continue anyway with partial system
            
            # Show dashboard
            try:
                self.show_dashboard()
            except Exception as e:
                logger.error(f"Failed to show dashboard: {e}")
            
            # Main loop
            logger.info("System running. Press Ctrl+C to stop.")
            
            try:
                while not self.stop_event.is_set():
                    try:
                        # Refresh dashboard periodically
                        time.sleep(30)
                        if not self.stop_event.is_set():
                            os.system('clear' if os.name == 'posix' else 'cls')
                            self.show_dashboard()
                    except Exception as e:
                        logger.error(f"Error in main loop: {e}")
                        time.sleep(5)  # Brief pause before retry
                        
            except KeyboardInterrupt:
                logger.info("Interrupted by user")
            
        except Exception as e:
            logger.critical(f"Critical system error: {e}", exc_info=True)
        finally:
            # Cleanup
            try:
                self.cleanup()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}", exc_info=True)

def main():
    """Entry point with error handling"""
    try:
        launcher = EnhancedAutonomousLauncher()
        launcher.run()
    except Exception as e:
        logger.critical(f"System failed to start: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()