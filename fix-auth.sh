#!/bin/bash

echo "🔧 FIXING AUTH COPY/PASTE ISSUE"
echo ""

# Create a paste command that works
cat > /usr/local/bin/paste-windows << 'EOF'
#!/bin/bash
# Get Windows clipboard content through WSL
powershell.exe -Command "Get-Clipboard" | tr -d '\r'
EOF

chmod +x /usr/local/bin/paste-windows

# Create an alias for easy use
echo 'alias getclip="powershell.exe -Command Get-Clipboard | tr -d '"'"'\\r'"'"'"' >> ~/.bashrc

echo "✅ FIXED! Now in any terminal you can:"
echo ""
echo "1. Copy auth code in browser (Ctrl+C)"
echo "2. In terminal type: getclip"
echo "3. Copy the output and paste it manually"
echo ""
echo "OR just type: paste-windows"
echo ""
echo "Restart your terminals and try it!"