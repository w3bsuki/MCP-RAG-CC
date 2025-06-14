#!/bin/bash

echo "🔧 Windows to WSL Clipboard Helper"
echo ""
echo "METHOD 1 - Use clip.exe:"
echo "1. Copy auth code in browser (Ctrl+C)"
echo "2. In WSL terminal, run: powershell.exe Get-Clipboard"
echo "3. Copy that output manually"
echo ""
echo "METHOD 2 - Use file transfer:"
echo "1. Copy auth code in browser" 
echo "2. Open notepad, paste it"
echo "3. Save as /mnt/c/temp/authcode.txt"
echo "4. In terminal: cat /mnt/c/temp/authcode.txt"
echo ""
echo "METHOD 3 - Direct paste in terminal:"
echo "1. Right-click in XTerm window"
echo "2. Look for 'Paste' option"
echo "3. Or try Ctrl+V directly in the auth prompt"
echo ""

# Create temp directory on Windows side
mkdir -p /mnt/c/temp

echo "✅ Helper ready! Windows temp dir: C:\\temp"