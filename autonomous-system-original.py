#!/usr/bin/env python3
"""
Autonomous Multi-Agent System Launcher
Manages Claude Code agents in tmux sessions with MCP coordination
"""

import subprocess
import time
import os
import json
import sys
from datetime import datetime
from pathlib import Path
import signal
import atexit

class AutonomousSystemLauncher:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.config_file = self.base_dir / ".claude" / "config.json"
        self.mcp_settings = self.base_dir / "claude_mcp_settings.json"
        self.session_name = "autonomous-claude"
        self.agents = []
        
        # Load configuration
        self.load_config()
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def load_config(self):
        """Load project configuration"""
        if not self.config_file.exists():
            print("❌ Configuration file not found at .claude/config.json")
            sys.exit(1)
        
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutting down autonomous system...")
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Clean up resources on exit"""
        # Save agent states
        self.save_agent_states()
        
        # Notify agents to gracefully shutdown
        for agent in self.agents:
            try:
                self.send_to_agent(agent['window'], "/exit")
            except:
                pass
    
    def save_agent_states(self):
        """Save current agent states"""
        state = {
            'shutdown_time': datetime.now().isoformat(),
            'agents': self.agents
        }
        state_file = self.base_dir / "mcp-coordinator" / "launcher-state.json"
        state_file.parent.mkdir(exist_ok=True)
        
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def check_dependencies(self):
        """Check required dependencies"""
        print("🔍 Checking dependencies...")
        
        # Check tmux
        try:
            subprocess.run(['tmux', '-V'], capture_output=True, check=True)
            print("✅ tmux installed")
        except:
            print("❌ tmux not found. Please install tmux.")
            return False
        
        # Check Claude Code
        try:
            subprocess.run(['claude', '--version'], capture_output=True, check=True)
            print("✅ Claude Code installed")
        except:
            print("❌ Claude Code not found. Install with: npm install -g @anthropic-ai/claude-code")
            return False
        
        # Check Python packages
        required_packages = ['mcp']
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package} installed")
            except ImportError:
                print(f"❌ {package} not found. Install with: pip install {package}")
                return False
        
        # Check MCP server
        if not (self.base_dir / "mcp-coordinator" / "server.py").exists():
            print("❌ MCP coordinator server not found")
            return False
        
        print("✅ MCP coordinator server found")
        
        # Check git repository
        try:
            subprocess.run(['git', 'status'], capture_output=True, check=True, cwd=self.base_dir)
            print("✅ Git repository detected")
        except:
            print("⚠️  No git repository found. Some features may not work.")
        
        return True
    
    def setup_tmux_session(self):
        """Create tmux session for agents"""
        print(f"🖥️  Setting up tmux session: {self.session_name}")
        
        # Kill existing session if exists
        subprocess.run(['tmux', 'kill-session', '-t', self.session_name], 
                      capture_output=True)
        
        # Create new session
        subprocess.run(['tmux', 'new-session', '-d', '-s', self.session_name], 
                      check=True)
        
        print("✅ Tmux session created")
    
    def launch_mcp_coordinator(self):
        """Launch MCP coordinator in background"""
        print("🚀 Starting MCP coordinator...")
        
        # MCP coordinator runs via stdio, so agents will connect to it
        # No separate window needed as it's accessed via MCP protocol
        
        print("✅ MCP coordinator configured")
    
    def create_agent_window(self, role: str, index: int = 0):
        """Create tmux window for an agent"""
        window_name = f"{role}-{index}" if index > 0 else role
        
        # Create new window
        subprocess.run([
            'tmux', 'new-window', '-t', f'{self.session_name}:', 
            '-n', window_name
        ], check=True)
        
        return window_name
    
    def send_to_agent(self, window: str, command: str):
        """Send command to agent window"""
        # Escape quotes in command
        escaped_command = command.replace('"', '\\"')
        
        subprocess.run([
            'tmux', 'send-keys', '-t', f'{self.session_name}:{window}',
            escaped_command, 'Enter'
        ], check=True)
    
    def launch_agent(self, role: str, index: int = 0):
        """Launch a single agent"""
        agent_id = f"{role}-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{index}"
        window = self.create_agent_window(role, index)
        
        print(f"🤖 Launching {role} agent: {agent_id}")
        
        # Set up environment
        self.send_to_agent(window, f"cd {self.base_dir}")
        time.sleep(0.5)
        
        # Export MCP settings path
        self.send_to_agent(window, f"export CLAUDE_MCP_SETTINGS_PATH={self.mcp_settings}")
        time.sleep(0.5)
        
        # Start Claude Code with initial instructions
        instructions_file = self.base_dir / ".claude" / "agents" / f"{role}.md"
        
        if instructions_file.exists():
            # Start Claude with instructions
            init_prompt = f"""I am agent {agent_id}. My role is {role}.

