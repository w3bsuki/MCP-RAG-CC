#!/usr/bin/env python3
"""
Autonomous Auditor Agent for MCP System
Continuously scans codebase for issues and submits findings
"""

import json
import os
import sys
import logging
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auditor_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("auditor-agent")

class AuditorAgent:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.role = "auditor"
        self.capabilities = [
            "code_analysis",
            "security_scanning", 
            "performance_auditing",
            "quality_assessment",
            "pattern_recognition",
            "continuous_monitoring"
        ]
        self.base_dir = Path(__file__).parent
        self.registered = False
        
    def register_with_coordinator(self) -> bool:
        """Register with the MCP coordinator"""
        try:
            # Use MCP client to register
            registration_data = {
                "agent_id": self.agent_id,
                "role": self.role,
                "capabilities": self.capabilities,
                "status": "active",
                "registered_at": datetime.utcnow().isoformat()
            }
            
            # Save registration info locally
            reg_file = self.base_dir / "mcp-coordinator" / f"{self.agent_id}-registration.json"
            with open(reg_file, 'w') as f:
                json.dump(registration_data, f, indent=2)
                
            logger.info(f"Agent {self.agent_id} registered successfully")
            self.registered = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to register with coordinator: {e}")
            return False
    
    def scan_codebase(self) -> List[Dict[str, Any]]:
        """Perform comprehensive codebase scan"""
        findings = []
        
        try:
            # Scan Python files for common issues
            python_files = list(self.base_dir.glob("**/*.py"))
            for py_file in python_files:
                if "venv" in str(py_file) or "__pycache__" in str(py_file):
                    continue
                    
                findings.extend(self._scan_python_file(py_file))
            
            # Scan for security issues
            findings.extend(self._scan_security_issues())
            
            # Scan for performance issues
            findings.extend(self._scan_performance_issues())
            
            logger.info(f"Found {len(findings)} potential issues")
            return findings
            
        except Exception as e:
            logger.error(f"Error during codebase scan: {e}")
            return []
    
    def _scan_python_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Scan individual Python file for issues"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Check for hardcoded secrets
                if any(secret in line.lower() for secret in ['password', 'secret', 'token', 'key']):
                    if '=' in line and any(quote in line for quote in ['"', "'"]):
                        findings.append({
                            "title": "Potential hardcoded secret",
                            "description": f"Line contains potential hardcoded credential: {line.strip()}",
                            "severity": "high",
                            "category": "security",
                            "file_path": str(file_path),
                            "line_number": line_num
                        })
                
                # Check for SQL injection risks
                if 'execute(' in line and ('"' in line or "'" in line):
                    if '%' in line or '+' in line:
                        findings.append({
                            "title": "Potential SQL injection risk",
                            "description": f"SQL query construction using string formatting: {line.strip()}",
                            "severity": "high",
                            "category": "security", 
                            "file_path": str(file_path),
                            "line_number": line_num
                        })
                
                # Check for long lines
                if len(line) > 120:
                    findings.append({
                        "title": "Line too long",
                        "description": f"Line exceeds 120 characters ({len(line)} chars)",
                        "severity": "low",
                        "category": "quality",
                        "file_path": str(file_path),
                        "line_number": line_num
                    })
                
                # Check for TODO/FIXME comments
                if any(marker in line.upper() for marker in ['TODO', 'FIXME', 'XXX', 'HACK']):
                    findings.append({
                        "title": "Technical debt marker",
                        "description": f"Code contains technical debt marker: {line.strip()}",
                        "severity": "medium",
                        "category": "quality",
                        "file_path": str(file_path),
                        "line_number": line_num
                    })
        
        except Exception as e:
            logger.error(f"Error scanning file {file_path}: {e}")
            
        return findings
    
    def _scan_security_issues(self) -> List[Dict[str, Any]]:
        """Scan for security-related issues"""
        findings = []
        
        # Check for .env files that might be committed
        env_files = list(self.base_dir.glob("**/.env*"))
        for env_file in env_files:
            if ".env" in env_file.name and not env_file.name.endswith('.example'):
                findings.append({
                    "title": "Environment file found",
                    "description": f"Environment file {env_file.name} may contain secrets",
                    "severity": "medium",
                    "category": "security",
                    "file_path": str(env_file),
                    "line_number": 1
                })
        
        return findings
    
    def _scan_performance_issues(self) -> List[Dict[str, Any]]:
        """Scan for performance-related issues"""
        findings = []
        
        # Check for large files that might slow down the system
        large_files = []
        for file_path in self.base_dir.rglob("*"):
            if file_path.is_file() and "venv" not in str(file_path):
                size_mb = file_path.stat().st_size / (1024 * 1024)
                if size_mb > 10:  # Files larger than 10MB
                    large_files.append((file_path, size_mb))
        
        for file_path, size_mb in large_files:
            findings.append({
                "title": "Large file detected",
                "description": f"File is {size_mb:.1f}MB, may impact performance",
                "severity": "low",
                "category": "performance",
                "file_path": str(file_path),
                "line_number": 1
            })
        
        return findings
    
    def submit_findings(self, findings: List[Dict[str, Any]]) -> bool:
        """Submit findings to the coordinator"""
        try:
            # Save findings locally
            findings_file = f"audit_findings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(findings_file, 'w') as f:
                json.dump(findings, f, indent=2)
            
            logger.info(f"Submitted {len(findings)} findings to {findings_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to submit findings: {e}")
            return False
    
    def run_continuous_audit(self):
        """Main audit loop"""
        logger.info(f"Starting continuous audit loop for {self.agent_id}")
        
        if not self.register_with_coordinator():
            logger.error("Failed to register with coordinator, exiting")
            return
        
        audit_count = 0
        while True:
            try:
                audit_count += 1
                logger.info(f"Starting audit cycle #{audit_count}")
                
                # Perform codebase scan
                findings = self.scan_codebase()
                
                if findings:
                    self.submit_findings(findings)
                    logger.info(f"Audit cycle #{audit_count} completed - {len(findings)} findings")
                else:
                    logger.info(f"Audit cycle #{audit_count} completed - no issues found")
                
                # Wait before next audit (30 seconds)
                time.sleep(30)
                
            except KeyboardInterrupt:
                logger.info("Audit loop interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in audit loop: {e}")
                time.sleep(10)  # Wait before retrying

def main():
    agent_id = "auditor-20250614-095401-0"
    auditor = AuditorAgent(agent_id)
    auditor.run_continuous_audit()

if __name__ == "__main__":
    main()