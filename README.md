# Autonomous Multi-Agent System with MCP

This system enables multiple Claude Code instances to work together autonomously 24/7 to audit, plan, code, test, and review your codebase using the Model Context Protocol (MCP).

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
npm install -g @anthropic-ai/claude-code

# Test the system
./test-system.py

# Start the autonomous agents
./start.sh
```

## 📋 Prerequisites

- Python 3.8+
- Node.js and npm
- tmux
- git
- Claude Code CLI (`npm install -g @anthropic-ai/claude-code`)

## 🏗️ Architecture

The system consists of:

1. **MCP Coordinator Server** - Central hub for agent coordination
2. **Agent Roles**:
   - **Auditor** - Continuously scans for issues
   - **Planner** - Creates implementation plans
   - **Coder** - Implements solutions
   - **Tester** - Writes and runs tests
   - **Reviewer** - Reviews and approves changes

## 📁 Project Structure

```
.
├── mcp-coordinator/          # MCP server and data
│   └── server.py            # Coordinator server
├── .claude/                 # Configuration
│   ├── config.json         # System configuration
│   └── agents/             # Agent instructions
│       ├── auditor.md
│       ├── planner.md
│       ├── coder.md
│       ├── tester.md
│       └── reviewer.md
├── agent-workspaces/        # Git worktrees for agents
├── autonomous-system.py     # Main launcher
├── claude_mcp_settings.json # MCP configuration
├── start.sh                # Start script
├── stop.sh                 # Stop script
├── status.sh               # Status checker
└── PROJECT_GOALS.md        # Project objectives
```

## 🔧 Configuration

Edit `.claude/config.json` to customize:
- Agent roles and capabilities
- Automation rules
- Quality standards
- Git settings

## 🎮 Usage

### Start the System
```bash
./start.sh
```

### Monitor Agents
```bash
# Check status
./status.sh

# View agents in tmux
tmux attach -t autonomous-claude

# Switch between agents
# Ctrl+B, then window number (0-9)
```

### Stop the System
```bash
./stop.sh
# or press Ctrl+C in the monitor
```

## 🤖 How It Works

1. **Auditor** continuously scans the codebase for issues
2. **Planner** creates implementation plans from findings
3. **Coder** implements solutions in isolated git worktrees
4. **Tester** writes tests for the changes
5. **Reviewer** reviews and creates pull requests

All agents communicate through the MCP coordinator, ensuring no conflicts and efficient task distribution.

## 🛠️ Customization

### Add New Agent Type
1. Create instructions: `.claude/agents/newrole.md`
2. Add to config: `.claude/config.json`
3. Update launcher if needed

### Modify Audit Rules
Edit `.claude/agents/auditor.md` to change what the auditor looks for.

### Change Automation Settings
Update `.claude/config.json` to modify:
- Audit frequency
- Auto-PR creation
- Test requirements
- Working hours

## 🐛 Troubleshooting

### Agents Not Starting
- Check dependencies: `./test-system.py`
- Verify Claude Code is installed: `claude --version`
- Check tmux session: `tmux ls`

### MCP Connection Issues
- Verify MCP settings: `cat claude_mcp_settings.json`
- Check server logs: `tail -f mcp-coordinator/state.json`

### Git Worktree Errors
- Ensure you're in a git repository: `git status`
- Clean up worktrees: `git worktree prune`

## 📊 Monitoring

The system provides several monitoring options:
- `./status.sh` - Quick status overview
- `tmux attach` - Live agent views
- `mcp-coordinator/state.json` - Detailed state

## 🔒 Security

- Agents work in isolated git worktrees
- No credentials are stored in code
- All changes go through review

## 🤝 Contributing

To improve the autonomous system:
1. Test changes with `./test-system.py`
2. Update relevant agent instructions
3. Document in this README

## 📜 License

This autonomous system is provided as-is for use with Claude Code.