First, I'll read my instructions and initialize:

1. Read my role instructions from {instructions_file}
2. Register with the MCP coordinator
3. Start my autonomous work loop

Let me begin by reading my instructions."""
            
            # Start Claude Code
            self.send_to_agent(window, f'claude "{init_prompt}"')
            
            # Give agent time to start
            time.sleep(3)
            
            # Send follow-up to ensure agent reads instructions and starts
            follow_up = f"""Now I'll read my detailed instructions and start working:

/read {instructions_file}

After reading, I'll register with the coordinator and begin my autonomous loop."""
            
            self.send_to_agent(window, follow_up)
        else:
            print(f"⚠️  No instructions found for {role} at {instructions_file}")
        
        # Track agent
        self.agents.append({
            'id': agent_id,
            'role': role,
            'window': window,
            'started_at': datetime.now().isoformat()
        })
        
        return agent_id
    
    def launch_all_agents(self):
        """Launch all configured agents"""
        print("🚀 Launching all agents...")
        
        # Get role configurations
        roles = self.config.get('agents', {}).get('roles', {})
        
        # Launch agents with staggered start
        for role, role_config in roles.items():
            # Determine number of instances
            max_instances = role_config.get('max_instances', 1)
            
            for i in range(max_instances):
                self.launch_agent(role, i)
                
                # Stagger launches to avoid overwhelming the system
                time.sleep(5)
        
        print(f"✅ Launched {len(self.agents)} agents")
    
    def monitor_agents(self):
        """Monitor agent health and performance"""
        print("\n📊 Monitoring agents...")
        print("Press Ctrl+C to stop the system\n")
        
        monitoring_interval = 60  # Check every minute
        
        while True:
            try:
                # Check agent windows
                result = subprocess.run([
                    'tmux', 'list-windows', '-t', self.session_name
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    windows = result.stdout.strip().split('\n')
                    active_windows = len(windows)
                    
                    print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                          f"Active agents: {active_windows}/{len(self.agents)} | "
                          f"Session: {self.session_name}", end='', flush=True)
                
                # Check MCP coordinator state
                state_file = self.base_dir / "mcp-coordinator" / "state.json"
                if state_file.exists():
                    with open(state_file, 'r') as f:
                        state = json.load(f)
                        
                    pending_tasks = len([t for t in state.get('task_queue', []) 
                                       if t['status'] == 'pending'])
                    
                    print(f" | Pending tasks: {pending_tasks}", end='', flush=True)
                
                time.sleep(monitoring_interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\n⚠️  Monitoring error: {e}")
                time.sleep(monitoring_interval)
    
    def show_instructions(self):
        """Show usage instructions"""
        print("\n📚 Autonomous System Started!")
        print("=" * 50)
        print("ℹ️  The agents are now running autonomously.")
        print("\n🖥️  To view agents:")
        print(f"   tmux attach -t {self.session_name}")
        print("\n🔄 To switch between agents:")
        print("   Ctrl+B, then window number (0-9)")
        print("\n📊 To check status:")
        print("   ./status.sh")
        print("\n🛑 To stop all agents:")
        print("   ./stop.sh or Ctrl+C")
        print("=" * 50)
    
    def run(self):
        """Main execution flow"""
        print("🚀 Autonomous Multi-Agent System Launcher")
        print("=" * 50)
        
        # Check dependencies
        if not self.check_dependencies():
            print("\n❌ Missing dependencies. Please install them and try again.")
            sys.exit(1)
        
        # Setup tmux session
        self.setup_tmux_session()
        
        # Launch MCP coordinator
        self.launch_mcp_coordinator()
        
        # Launch all agents
        self.launch_all_agents()
        
        # Show instructions
        self.show_instructions()
        
        # Monitor agents
        self.monitor_agents()
        
        # Cleanup on exit
        print("\n👋 Shutting down autonomous system...")

def main():
    """Entry point"""
    launcher = AutonomousSystemLauncher()
    launcher.run()

if __name__ == "__main__":
    main()