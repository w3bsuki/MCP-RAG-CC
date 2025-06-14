#!/bin/bash

echo "🚀 Launching agents with Windows clipboard support..."
pkill -f "claude --dangerously-skip-permissions" 2>/dev/null

# Check if we can use Windows clipboard
if command -v clip.exe &> /dev/null; then
    echo "✅ Windows clipboard detected"
else
    echo "⚠️  Windows clipboard not available"
fi

# Create a script that shows the auth code in a way you can copy
cat > /tmp/auth_helper.sh << 'EOF'
#!/bin/bash
echo "========================================="
echo "🤖 AGENT: $1"
echo "========================================="
echo ""
echo "💡 WINDOWS CLIPBOARD SOLUTION:"
echo "1. When you see the auth code, it will be saved to a file"
echo "2. Open the file in notepad to copy/paste easily"
echo ""

cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC
source venv/bin/activate
export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json

# Run Claude and capture output to a file
echo "Starting Claude agent..."
claude --dangerously-skip-permissions "I am $1 agent - I need to register with the MCP coordinator first using: mcp-coordinator.register_agent()" | tee "/tmp/$1_output.txt"

echo ""
echo "✅ Output saved to: /tmp/$1_output.txt"
echo "💡 Open this file in notepad to copy the auth code!"

exec bash
EOF

chmod +x /tmp/auth_helper.sh

# Launch agents
for agent in AUDITOR PLANNER CODER-1 CODER-2 TESTER REVIEWER; do
    xterm -title "$agent" -e bash /tmp/auth_helper.sh "$agent" &
    sleep 1
done

echo "✅ All agents launched!"
echo ""
echo "🎯 WINDOWS COPY/PASTE SOLUTION:"
echo ""
echo "METHOD 1 - Use files:"
echo "1. Auth codes are saved to /tmp/AGENT_output.txt"
echo "2. Open with: notepad.exe /tmp/AUDITOR_output.txt"
echo "3. Copy from notepad with Ctrl+C"
echo ""
echo "METHOD 2 - Triple-click:"
echo "1. Triple-click the auth code line in XTerm"
echo "2. Right-click in XTerm → Copy"
echo "3. Paste in browser with Ctrl+V"
echo ""
echo "METHOD 3 - Mouse selection:"
echo "1. Click and drag to select auth code"
echo "2. Middle-click in browser to paste"