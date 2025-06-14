#!/bin/bash

echo "🚀 Launching agents with automatic auth handling..."
pkill -f "claude --dangerously-skip-permissions" 2>/dev/null

# Create an auto-auth script that shows URLs in files
cat > /tmp/auto_auth.sh << 'EOF'
#!/bin/bash
AGENT_NAME="$1"
cd /home/w3bsuki/svelte-threadly-1/MCP-RAG-CC
source venv/bin/activate
export CLAUDE_MCP_SETTINGS_PATH=/home/w3bsuki/svelte-threadly-1/MCP-RAG-CC/claude_mcp_settings.json

echo "========================================="
echo "🤖 $AGENT_NAME AGENT"
echo "========================================="
echo ""
echo "💡 SOLUTION: All auth URLs will be saved to files!"
echo "   Check /tmp/ directory for auth links"
echo ""

# Run Claude and capture ALL output including auth URLs
claude --dangerously-skip-permissions "I am $AGENT_NAME agent - I need to register with the MCP coordinator first using: mcp-coordinator.register_agent()" 2>&1 | tee "/tmp/${AGENT_NAME}_auth.txt"

echo ""
echo "✅ All output saved to: /tmp/${AGENT_NAME}_auth.txt"
echo "💡 Open this file to see auth URL and paste auth code!"

# Keep terminal open
exec bash
EOF

chmod +x /tmp/auto_auth.sh

# Launch each agent and save auth to files
for agent in AUDITOR PLANNER CODER-1 CODER-2 TESTER REVIEWER; do
    echo "Starting $agent..."
    xterm -title "$agent" -e bash /tmp/auto_auth.sh "$agent" &
    sleep 1
done

echo ""
echo "✅ All 6 agents launched!"
echo ""
echo "🎯 CLIPBOARD-FREE SOLUTION:"
echo ""
echo "1. Auth URLs are saved to files like:"
echo "   /tmp/AUDITOR_auth.txt"
echo "   /tmp/PLANNER_auth.txt" 
echo "   etc."
echo ""
echo "2. Open these files in notepad:"
echo "   notepad.exe /tmp/AUDITOR_auth.txt"
echo ""
echo "3. Copy URLs from notepad to browser"
echo "4. Copy auth codes from browser to notepad"  
echo "5. Type auth codes manually from notepad"
echo ""
echo "💡 Files update in real-time as agents run!"