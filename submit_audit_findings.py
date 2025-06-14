#!/usr/bin/env python3
"""
Submit audit findings to MCP coordinator
This script would normally use the MCP tools, but in Claude Code environment,
it saves the findings in the expected format for the coordinator to process.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

def submit_findings():
    """Submit audit findings to the coordinator"""
    
    # Load the comprehensive findings
    findings_file = Path("audit_findings_comprehensive.json")
    if not findings_file.exists():
        print("Error: audit_findings_comprehensive.json not found")
        return False
    
    with open(findings_file, 'r') as f:
        findings = json.load(f)
    
    print(f"Loaded {len(findings)} findings from comprehensive audit")
    
    # In a real MCP environment, each finding would be submitted via:
    # mcp-coordinator.submit_audit_finding(finding)
    
    # For now, save to the coordinator's expected location
    coordinator_dir = Path("mcp-coordinator")
    coordinator_dir.mkdir(exist_ok=True)
    
    # Create a findings file in the format the coordinator expects
    submitted_findings = []
    
    for i, finding in enumerate(findings):
        # Add required fields for coordinator
        finding['id'] = f"audit-{datetime.now().strftime('%Y%m%d')}-{i+1:03d}"
        finding['submitted_at'] = datetime.now().isoformat()
        finding['status'] = 'new'
        finding['submitted_by'] = 'security-auditor'
        
        submitted_findings.append(finding)
        
        print(f"✓ Finding {i+1}: {finding['title']} ({finding['severity']})")
    
    # Save findings for coordinator
    output_file = coordinator_dir / f"audit_findings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'findings': submitted_findings,
            'summary': {
                'total': len(submitted_findings),
                'critical': len([f for f in submitted_findings if f['severity'] == 'critical']),
                'high': len([f for f in submitted_findings if f['severity'] == 'high']),
                'medium': len([f for f in submitted_findings if f['severity'] == 'medium']),
                'low': len([f for f in submitted_findings if f['severity'] == 'low'])
            },
            'submitted_at': datetime.now().isoformat(),
            'audit_type': 'comprehensive_security_audit'
        }, f, indent=2)
    
    print(f"\n✅ Successfully submitted {len(submitted_findings)} findings")
    print(f"📁 Findings saved to: {output_file}")
    
    # Print summary
    print("\n📊 Summary by Severity:")
    print(f"   Critical: {len([f for f in submitted_findings if f['severity'] == 'critical'])}")
    print(f"   High:     {len([f for f in submitted_findings if f['severity'] == 'high'])}")
    print(f"   Medium:   {len([f for f in submitted_findings if f['severity'] == 'medium'])}")
    print(f"   Low:      {len([f for f in submitted_findings if f['severity'] == 'low'])}")
    
    print("\n📊 Summary by Category:")
    categories = {}
    for finding in submitted_findings:
        cat = finding['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items()):
        print(f"   {cat.replace('_', ' ').title()}: {count}")
    
    return True

if __name__ == "__main__":
    success = submit_findings()
    sys.exit(0 if success else 1)