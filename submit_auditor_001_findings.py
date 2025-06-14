#!/usr/bin/env python3
"""
Submit AUDITOR-001 findings to MCP Coordinator
"""

import json
from datetime import datetime

# Load the findings
with open('auditor_001_findings_20250614_113537.json', 'r') as f:
    findings = json.load(f)

print("AUDITOR-001: Submitting audit findings to MCP Coordinator")
print(f"Total findings to submit: {len(findings)}")

# Critical findings first
critical_findings = [f for f in findings if f['severity'] == 'critical']
high_findings = [f for f in findings if f['severity'] == 'high']
other_findings = [f for f in findings if f['severity'] not in ['critical', 'high']]

print(f"\nPriority breakdown:")
print(f"- Critical: {len(critical_findings)}")
print(f"- High: {len(high_findings)}")
print(f"- Other: {len(other_findings)}")

print("\nFindings ready for submission via MCP tools:")
print("\nUse the following MCP commands to submit each finding:")

# Generate submission commands
for i, finding in enumerate(findings, 1):
    print(f"\n# Finding {i}: {finding['title']}")
    print(f"mcp-coordinator.submit_audit_finding({{")
    print(f'    "title": "{finding["title"]}",')
    print(f'    "description": "{finding["description"]}",')
    print(f'    "severity": "{finding["severity"]}",')
    print(f'    "category": "{finding["category"]}",')
    print(f'    "file_path": "{finding["file_path"]}",')
    print(f'    "line_number": {finding["line_number"]}')
    if 'recommendation' in finding:
        print(f',    "recommendation": "{finding["recommendation"]}"')
    print(f"}})")

print("\n\nAUDITOR-001: Ready to submit findings. Use the MCP tool commands above.")