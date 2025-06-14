#!/usr/bin/env python3
import json

# Read all batch files
all_findings = []

for i in range(1, 5):
    with open(f'audit_findings_batch{i}.json', 'r') as f:
        findings = json.load(f)
        all_findings.extend(findings)

# Write merged findings
with open('all_audit_findings.json', 'w') as f:
    json.dump(all_findings, f, indent=2)

print(f"Merged {len(all_findings)} findings into all_audit_findings.json")