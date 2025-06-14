#!/bin/bash
# Autonomous Multi-Agent System Starter

set -e

echo "🚀 Starting Autonomous Multi-Agent System"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check command existence
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 is not installed${NC}"
        return 1
    else
        echo -e "${GREEN}✅ $1 is installed${NC}"
        return 0
    fi
}

# Function to check Python package
check_python_package() {
    if python3 -c "import $1" &> /dev/null; then
        echo -e "${GREEN}✅ Python package '$1' is installed${NC}"
        return 0
    else
        echo -e "${RED}❌ Python package '$1' is not installed${NC}"
        return 1
    fi
}

echo "🔍 Checking dependencies..."
echo ""

# Check required commands
MISSING_DEPS=0

if ! check_command "tmux"; then
    echo "   Install with: sudo apt-get install tmux (or your package manager)"
    MISSING_DEPS=1
fi

if ! check_command "claude"; then
    echo "   Install with: npm install -g @anthropic-ai/claude-code"
    MISSING_DEPS=1
fi

if ! check_command "python3"; then
    echo "   Install Python 3.8 or higher"
    MISSING_DEPS=1
fi

if ! check_command "git"; then
    echo "   Install git"
    MISSING_DEPS=1
fi

# Check Python packages
echo ""
echo "🐍 Checking Python packages..."

if ! check_python_package "mcp"; then
    echo "   Install with: pip install mcp"
    MISSING_DEPS=1
fi

# Check for required files
echo ""
echo "📁 Checking required files..."

if [ ! -f "mcp-coordinator/server.py" ]; then
    echo -e "${RED}❌ MCP coordinator server not found${NC}"
    MISSING_DEPS=1
else
    echo -e "${GREEN}✅ MCP coordinator server found${NC}"
fi

if [ ! -f ".claude/config.json" ]; then
    echo -e "${RED}❌ Configuration file not found${NC}"
    MISSING_DEPS=1
else
    echo -e "${GREEN}✅ Configuration file found${NC}"
fi

if [ ! -f "claude_mcp_settings.json" ]; then
    echo -e "${RED}❌ MCP settings file not found${NC}"
    MISSING_DEPS=1
else
    echo -e "${GREEN}✅ MCP settings file found${NC}"
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Warning: Not in a git repository. Some features may not work.${NC}"
    echo -e "${YELLOW}   Initialize with: git init${NC}"
fi

# Exit if dependencies are missing
if [ $MISSING_DEPS -eq 1 ]; then
    echo ""
    echo -e "${RED}❌ Missing dependencies. Please install them and try again.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ All dependencies satisfied!${NC}"
echo ""

# Check if system is already running
if tmux has-session -t autonomous-claude 2>/dev/null; then
    echo -e "${YELLOW}⚠️  System appears to be already running${NC}"
    echo ""
    read -p "Stop existing system and restart? (y/N) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Stopping existing system..."
        ./stop.sh
        sleep 2
    else
        echo "Attaching to existing session..."
        tmux attach -t autonomous-claude
        exit 0
    fi
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p mcp-coordinator agent-workspaces .claude/agents

# Launch the autonomous system
echo ""
echo "🚀 Launching autonomous system..."
echo ""

# Set MCP settings path
export CLAUDE_MCP_SETTINGS_PATH="$(pwd)/claude_mcp_settings.json"

# Run the launcher
python3 autonomous-system.py