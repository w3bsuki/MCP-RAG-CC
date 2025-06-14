#!/bin/bash

echo "🚀 Launching AI Agent Team with clipboard-friendly terminals..."
echo "Killing old agents..."
pkill -f "claude --dangerously-skip-permissions" 2>/dev/null

# Set environment
export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json

echo "Starting agents with proper clipboard support..."

# Install xclip if not available for proper clipboard
if ! command -v xclip &> /dev/null; then
    echo "Installing xclip for better clipboard support..."
    sudo apt-get update && sudo apt-get install -y xclip
fi

# Create a helper script for each agent that handles clipboard
cat > /tmp/agent_helper.sh << 'EOF'
#!/bin/bash
echo "========================================="
echo "🔍 AGENT: $1"
echo "========================================="
echo ""
echo "💡 CLIPBOARD TIPS:"
echo "1. Copy auth URL: Select text + Ctrl+Shift+C"
echo "2. Copy auth code from browser: Ctrl+C" 
echo "3. Paste auth code here: Ctrl+Shift+V"
echo "4. Or try right-click → paste"
echo ""
echo "Starting agent..."
echo ""

cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC
source venv/bin/activate
export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json

# Enable clipboard sharing
export DISPLAY=:0

claude --dangerously-skip-permissions "I am $1 agent - I need to register with the MCP coordinator first using: mcp-coordinator.register_agent()"

exec bash
EOF

chmod +x /tmp/agent_helper.sh

# Launch each agent with better clipboard support
xterm -title "AUDITOR" -e bash /tmp/agent_helper.sh "AUDITOR" &
sleep 2

xterm -title "PLANNER" -e bash /tmp/agent_helper.sh "PLANNER" &
sleep 2

xterm -title "CODER-1" -e bash /tmp/agent_helper.sh "CODER-1" &
sleep 2

xterm -title "CODER-2" -e bash /tmp/agent_helper.sh "CODER-2" &
sleep 2

xterm -title "TESTER" -e bash /tmp/agent_helper.sh "TESTER" &
sleep 2

xterm -title "REVIEWER" -e bash /tmp/agent_helper.sh "REVIEWER" &

echo "✅ All 6 AI agents launched with clipboard support!"
echo ""
echo "🎯 COPY/PASTE GUIDE:"
echo "1. Select auth URL → Ctrl+Shift+C"
echo "2. Paste in browser → Ctrl+V"
echo "3. Copy auth code from browser → Ctrl+C"
echo "4. Paste in terminal → Ctrl+Shift+V"
echo ""
echo "If Ctrl+Shift+V doesn't work, try:"
echo "- Right-click → Paste"
echo "- Shift+Insert"
echo "- Middle mouse button"