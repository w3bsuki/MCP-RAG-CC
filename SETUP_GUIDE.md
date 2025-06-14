# MCP + RAG + CC System Setup Guide

## Overview
This is an autonomous multi-agent system using MCP (Model Context Protocol) for coordination, with RAG capabilities and Claude Code integration.

## Prerequisites

### System Requirements
- Python 3.8+
- Node.js 16+
- Git
- Docker (optional, for isolated environments)

### Required Tools
- Claude Code CLI
- MCP SDK
- Git with GitHub CLI (`gh`)

## Installation Steps

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd MCP+RAG+CC
```

### 2. Python Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Node.js Dependencies
```bash
# Install Node packages
npm install
```

### 4. MCP Coordinator Setup
```bash
# Install MCP tools
pip install mcp-sdk
npm install @modelcontextprotocol/sdk

# Set up MCP coordinator
python scripts/setup_coordinator.py
```

### 5. Configure Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your values:
# - ANTHROPIC_API_KEY=your-api-key
# - MCP_COORDINATOR_PORT=8080
# - GITHUB_TOKEN=your-github-token
# - Other service credentials
```

## System Architecture

### Core Components

1. **MCP Coordinator** - Central task management
2. **Agent Pool** - Multiple specialized agents:
   - Auditor: Code quality scanning
   - Planner: Task breakdown
   - Coder: Implementation
   - Tester: Test creation
   - Reviewer: PR management

3. **RAG System** - Knowledge retrieval
4. **Claude Code Integration** - AI-powered coding

## Configuration

### 1. Agent Configuration
```yaml
# config/agents.yaml
agents:
  auditor:
    id: auditor-001
    capabilities:
      - code_analysis
      - security_scanning
      - performance_profiling
    
  planner:
    id: planner-001
    capabilities:
      - task_breakdown
      - dependency_analysis
      - priority_assignment
```

### 2. MCP Configuration
```json
// config/mcp-config.json
{
  "coordinator": {
    "host": "localhost",
    "port": 8080,
    "persistence": {
      "type": "sqlite",
      "path": "./data/coordinator.db"
    }
  },
  "agents": {
    "max_concurrent": 5,
    "heartbeat_interval": 30,
    "task_timeout": 3600
  }
}
```

### 3. RAG Configuration
```yaml
# config/rag-config.yaml
vector_store:
  type: chromadb
  path: ./data/embeddings
  
embeddings:
  model: text-embedding-ada-002
  chunk_size: 1000
  overlap: 200
```

## Running the System

### 1. Start MCP Coordinator
```bash
# In terminal 1
python -m mcp_coordinator.server --config config/mcp-config.json
```

### 2. Start Agent Pool
```bash
# In terminal 2
python -m agents.manager start --all
```

### 3. Initialize RAG System
```bash
# Index your codebase
python scripts/index_codebase.py --path . --config config/rag-config.yaml
```

### 4. Start Claude Code Integration
```bash
# In terminal 3
claude-code serve --mcp --port 3000
```

## Testing the System

### 1. Basic Health Check
```bash
# Check coordinator health
curl http://localhost:8080/health

# Check agent status
python scripts/check_agents.py
```

### 2. Submit Test Task
```bash
# Submit an audit task
python scripts/submit_task.py --type audit --target src/

# Monitor task progress
python scripts/monitor_tasks.py --watch
```

### 3. Run Integration Tests
```bash
# Run all tests
pytest tests/

# Run specific test suite
pytest tests/integration/test_mcp_flow.py -v
```

## Common Commands

### Task Management
```bash
# List all tasks
python -m mcp_coordinator.cli list-tasks

# Get task details
python -m mcp_coordinator.cli get-task <task-id>

# Cancel task
python -m mcp_coordinator.cli cancel-task <task-id>
```

### Agent Management
```bash
# List agents
python -m agents.cli list

# Restart agent
python -m agents.cli restart <agent-id>

# View agent logs
python -m agents.cli logs <agent-id>
```

### System Monitoring
```bash
# View system metrics
python scripts/metrics.py

# Export metrics
python scripts/metrics.py --export metrics.json
```

## Troubleshooting

### Common Issues

1. **Coordinator Connection Failed**
   ```bash
   # Check if coordinator is running
   ps aux | grep mcp_coordinator
   
   # Check logs
   tail -f logs/coordinator.log
   ```

2. **Agent Registration Failed**
   ```bash
   # Verify agent config
   python scripts/validate_config.py
   
   # Check network connectivity
   nc -zv localhost 8080
   ```

3. **RAG Indexing Issues**
   ```bash
   # Clear index and rebuild
   rm -rf data/embeddings/*
   python scripts/index_codebase.py --rebuild
   ```

## Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature
```

### 2. Make Changes
```bash
# Edit files
# Run linting
ruff check .
npm run lint

# Run tests
pytest
npm test
```

### 3. Submit for Review
```bash
# Commit changes
git add .
git commit -m "feat: Add new feature"

# Push and create PR
git push -u origin feature/your-feature
gh pr create
```

## Advanced Configuration

### Custom Agent Development
```python
# agents/custom_agent.py
from mcp_sdk import Agent

class CustomAgent(Agent):
    def __init__(self):
        super().__init__(
            agent_id="custom-001",
            role="custom",
            capabilities=["custom_analysis"]
        )
    
    async def process_task(self, task):
        # Your implementation
        pass
```

### RAG Pipeline Customization
```python
# rag/custom_pipeline.py
from rag_framework import Pipeline

class CustomRAGPipeline(Pipeline):
    def preprocess(self, text):
        # Custom preprocessing
        return processed_text
    
    def embed(self, chunks):
        # Custom embedding logic
        return embeddings
```

## Monitoring and Logs

### Log Locations
- Coordinator: `logs/coordinator.log`
- Agents: `logs/agents/<agent-id>.log`
- RAG: `logs/rag.log`
- System: `logs/system.log`

### Metrics Dashboard
```bash
# Start metrics server
python scripts/metrics_server.py

# Access dashboard at http://localhost:9090
```

## Security Considerations

1. **API Keys**: Store in `.env`, never commit
2. **GitHub Token**: Use fine-grained permissions
3. **Network**: Run coordinator on localhost only
4. **Data**: Encrypt sensitive data at rest

## Performance Tuning

### Agent Pool
```yaml
# Adjust in config/agents.yaml
performance:
  max_workers: 10
  queue_size: 1000
  batch_size: 50
```

### RAG System
```yaml
# Adjust in config/rag-config.yaml
performance:
  cache_size: 1000
  parallel_queries: 5
  timeout: 30
```

## Backup and Recovery

### Backup
```bash
# Backup all data
./scripts/backup.sh

# Backup specific component
./scripts/backup.sh --component coordinator
```

### Restore
```bash
# Restore from backup
./scripts/restore.sh --backup backup-2024-01-14.tar.gz
```

## Support and Documentation

- Documentation: `docs/`
- Issues: GitHub Issues
- Logs: Check `logs/` directory
- Community: Discord/Slack channel

## Quick Test Commands

```bash
# Test the entire setup
./scripts/test_setup.sh

# This will:
# 1. Check all services are running
# 2. Submit a test task
# 3. Monitor completion
# 4. Verify outputs
```

Remember to check the CLAUDE.md file for agent-specific instructions and quality standards!