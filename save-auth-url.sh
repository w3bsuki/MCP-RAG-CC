#!/bin/bash

echo "Capture auth URL and save to file..."

# Monitor Claude output and save URLs automatically
tail -f /tmp/claude_output.log | grep -E "(https://|http://)" | while read line; do
    echo "$line" >> /tmp/auth_urls.txt
    echo "✅ Auth URL saved to /tmp/auth_urls.txt"
    # Also copy to Windows clipboard
    echo "$line" | clip.exe 2>/dev/null
done