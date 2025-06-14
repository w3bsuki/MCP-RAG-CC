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
            logger.error(f"Invalid JSON in config file: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
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
                logger.error(f"Error stopping agent {agent_id}: {e}")
        
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
                    check=True
                )
                version = result.stdout.strip()
                
                # Version checking could be enhanced here
                logger.info(f"✅ {dep_name} installed: {version}")
                
            except subprocess.CalledProcessError:
                logger.error(f"❌ {dep_name} not found. Install with: {dep_info['install']}")
                all_ok = False
            except Exception as e:
                logger.error(f"❌ Error checking {dep_name}: {e}")
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
            except ImportError:
                logger.error(f"❌ {package} not found. Install with: pip install {package}>={min_version}")
                all_ok = False
        
        # Check system resources
        if not self.check_system_resources():
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
                capture_output=True
            )
            
            if result.returncode == 0:
                logger.warning("Existing session found, killing it...")
                subprocess.run(['tmux', 'kill-session', '-t', self.session_name])
                time.sleep(1)
            
            # Create new session with specific settings
            subprocess.run([
                'tmux', 'new-session', '-d', '-s', self.session_name,
                '-x', '120', '-y', '40'  # Set initial size
            ], check=True)
            
            # Set tmux options for better agent handling
            tmux_options = [
                ('set-option', '-g', 'history-limit', '10000'),
                ('set-option', '-g', 'mouse', 'on'),
                ('set-window-option', '-g', 'monitor-activity', 'on')
            ]
            
            for option in tmux_options:
                subprocess.run(['tmux'] + list(option) + ['-t', self.session_name])
            
            logger.info("✅ Tmux session created successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create tmux session: {e}")
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
        """Send command with retry logic"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # Clear any existing input
                subprocess.run([
                    'tmux', 'send-keys', '-t', f'{self.session_name}:{window}',
                    'C-c'  # Cancel any ongoing input
                ], capture_output=True)
                
                time.sleep(0.5)
                
                # Send the command
                subprocess.run([
                    'tmux', 'send-keys', '-t', f'{self.session_name}:{window}',
                    command, 'Enter'
                ], check=True)
                
                return
                
            except subprocess.CalledProcessError as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Retry {attempt + 1} sending to {window}: {e}")
                    time.sleep(1)
                else:
                    logger.error(f"Failed to send command to {window}: {e}")
                    raise
    
    def launch_agent(self, role: str, index: int = 0) -> Optional[str]:
        """Enhanced agent launch with health checks"""
        agent_id = f"{role}-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{index}"
        
        logger.info(f"Launching agent: {agent_id}")
        
        # Create window
        window = self.create_agent_window(role, index)
        if not window:
            return None
        
        # Create agent info
        agent = AgentInfo(
            id=agent_id,
            role=role,
            window=window,
            started_at=datetime.now().isoformat(),
            state=AgentState.STARTING
        )
        
        try:
            # Set up environment
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
            launch_command = f'claude "{init_prompt}"'
            self.send_to_agent(window, launch_command)
            
            # Wait for Claude to start
            time.sleep(3)
            
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
            
            # Get process ID
            time.sleep(2)
            agent.pid = self.get_agent_pid(window)
            
            # Update state
            agent.state = AgentState.RUNNING
            agent.last_activity = datetime.now().isoformat()
            
            # Store agent
            self.agents[agent_id] = agent
            
            logger.info(f"✅ Agent {agent_id} launched successfully (PID: {agent.pid})")
            return agent_id
            
        except Exception as e:
            logger.error(f"Failed to launch agent {agent_id}: {e}")
            agent.state = AgentState.ERROR
            agent.error_count += 1
            self.agents[agent_id] = agent
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
            logger.error(f"Error stopping agent {agent.id}: {e}")
    
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
        """Restart a failed agent"""
        if agent_id not in self.agents:
            logger.error(f"Agent {agent_id} not found")
            return
        
        agent = self.agents[agent_id]
        logger.info(f"Restarting agent {agent_id} (attempt {agent.restart_count + 1})")
        
        # Stop the agent
        self.stop_agent_gracefully(agent)
        time.sleep(2)
        
        # Remove from tracking
        del self.agents[agent_id]
        
        # Relaunch
        new_agent_id = self.launch_agent(agent.role, agent.restart_count)
        
        if new_agent_id and new_agent_id in self.agents:
            # Update restart count
            self.agents[new_agent_id].restart_count = agent.restart_count + 1
    
    def monitoring_loop(self):
        """Background monitoring thread"""
        logger.info("Starting health monitoring loop")
        
        while not self.stop_event.is_set():
            try:
                # Check each agent
                for agent_id, agent in list(self.agents.items()):
                    if agent.state == AgentState.STOPPED:
                        continue
                    
                    health = self.monitor_agent_health(agent_id, agent)
                    
                    # Handle unhealthy agents
                    if not health['healthy']:
                        logger.warning(f"Agent {agent_id} unhealthy: {health['issues']}")
                        
                        # Restart if too many errors
                        if agent.error_count > 5 and agent.restart_count < 3:
                            self.restart_agent(agent_id)
                    
                    # Log metrics periodically
                    if health['metrics']:
                        logger.debug(f"Agent {agent_id} metrics: {health['metrics']}")
                
                # Save state periodically
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    self.save_system_state()
                
                # Check system resources
                self.check_system_health()
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
            
            # Wait before next check
            self.stop_event.wait(self.health_check_interval)
        
        logger.info("Monitoring loop stopped")
    
    def check_system_health(self):
        """Check overall system health"""
        try:
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            
            if memory.percent > 90:
                logger.warning(f"System memory critical: {memory.percent}%")
                # Could trigger agent throttling here
            
            if cpu > 90:
                logger.warning(f"System CPU critical: {cpu}%")
                
        except Exception as e:
            logger.error(f"System health check failed: {e}")
    
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
        """Main execution flow"""
        print("🚀 Enhanced Autonomous Multi-Agent System v2")
        print("="*50)
        
        # Check dependencies
        if not self.check_dependencies():
            logger.error("Missing dependencies. Please install them and try again.")
            sys.exit(1)
        
        # Setup tmux
        if not self.setup_tmux_session():
            logger.error("Failed to setup tmux session")
            sys.exit(1)
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop)
        self.monitoring_thread.start()
        
        # Launch agents
        self.launch_all_agents()
        
        # Show dashboard
        self.show_dashboard()
        
        # Main loop
        logger.info("System running. Press Ctrl+C to stop.")
        
        try:
            while not self.stop_event.is_set():
                # Refresh dashboard periodically
                time.sleep(30)
                os.system('clear' if os.name == 'posix' else 'cls')
                self.show_dashboard()
                
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        
        # Cleanup
        self.cleanup()

def main():
    """Entry point"""
    launcher = EnhancedAutonomousLauncher()
    launcher.run()

if __name__ == "__main__":
    main()