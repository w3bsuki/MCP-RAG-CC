#!/usr/bin/env python3
"""
Public Dashboard Server - Access from anywhere
"""

import os
import json
import subprocess
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=['*'])  # Allow all origins for public access

# HTML template for web interface
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP-RAG-CC Autonomous System Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
</head>
<body class="bg-gray-100">
    <div x-data="dashboard()" x-init="init()" class="container mx-auto p-4">
        <h1 class="text-3xl font-bold mb-6 text-center">🤖 Autonomous Agent System Dashboard</h1>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div class="bg-white p-4 rounded shadow">
                <h2 class="text-xl font-semibold mb-2">Active Agents</h2>
                <p class="text-3xl font-bold text-green-600" x-text="data.active_agents || 0"></p>
            </div>
            <div class="bg-white p-4 rounded shadow">
                <h2 class="text-xl font-semibold mb-2">Tasks Completed</h2>
                <p class="text-3xl font-bold text-blue-600" x-text="data.completed_tasks || 0"></p>
            </div>
            <div class="bg-white p-4 rounded shadow">
                <h2 class="text-xl font-semibold mb-2">Security Findings</h2>
                <p class="text-3xl font-bold text-red-600" x-text="data.total_findings || 0"></p>
                <p class="text-sm text-gray-600">
                    <span x-text="data.critical_findings || 0"></span> critical,
                    <span x-text="data.high_findings || 0"></span> high
                </p>
            </div>
        </div>
        
        <div class="bg-white p-4 rounded shadow mb-6">
            <h2 class="text-xl font-semibold mb-4">Recent Findings</h2>
            <div class="space-y-2">
                <template x-for="finding in data.recent_findings || []" :key="finding.id">
                    <div class="border-l-4 pl-4 py-2" 
                         :class="{
                            'border-red-600': finding.severity === 'critical',
                            'border-orange-500': finding.severity === 'high',
                            'border-yellow-500': finding.severity === 'medium',
                            'border-blue-500': finding.severity === 'low'
                         }">
                        <h3 class="font-semibold" x-text="finding.title"></h3>
                        <p class="text-sm text-gray-600" x-text="finding.description"></p>
                        <p class="text-xs text-gray-500">
                            <span x-text="finding.file_path"></span>:<span x-text="finding.line_number"></span>
                        </p>
                    </div>
                </template>
            </div>
        </div>
        
        <div class="bg-white p-4 rounded shadow">
            <h2 class="text-xl font-semibold mb-4">Task Queue</h2>
            <div class="mb-2">
                <span class="text-sm text-gray-600">Pending: </span>
                <span class="font-semibold" x-text="data.pending_tasks || 0"></span>
                <span class="text-sm text-gray-600 ml-4">In Progress: </span>
                <span class="font-semibold" x-text="data.in_progress_tasks || 0"></span>
            </div>
            <div class="space-y-2">
                <template x-for="task in (data.recent_tasks || []).slice(0, 5)" :key="task.id">
                    <div class="border rounded p-2">
                        <h3 class="font-semibold text-sm" x-text="task.description"></h3>
                        <p class="text-xs text-gray-600">
                            Status: <span x-text="task.status"></span> | 
                            Priority: <span x-text="task.priority"></span>
                        </p>
                    </div>
                </template>
            </div>
        </div>
        
        <div class="text-center mt-6 text-sm text-gray-600">
            Last updated: <span x-text="lastUpdate"></span>
        </div>
    </div>
    
    <script>
    function dashboard() {
        return {
            data: {},
            lastUpdate: '',
            
            async init() {
                await this.fetchData();
                setInterval(() => this.fetchData(), 5000);
            },
            
            async fetchData() {
                try {
                    const response = await fetch('/api/status');
                    this.data = await response.json();
                    this.lastUpdate = new Date().toLocaleTimeString();
                } catch (error) {
                    console.error('Failed to fetch data:', error);
                }
            }
        }
    }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/status')
def api_status():
    """Get current system status"""
    try:
        # Call the local dashboard API
        result = subprocess.run(
            ['curl', '-s', 'http://localhost:5000/api/status'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return jsonify(json.loads(result.stdout))
        else:
            return jsonify({'error': 'Failed to fetch status'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🌐 Public dashboard starting on port {port}")
    print(f"📱 Access from anywhere: http://YOUR_IP:{port}")
    
    # Get local IP for convenience
    try:
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"🏠 Local network access: http://{local_ip}:{port}")
    except:
        pass
    
    app.run(host='0.0.0.0', port=port, debug=False)