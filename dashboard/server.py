#!/usr/bin/env python3
"""
Simple Web Dashboard for Autonomous Agent Monitoring
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
import subprocess
from typing import Dict, List

try:
    from flask import Flask, render_template_string, jsonify
    from flask_cors import CORS
except ImportError:
    print("Flask not installed. Install with: pip install flask flask-cors")
    print("Dashboard is optional - the system works without it.")
    exit(0)

app = Flask(__name__)
CORS(app)

# Dashboard HTML template
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Autonomous Agent Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 30px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .card h3 {
            margin-top: 0;
            color: #34495e;
        }
        .status {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        .status.active { background: #27ae60; color: white; }
        .status.inactive { background: #e74c3c; color: white; }
        .status.pending { background: #f39c12; color: white; }
        .status.completed { background: #3498db; color: white; }
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 10px 0;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }
        .task-list {
            max-height: 300px;
            overflow-y: auto;
        }
        .task-item {
            padding: 10px;
            margin: 5px 0;
            background: #f8f9fa;
            border-radius: 4px;
            border-left: 4px solid #3498db;
        }
        .finding-item {
            padding: 10px;
            margin: 5px 0;
            background: #fff3cd;
            border-radius: 4px;
            border-left: 4px solid #f39c12;
        }
        .severity-critical { border-left-color: #e74c3c !important; }
        .severity-high { border-left-color: #e67e22 !important; }
        .severity-medium { border-left-color: #f39c12 !important; }
        .severity-low { border-left-color: #3498db !important; }
        .timestamp {
            color: #7f8c8d;
            font-size: 12px;
        }
        .refresh-btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        .refresh-btn:hover {
            background: #2980b9;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Autonomous Agent Dashboard</h1>
        
        <div class="grid">
            <div class="card">
                <h3>System Status</h3>
                <div class="metric">
                    <span>Tmux Session</span>
                    <span class="status" id="tmux-status">Checking...</span>
                </div>
                <div class="metric">
                    <span>Active Agents</span>
                    <span class="metric-value" id="active-agents">0</span>
                </div>
                <div class="metric">
                    <span>Uptime</span>
                    <span id="uptime">--:--:--</span>
                </div>
            </div>
            
            <div class="card">
                <h3>Task Queue</h3>
                <div class="metric">
                    <span>Pending</span>
                    <span class="metric-value" id="pending-tasks">0</span>
                </div>
                <div class="metric">
                    <span>In Progress</span>
                    <span class="metric-value" id="progress-tasks">0</span>
                </div>
                <div class="metric">
                    <span>Completed</span>
                    <span class="metric-value" id="completed-tasks">0</span>
                </div>
            </div>
            
            <div class="card">
                <h3>Audit Findings</h3>
                <div class="metric">
                    <span>Total Findings</span>
                    <span class="metric-value" id="total-findings">0</span>
                </div>
                <div class="metric">
                    <span>Critical</span>
                    <span class="metric-value" id="critical-findings">0</span>
                </div>
                <div class="metric">
                    <span>High</span>
                    <span class="metric-value" id="high-findings">0</span>
                </div>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>Recent Tasks</h3>
                <div class="task-list" id="recent-tasks">
                    <p>Loading...</p>
                </div>
            </div>
            
            <div class="card">
                <h3>Recent Findings</h3>
                <div class="task-list" id="recent-findings">
                    <p>Loading...</p>
                </div>
            </div>
        </div>
        
        <button class="refresh-btn" onclick="refreshData()">🔄 Refresh</button>
        <span class="timestamp" style="margin-left: 10px;">Last updated: <span id="last-update">Never</span></span>
    </div>
    
    <script>
        async function refreshData() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                // Update system status
                document.getElementById('tmux-status').textContent = data.tmux_active ? 'Active' : 'Inactive';
                document.getElementById('tmux-status').className = 'status ' + (data.tmux_active ? 'active' : 'inactive');
                document.getElementById('active-agents').textContent = data.active_agents;
                document.getElementById('uptime').textContent = data.uptime || '--:--:--';
                
                // Update task counts
                document.getElementById('pending-tasks').textContent = data.pending_tasks;
                document.getElementById('progress-tasks').textContent = data.in_progress_tasks;
                document.getElementById('completed-tasks').textContent = data.completed_tasks;
                
                // Update findings counts
                document.getElementById('total-findings').textContent = data.total_findings;
                document.getElementById('critical-findings').textContent = data.critical_findings;
                document.getElementById('high-findings').textContent = data.high_findings;
                
                // Update recent tasks
                const tasksHtml = data.recent_tasks.map(task => `
                    <div class="task-item">
                        <strong>${task.type}: ${task.description}</strong><br>
                        <span class="status ${task.status}">${task.status}</span>
                        <span class="timestamp">${new Date(task.created_at).toLocaleString()}</span>
                    </div>
                `).join('') || '<p>No recent tasks</p>';
                document.getElementById('recent-tasks').innerHTML = tasksHtml;
                
                // Update recent findings
                const findingsHtml = data.recent_findings.map(finding => `
                    <div class="finding-item severity-${finding.severity}">
                        <strong>${finding.title}</strong><br>
                        <span class="timestamp">${finding.file_path || 'General'}</span>
                    </div>
                `).join('') || '<p>No recent findings</p>';
                document.getElementById('recent-findings').innerHTML = findingsHtml;
                
                // Update timestamp
                document.getElementById('last-update').textContent = new Date().toLocaleString();
                
            } catch (error) {
                console.error('Failed to refresh data:', error);
            }
        }
        
        // Auto-refresh every 10 seconds
        setInterval(refreshData, 10000);
        
        // Initial load
        refreshData();
    </script>
</body>
</html>
'''

class DashboardServer:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.state_file = self.base_dir / "mcp-coordinator" / "state.json"
    
    def get_status(self) -> Dict:
        """Get current system status"""
        status = {
            'tmux_active': self.check_tmux_session(),
            'active_agents': 0,
            'uptime': None,
            'pending_tasks': 0,
            'in_progress_tasks': 0,
            'completed_tasks': 0,
            'total_findings': 0,
            'critical_findings': 0,
            'high_findings': 0,
            'recent_tasks': [],
            'recent_findings': []
        }
        
        # Load state file
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                
                # Count agents
                status['active_agents'] = len([a for a in state.get('agents', {}).values() 
                                             if a.get('status') == 'active'])
                
                # Count tasks
                tasks = state.get('task_queue', [])
                status['pending_tasks'] = len([t for t in tasks if t['status'] == 'pending'])
                status['in_progress_tasks'] = len([t for t in tasks if t['status'] == 'in_progress'])
                status['completed_tasks'] = len([t for t in tasks if t['status'] == 'completed'])
                
                # Get recent tasks
                status['recent_tasks'] = sorted(tasks, 
                                              key=lambda x: x.get('created_at', ''), 
                                              reverse=True)[:5]
                
                # Count findings
                findings = state.get('audit_findings', [])
                status['total_findings'] = len(findings)
                status['critical_findings'] = len([f for f in findings if f.get('severity') == 'critical'])
                status['high_findings'] = len([f for f in findings if f.get('severity') == 'high'])
                
                # Get recent findings
                status['recent_findings'] = sorted(findings, 
                                                 key=lambda x: x.get('submitted_at', ''), 
                                                 reverse=True)[:5]
                
            except Exception as e:
                print(f"Error reading state file: {e}")
        
        return status
    
    def check_tmux_session(self) -> bool:
        """Check if tmux session is active"""
        try:
            result = subprocess.run(['tmux', 'has-session', '-t', 'autonomous-claude'], 
                                  capture_output=True)
            return result.returncode == 0
        except:
            return False

dashboard = DashboardServer()

@app.route('/')
def index():
    """Serve the dashboard HTML"""
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/status')
def api_status():
    """Get current status as JSON"""
    return jsonify(dashboard.get_status())

def main():
    """Run the dashboard server"""
    print("🌐 Starting dashboard server...")
    print("📊 Dashboard available at: http://localhost:5000")
    print("Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()