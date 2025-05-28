"""
Advanced Compliance Automation for the Deployment Operations Layer

This module provides comprehensive compliance automation capabilities for the
Deployment Operations Layer, implementing policy-driven compliance checking,
automated remediation workflows, and comprehensive compliance reporting.

The compliance automation framework supports policy definition, compliance checking,
automated remediation, and reporting for regulatory and organizational requirements.
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta

from ..analytics.analytics_manager import AnalyticsManager
from ..agent.agent_utils import AgentUtils
from ..security.security_framework_manager import SecurityFrameworkManager

# Configure logging
logger = logging.getLogger(__name__)

class ComplianceManager:
    """Compliance manager for policy-driven compliance automation"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the compliance manager
        
        Args:
            config: Configuration for the compliance manager
        """
        self.config = config
        self.analytics_manager = AnalyticsManager()
        self.agent_utils = AgentUtils()
        self.security_manager = SecurityFrameworkManager()
        self.policies = {}
        self.compliance_checks = {}
        self.remediation_workflows = {}
        self.compliance_reports = {}
        self.status = "initialized"
        
        logger.info("Initialized compliance manager")
    
    async def initialize(self):
        """Initialize the compliance manager"""
        try:
            # Load policies
            await self._load_policies()
            
            # Load compliance checks
            await self._load_compliance_checks()
            
            # Load remediation workflows
            await self._load_remediation_workflows()
            
            self.status = "ready"
            logger.info("Compliance manager initialized successfully")
            
            return {
                "status": "success",
                "policies": len(self.policies),
                "compliance_checks": len(self.compliance_checks),
                "remediation_workflows": len(self.remediation_workflows)
            }
        except Exception as e:
            self.status = "error"
            logger.error(f"Failed to initialize compliance manager: {str(e)}")
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _load_policies(self):
        """Load compliance policies"""
        try:
            # In a real implementation, this would load policies from storage
            # For demonstration, we'll create sample policies
            self.policies = {
                "gdpr": {
                    "id": "gdpr",
                    "name": "General Data Protection Regulation",
                    "description": "EU data protection and privacy regulations",
                    "version": "1.0.0",
                    "status": "active",
                    "requirements": [
                        {
                            "id": "gdpr-data-encryption",
                            "name": "Data Encryption",
                            "description": "All personal data must be encrypted at rest and in transit",
                            "severity": "high"
                        },
                        {
                            "id": "gdpr-data-retention",
                            "name": "Data Retention",
                            "description": "Personal data must not be kept longer than necessary",
                            "severity": "medium"
                        },
                        {
                            "id": "gdpr-data-access",
                            "name": "Data Access Controls",
                            "description": "Access to personal data must be restricted and logged",
                            "severity": "high"
                        },
                        {
                            "id": "gdpr-data-processing",
                            "name": "Data Processing Records",
                            "description": "Records of data processing activities must be maintained",
                            "severity": "medium"
                        },
                        {
                            "id": "gdpr-data-breach",
                            "name": "Data Breach Notification",
                            "description": "Data breaches must be reported within 72 hours",
                            "severity": "high"
                        }
                    ]
                },
                "hipaa": {
                    "id": "hipaa",
                    "name": "Health Insurance Portability and Accountability Act",
                    "description": "US healthcare data privacy and security regulations",
                    "version": "1.0.0",
                    "status": "active",
                    "requirements": [
                        {
                            "id": "hipaa-data-encryption",
                            "name": "Data Encryption",
                            "description": "All protected health information must be encrypted",
                            "severity": "high"
                        },
                        {
                            "id": "hipaa-access-controls",
                            "name": "Access Controls",
                            "description": "Access to protected health information must be restricted",
                            "severity": "high"
                        },
                        {
                            "id": "hipaa-audit-controls",
                            "name": "Audit Controls",
                            "description": "Systems must record and examine activity",
                            "severity": "medium"
                        },
                        {
                            "id": "hipaa-integrity-controls",
                            "name": "Integrity Controls",
                            "description": "Systems must prevent unauthorized alteration or destruction of data",
                            "severity": "high"
                        },
                        {
                            "id": "hipaa-transmission-security",
                            "name": "Transmission Security",
                            "description": "Data must be protected when transmitted over networks",
                            "severity": "high"
                        }
                    ]
                },
                "pci-dss": {
                    "id": "pci-dss",
                    "name": "Payment Card Industry Data Security Standard",
                    "description": "Security standards for organizations that handle credit card data",
                    "version": "1.0.0",
                    "status": "active",
                    "requirements": [
                        {
                            "id": "pci-dss-network-security",
                            "name": "Network Security",
                            "description": "Install and maintain a firewall configuration to protect cardholder data",
                            "severity": "high"
                        },
                        {
                            "id": "pci-dss-data-protection",
                            "name": "Data Protection",
                            "description": "Protect stored cardholder data",
                            "severity": "high"
                        },
                        {
                            "id": "pci-dss-access-control",
                            "name": "Access Control",
                            "description": "Restrict access to cardholder data by business need to know",
                            "severity": "high"
                        },
                        {
                            "id": "pci-dss-vulnerability-management",
                            "name": "Vulnerability Management",
                            "description": "Develop and maintain secure systems and applications",
                            "severity": "medium"
                        },
                        {
                            "id": "pci-dss-monitoring",
                            "name": "Monitoring and Testing",
                            "description": "Regularly monitor and test networks",
                            "severity": "medium"
                        }
                    ]
                },
                "iso27001": {
                    "id": "iso27001",
                    "name": "ISO/IEC 27001",
                    "description": "International standard for information security management",
                    "version": "1.0.0",
                    "status": "active",
                    "requirements": [
                        {
                            "id": "iso27001-security-policy",
                            "name": "Security Policy",
                            "description": "Establish security policy and management framework",
                            "severity": "medium"
                        },
                        {
                            "id": "iso27001-asset-management",
                            "name": "Asset Management",
                            "description": "Identify and classify information assets",
                            "severity": "medium"
                        },
                        {
                            "id": "iso27001-access-control",
                            "name": "Access Control",
                            "description": "Control access to information and systems",
                            "severity": "high"
                        },
                        {
                            "id": "iso27001-cryptography",
                            "name": "Cryptography",
                            "description": "Use cryptographic controls to protect information",
                            "severity": "high"
                        },
                        {
                            "id": "iso27001-incident-management",
                            "name": "Incident Management",
                            "description": "Manage information security incidents",
                            "severity": "medium"
                        }
                    ]
                },
                "soc2": {
                    "id": "soc2",
                    "name": "SOC 2",
                    "description": "Service Organization Control 2 for service providers",
                    "version": "1.0.0",
                    "status": "active",
                    "requirements": [
                        {
                            "id": "soc2-security",
                            "name": "Security",
                            "description": "Protection of system resources against unauthorized access",
                            "severity": "high"
                        },
                        {
                            "id": "soc2-availability",
                            "name": "Availability",
                            "description": "System availability for operation and use as committed",
                            "severity": "medium"
                        },
                        {
                            "id": "soc2-processing-integrity",
                            "name": "Processing Integrity",
                            "description": "System processing is complete, accurate, timely, and authorized",
                            "severity": "medium"
                        },
                        {
                            "id": "soc2-confidentiality",
                            "name": "Confidentiality",
                            "description": "Information designated as confidential is protected",
                            "severity": "high"
                        },
                        {
                            "id": "soc2-privacy",
                            "name": "Privacy",
                            "description": "Personal information is collected, used, retained, and disclosed in conformity with commitments",
                            "severity": "high"
                        }
                    ]
                }
            }
            
            logger.info(f"Loaded {len(self.policies)} compliance policies")
        except Exception as e:
            logger.error(f"Failed to load compliance policies: {str(e)}")
            raise
    
    async def _load_compliance_checks(self):
        """Load compliance checks"""
        try:
            # In a real implementation, this would load compliance checks from storage
            # For demonstration, we'll create sample compliance checks
            self.compliance_checks = {
                "check-data-encryption": {
                    "id": "check-data-encryption",
                    "name": "Data Encryption Check",
                    "description": "Check if data is encrypted at rest and in transit",
                    "policy_requirements": ["gdpr-data-encryption", "hipaa-data-encryption", "pci-dss-data-protection", "iso27001-cryptography"],
                    "check_type": "automated",
                    "check_script": "data_encryption_check.py",
                    "parameters": {
                        "encryption_algorithms": ["AES-256", "RSA-2048"]
                    }
                },
                "check-access-controls": {
                    "id": "check-access-controls",
                    "name": "Access Controls Check",
                    "description": "Check if access controls are properly implemented",
                    "policy_requirements": ["gdpr-data-access", "hipaa-access-controls", "pci-dss-access-control", "iso27001-access-control", "soc2-security"],
                    "check_type": "automated",
                    "check_script": "access_controls_check.py",
                    "parameters": {
                        "required_controls": ["authentication", "authorization", "least_privilege"]
                    }
                },
                "check-data-retention": {
                    "id": "check-data-retention",
                    "name": "Data Retention Check",
                    "description": "Check if data retention policies are properly implemented",
                    "policy_requirements": ["gdpr-data-retention"],
                    "check_type": "automated",
                    "check_script": "data_retention_check.py",
                    "parameters": {
                        "max_retention_days": 365
                    }
                },
                "check-audit-logging": {
                    "id": "check-audit-logging",
                    "name": "Audit Logging Check",
                    "description": "Check if audit logging is properly implemented",
                    "policy_requirements": ["hipaa-audit-controls", "pci-dss-monitoring", "soc2-security"],
                    "check_type": "automated",
                    "check_script": "audit_logging_check.py",
                    "parameters": {
                        "required_events": ["login", "logout", "data_access", "data_modification", "data_deletion"]
                    }
                },
                "check-vulnerability-management": {
                    "id": "check-vulnerability-management",
                    "name": "Vulnerability Management Check",
                    "description": "Check if vulnerability management processes are properly implemented",
                    "policy_requirements": ["pci-dss-vulnerability-management"],
                    "check_type": "automated",
                    "check_script": "vulnerability_management_check.py",
                    "parameters": {
                        "max_scan_age_days": 30,
                        "max_critical_vulnerabilities": 0,
                        "max_high_vulnerabilities": 0
                    }
                }
            }
            
            logger.info(f"Loaded {len(self.compliance_checks)} compliance checks")
        except Exception as e:
            logger.error(f"Failed to load compliance checks: {str(e)}")
            raise
    
    async def _load_remediation_workflows(self):
        """Load remediation workflows"""
        try:
            # In a real implementation, this would load remediation workflows from storage
            # For demonstration, we'll create sample remediation workflows
            self.remediation_workflows = {
                "remediate-data-encryption": {
                    "id": "remediate-data-encryption",
                    "name": "Data Encryption Remediation",
                    "description": "Remediate data encryption issues",
                    "compliance_check_id": "check-data-encryption",
                    "workflow_type": "automated",
                    "workflow_script": "data_encryption_remediation.py",
                    "parameters": {
                        "encryption_algorithm": "AES-256"
                    }
                },
                "remediate-access-controls": {
                    "id": "remediate-access-controls",
                    "name": "Access Controls Remediation",
                    "description": "Remediate access control issues",
                    "compliance_check_id": "check-access-controls",
                    "workflow_type": "automated",
                    "workflow_script": "access_controls_remediation.py",
                    "parameters": {
                        "enforce_least_privilege": True
                    }
                },
                "remediate-data-retention": {
                    "id": "remediate-data-retention",
                    "name": "Data Retention Remediation",
                    "description": "Remediate data retention issues",
                    "compliance_check_id": "check-data-retention",
                    "workflow_type": "automated",
                    "workflow_script": "data_retention_remediation.py",
                    "parameters": {
                        "retention_days": 365
                    }
                },
                "remediate-audit-logging": {
                    "id": "remediate-audit-logging",
                    "name": "Audit Logging Remediation",
                    "description": "Remediate audit logging issues",
                    "compliance_check_id": "check-audit-logging",
                    "workflow_type": "automated",
                    "workflow_script": "audit_logging_remediation.py",
                    "parameters": {
                        "enable_all_required_events": True
                    }
                },
                "remediate-vulnerability-management": {
                    "id": "remediate-vulnerability-management",
                    "name": "Vulnerability Management Remediation",
                    "description": "Remediate vulnerability management issues",
                    "compliance_check_id": "check-vulnerability-management",
                    "workflow_type": "manual",
                    "workflow_script": None,
                    "parameters": {
                        "instructions": "Review and patch all critical and high vulnerabilities"
                    }
                }
            }
            
            logger.info(f"Loaded {len(self.remediation_workflows)} remediation workflows")
        except Exception as e:
            logger.error(f"Failed to load remediation workflows: {str(e)}")
            raise
    
    async def run_compliance_check(self, check_id: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run a compliance check
        
        Args:
            check_id: ID of the compliance check to run
            parameters: Additional parameters for the check, or None to use defaults
            
        Returns:
            Dict containing compliance check results
        """
        try:
            if check_id not in self.compliance_checks:
                return {
                    "status": "not_found",
                    "check_id": check_id
                }
            
            check = self.compliance_checks[check_id]
            
            logger.info(f"Running compliance check {check_id}: {check['name']}")
            
            # Merge parameters
            merged_parameters = check.get("parameters", {}).copy()
            if parameters:
                merged_parameters.update(parameters)
            
            # In a real implementation, this would run the actual compliance check
            # For demonstration, we'll simulate the check
            
            # Generate check run ID
            check_run_id = f"check-run-{check_id}-{self.agent_utils.generate_id()}"
            
            # Create check run record
            check_run = {
                "id": check_run_id,
                "check_id": check_id,
                "status": "running",
                "parameters": merged_parameters,
                "started_at": self.agent_utils.get_current_timestamp()
            }
            
            # Simulate check execution
            await asyncio.sleep(2)
            
            # Simulate check results (80% pass, 20% fail)
            import random
            passed = random.random() < 0.8
            
            if passed:
                check_run["status"] = "passed"
                check_run["results"] = {
                    "passed": True,
                    "details": f"All {check['name']} requirements met"
                }
            else:
                check_run["status"] = "failed"
                check_run["results"] = {
                    "passed": False,
                    "details": f"Failed to meet {check['name']} requirements",
                    "issues": [
                        {
                            "id": f"issue-{self.agent_utils.generate_id()}",
                            "description": f"Sample issue for {check['name']}",
                            "severity": "high",
                            "remediation_workflow_id": f"remediate-{check_id.replace('check-', '')}"
                        }
                    ]
                }
            
            check_run["completed_at"] = self.agent_utils.get_current_timestamp()
            
            # Record check run in analytics
            self.analytics_manager.record_compliance_check_run(
                check_run_id=check_run_id,
                check_id=check_id,
                status=check_run["status"],
                passed=passed,
                timestamp=check_run["completed_at"]
            )
            
            logger.info(f"Compliance check {check_id} completed with status: {check_run['status']}")
            
            return {
                "status": "success",
                "check_run_id": check_run_id,
                "check_run": check_run
            }
        except Exception as e:
            logger.error(f"Failed to run compliance check {check_id}: {str(e)}")
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def run_all_compliance_checks(self, policy_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run all compliance checks
        
        Args:
            policy_id: ID of the policy to check, or None for all checks
            
        Returns:
            Dict containing compliance check results
        """
        try:
            # Determine which checks to run
            checks_to_run = []
            
            if policy_id:
                # Run checks for a specific policy
                if policy_id not in self.policies:
                    return {
                        "status": "not_found",
                        "policy_id": policy_id
                    }
                
                policy = self.policies[policy_id]
                policy_requirements = [req["id"] for req in policy["requirements"]]
                
                # Find checks that cover these requirements
                for check_id, check in self.compliance_checks.items():
                    for req_id in check.get("policy_requirements", []):
                        if req_id in policy_requirements:
                            checks_to_run.append(check_id)
                            break
            else:
                # Run all checks
                checks_to_run = list(self.compliance_checks.keys())
            
            logger.info(f"Running {len(checks_to_run)} compliance checks")
            
            # Generate check run batch ID
            batch_id = f"check-batch-{self.agent_utils.generate_id()}"
            
            # Create batch record
            batch = {
                "id": batch_id,
                "policy_id": policy_id,
                "status": "running",
                "check_count": len(checks_to_run),
                "started_at": self.agent_utils.get_current_timestamp(),
                "check_runs": {}
            }
            
            # Run all checks
            for check_id in checks_to_run:
                result = await self.run_compliance_check(check_id)
                
                if result.get("status") == "success":
                    batch["check_runs"][check_id] = result.get("check_run")
            
            # Determine batch status
            passed_count = 0
            failed_count = 0
            error_count = 0
            
            for check_id, check_run in batch["check_runs"].items():
                if check_run["status"] == "passed":
                    passed_count += 1
                elif check_run["status"] == "failed":
                    failed_count += 1
                else:
                    error_count += 1
            
            if error_count > 0:
                batch["status"] = "error"
            elif failed_count > 0:
                batch["status"] = "failed"
            else:
                batch["status"] = "passed"
            
            batch["completed_at"] = self.agent_utils.get_current_timestamp()
            batch["summary"] = {
                "total": len(checks_to_run),
                "passed": passed_count,
                "failed": failed_count,
                "error": error_count
            }
            
            # Record batch in analytics
            self.analytics_manager.record_compliance_check_batch(
                batch_id=batch_id,
                policy_id=policy_id,
                status=batch["status"],
                summary=batch["summary"],
                timestamp=batch["completed_at"]
            )
            
            logger.info(f"Compliance check batch {batch_id} completed with status: {batch['status']}")
            
            return {
                "status": "success",
                "batch_id": batch_id,
                "batch": batch
            }
        except Exception as e:
            logger.error(f"Failed to run all compliance checks: {str(e)}")
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def run_remediation_workflow(self, workflow_id: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run a remediation workflow
        
        Args:
            workflow_id: ID of the remediation workflow to run
            parameters: Additional parameters for the workflow, or None to use defaults
            
        Returns:
            Dict containing remediation workflow results
        """
        try:
            if workflow_id not in self.remediation_workflows:
                return {
                    "status": "not_found",
                    "workflow_id": workflow_id
                }
            
            workflow = self.remediation_workflows[workflow_id]
            
            logger.info(f"Running remediation workflow {workflow_id}: {workflow['name']}")
            
            # Merge parameters
            merged_parameters = workflow.get("parameters", {}).copy()
            if parameters:
                merged_parameters.update(parameters)
            
            # Generate workflow run ID
            workflow_run_id = f"workflow-run-{workflow_id}-{self.agent_utils.generate_id()}"
            
            # Create workflow run record
            workflow_run = {
                "id": workflow_run_id,
                "workflow_id": workflow_id,
                "status": "running",
                "parameters": merged_parameters,
                "started_at": self.agent_utils.get_current_timestamp()
            }
            
            # Check if this is an automated or manual workflow
            if workflow["workflow_type"] == "automated":
                # In a real implementation, this would run the actual remediation workflow
                # For demonstration, we'll simulate the workflow
                
                # Simulate workflow execution
                await asyncio.sleep(3)
                
                # Simulate workflow results (90% success, 10% failure)
                import random
                success = random.random() < 0.9
                
                if success:
                    workflow_run["status"] = "completed"
                    workflow_run["results"] = {
                        "success": True,
                        "details": f"Successfully remediated {workflow['name']} issues"
                    }
                else:
                    workflow_run["status"] = "failed"
                    workflow_run["results"] = {
                        "success": False,
                        "details": f"Failed to remediate {workflow['name']} issues",
                        "error": "Simulated failure"
                    }
            else:
                # Manual workflow
                workflow_run["status"] = "manual_action_required"
                workflow_run["results"] = {
                    "success": False,
                    "details": f"Manual action required for {workflow['name']}",
                    "instructions": merged_parameters.get("instructions", "No instructions provided")
                }
            
            workflow_run["completed_at"] = self.agent_utils.get_current_timestamp()
            
            # Record workflow run in analytics
            self.analytics_manager.record_remediation_workflow_run(
                workflow_run_id=workflow_run_id,
                workflow_id=workflow_id,
                status=workflow_run["status"],
                success=workflow_run.get("results", {}).get("success", False),
                timestamp=workflow_run["completed_at"]
            )
            
            logger.info(f"Remediation workflow {workflow_id} completed with status: {workflow_run['status']}")
            
            return {
                "status": "success",
                "workflow_run_id": workflow_run_id,
                "workflow_run": workflow_run
            }
        except Exception as e:
            logger.error(f"Failed to run remediation workflow {workflow_id}: {str(e)}")
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def generate_compliance_report(self, policy_id: str) -> Dict[str, Any]:
        """
        Generate a compliance report for a policy
        
        Args:
            policy_id: ID of the policy to generate a report for
            
        Returns:
            Dict containing compliance report results
        """
        try:
            if policy_id not in self.policies:
                return {
                    "status": "not_found",
                    "policy_id": policy_id
                }
            
            policy = self.policies[policy_id]
            
            logger.info(f"Generating compliance report for policy {policy_id}: {policy['name']}")
            
            # Run compliance checks for the policy
            check_result = await self.run_all_compliance_checks(policy_id)
            
            if check_result.get("status") != "success":
                return check_result
            
            batch = check_result.get("batch")
            
            # Generate report ID
            report_id = f"report-{policy_id}-{self.agent_utils.generate_id()}"
            
            # Create report record
            report = {
                "id": report_id,
                "policy_id": policy_id,
                "policy_name": policy["name"],
                "status": batch["status"],
                "generated_at": self.agent_utils.get_current_timestamp(),
                "summary": batch["summary"],
                "details": {
                    "policy": policy,
                    "check_batch": batch
                }
            }
            
            # Store report
            self.compliance_reports[report_id] = report
            
            # Record report generation in analytics
            self.analytics_manager.record_compliance_report_generation(
                report_id=report_id,
                policy_id=policy_id,
                status=report["status"],
                summary=report["summary"],
                timestamp=report["generated_at"]
            )
            
            logger.info(f"Compliance report {report_id} generated with status: {report['status']}")
            
            return {
                "status": "success",
                "report_id": report_id,
                "report": report
            }
        except Exception as e:
            logger.error(f"Failed to generate compliance report for policy {policy_id}: {str(e)}")
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_compliance_report(self, report_id: str) -> Dict[str, Any]:
        """
        Get a compliance report
        
        Args:
            report_id: ID of the report to get
            
        Returns:
            Dict containing compliance report
        """
        if report_id not in self.compliance_reports:
            return {
                "status": "not_found",
                "report_id": report_id
            }
        
        return {
            "status": "success",
            "report": self.compliance_reports[report_id]
        }
    
    async def list_compliance_reports(self, policy_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List compliance reports
        
        Args:
            policy_id: Filter by policy ID, or None for all reports
            
        Returns:
            List of compliance reports
        """
        reports = []
        
        for report_id, report in self.compliance_reports.items():
            if policy_id is None or report["policy_id"] == policy_id:
                reports.append({
                    "id": report["id"],
                    "policy_id": report["policy_id"],
                    "policy_name": report["policy_name"],
                    "status": report["status"],
                    "generated_at": report["generated_at"],
                    "summary": report["summary"]
                })
        
        # Sort by generation time (newest first)
        reports.sort(key=lambda r: r["generated_at"], reverse=True)
        
        return reports
    
    async def get_policy(self, policy_id: str) -> Dict[str, Any]:
        """
        Get a compliance policy
        
        Args:
            policy_id: ID of the policy to get
            
        Returns:
            Dict containing compliance policy
        """
        if policy_id not in self.policies:
            return {
                "status": "not_found",
                "policy_id": policy_id
            }
        
        return {
            "status": "success",
            "policy": self.policies[policy_id]
        }
    
    async def list_policies(self) -> List[Dict[str, Any]]:
        """
        List compliance policies
        
        Returns:
            List of compliance policies
        """
        return list(self.policies.values())
    
    async def get_compliance_check(self, check_id: str) -> Dict[str, Any]:
        """
        Get a compliance check
        
        Args:
            check_id: ID of the check to get
            
        Returns:
            Dict containing compliance check
        """
        if check_id not in self.compliance_checks:
            return {
                "status": "not_found",
                "check_id": check_id
            }
        
        return {
            "status": "success",
            "check": self.compliance_checks[check_id]
        }
    
    async def list_compliance_checks(self, policy_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List compliance checks
        
        Args:
            policy_id: Filter by policy ID, or None for all checks
            
        Returns:
            List of compliance checks
        """
        if policy_id is None:
            # Return all checks
            return list(self.compliance_checks.values())
        
        # Filter checks by policy
        if policy_id not in self.policies:
            return []
        
        policy = self.policies[policy_id]
        policy_requirements = [req["id"] for req in policy["requirements"]]
        
        checks = []
        for check_id, check in self.compliance_checks.items():
            for req_id in check.get("policy_requirements", []):
                if req_id in policy_requirements:
                    checks.append(check)
                    break
        
        return checks
    
    async def get_remediation_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get a remediation workflow
        
        Args:
            workflow_id: ID of the workflow to get
            
        Returns:
            Dict containing remediation workflow
        """
        if workflow_id not in self.remediation_workflows:
            return {
                "status": "not_found",
                "workflow_id": workflow_id
            }
        
        return {
            "status": "success",
            "workflow": self.remediation_workflows[workflow_id]
        }
    
    async def list_remediation_workflows(self, check_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List remediation workflows
        
        Args:
            check_id: Filter by compliance check ID, or None for all workflows
            
        Returns:
            List of remediation workflows
        """
        if check_id is None:
            # Return all workflows
            return list(self.remediation_workflows.values())
        
        # Filter workflows by check
        workflows = []
        for workflow_id, workflow in self.remediation_workflows.items():
            if workflow.get("compliance_check_id") == check_id:
                workflows.append(workflow)
        
        return workflows
    
    async def cleanup(self):
        """Clean up resources used by the compliance manager"""
        logger.info("Cleaned up compliance manager")


# Singleton instance
_instance = None

def get_compliance_manager(config: Optional[Dict[str, Any]] = None) -> ComplianceManager:
    """
    Get the singleton instance of the compliance manager
    
    Args:
        config: Configuration for the compliance manager (only used if creating a new instance)
        
    Returns:
        ComplianceManager instance
    """
    global _instance
    
    if _instance is None:
        if config is None:
            config = {}
        
        _instance = ComplianceManager(config)
    
    return _instance
