"""
Security Orchestration Agent for the Security & Compliance Layer

This agent orchestrates security operations and responses across the Industriverse platform.
It coordinates security activities, automates responses, and manages security workflows.

Key capabilities:
1. Security workflow orchestration
2. Automated incident response
3. Security tool integration
4. Response playbook execution
5. Cross-layer security coordination

The Security Orchestration Agent enables comprehensive security orchestration and
automated response capabilities for the Industriverse platform.
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
import random
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SecurityOrchestrationAgent")

class SecurityOrchestrationAgent:
    """
    Security Orchestration Agent for orchestrating security operations and responses
    across the Industriverse platform.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Security Orchestration Agent.
        
        Args:
            config_path: Path to the configuration file
        """
        self.logger = logger
        self.config = self._load_config(config_path)
        self.playbooks = self._load_playbooks()
        self.integrations = self._load_integrations()
        self.active_workflows = {}
        self.workflow_history = []
        
        self.logger.info("Security Orchestration Agent initialized")
        
    def _load_config(self, config_path: str) -> Dict:
        """
        Load the agent configuration.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dict containing the configuration
        """
        default_config = {
            "workflow_timeout": 3600,  # seconds
            "max_concurrent_workflows": 100,
            "max_workflow_history": 1000,
            "default_severity_thresholds": {
                "critical": 90,
                "high": 70,
                "medium": 50,
                "low": 30
            },
            "auto_response": {
                "enabled": True,
                "max_severity": "high"  # Don't auto-respond to critical incidents
            },
            "integration": {
                "identity_provider": True,
                "access_control": True,
                "data_security": True,
                "protocol_security": True,
                "policy_governance": True,
                "threat_detection": True
            }
        }
        
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with default config
                    for key, value in loaded_config.items():
                        if isinstance(value, dict) and key in default_config:
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
                    
                self.logger.info(f"Configuration loaded from {config_path}")
            except Exception as e:
                self.logger.error(f"Error loading configuration: {str(e)}")
                self.logger.info("Using default configuration")
        
        return default_config
    
    def _load_playbooks(self) -> Dict:
        """
        Load security response playbooks.
        
        Returns:
            Dict containing playbooks
        """
        # In production, this would load from a database or configuration files
        # For now, we'll use a simple dictionary
        return {
            "malware_detection": {
                "name": "Malware Detection Response",
                "description": "Respond to malware detection alerts",
                "severity": "high",
                "triggers": ["threat_detection.malware", "endpoint.malware_alert"],
                "steps": [
                    {
                        "name": "isolate_host",
                        "action": "network.isolate_host",
                        "parameters": {"host_id": "{{event.host_id}}"},
                        "timeout": 60,
                        "on_failure": "notify_security_team"
                    },
                    {
                        "name": "scan_host",
                        "action": "endpoint.full_scan",
                        "parameters": {"host_id": "{{event.host_id}}", "scan_type": "deep"},
                        "timeout": 300,
                        "on_failure": "continue"
                    },
                    {
                        "name": "collect_forensics",
                        "action": "forensics.collect_data",
                        "parameters": {"host_id": "{{event.host_id}}", "data_types": ["memory", "files", "registry"]},
                        "timeout": 300,
                        "on_failure": "continue"
                    },
                    {
                        "name": "analyze_threat",
                        "action": "threat_intelligence.analyze",
                        "parameters": {"ioc": "{{event.ioc}}", "context": "{{event.context}}"},
                        "timeout": 120,
                        "on_failure": "continue"
                    },
                    {
                        "name": "remediate_threat",
                        "action": "endpoint.remediate",
                        "parameters": {"host_id": "{{event.host_id}}", "threat_id": "{{event.threat_id}}"},
                        "timeout": 180,
                        "on_failure": "notify_security_team"
                    },
                    {
                        "name": "verify_remediation",
                        "action": "endpoint.verify_clean",
                        "parameters": {"host_id": "{{event.host_id}}"},
                        "timeout": 120,
                        "on_failure": "notify_security_team"
                    },
                    {
                        "name": "restore_host",
                        "action": "network.restore_host",
                        "parameters": {"host_id": "{{event.host_id}}"},
                        "timeout": 60,
                        "on_failure": "notify_security_team"
                    },
                    {
                        "name": "update_ioc_database",
                        "action": "threat_intelligence.update_ioc",
                        "parameters": {"ioc": "{{event.ioc}}", "context": "{{event.context}}", "resolution": "{{workflow.resolution}}"},
                        "timeout": 60,
                        "on_failure": "continue"
                    }
                ]
            },
            "unauthorized_access": {
                "name": "Unauthorized Access Response",
                "description": "Respond to unauthorized access attempts",
                "severity": "high",
                "triggers": ["access_control.unauthorized_access", "identity_provider.suspicious_login"],
                "steps": [
                    {
                        "name": "lock_account",
                        "action": "identity.lock_account",
                        "parameters": {"user_id": "{{event.user_id}}"},
                        "timeout": 30,
                        "on_failure": "notify_security_team"
                    },
                    {
                        "name": "terminate_sessions",
                        "action": "identity.terminate_sessions",
                        "parameters": {"user_id": "{{event.user_id}}"},
                        "timeout": 60,
                        "on_failure": "continue"
                    },
                    {
                        "name": "check_user_activity",
                        "action": "audit.user_activity",
                        "parameters": {"user_id": "{{event.user_id}}", "time_range": "24h"},
                        "timeout": 120,
                        "on_failure": "continue"
                    },
                    {
                        "name": "check_authentication_logs",
                        "action": "audit.authentication_logs",
                        "parameters": {"user_id": "{{event.user_id}}", "time_range": "7d"},
                        "timeout": 120,
                        "on_failure": "continue"
                    },
                    {
                        "name": "analyze_risk",
                        "action": "risk.analyze_user",
                        "parameters": {"user_id": "{{event.user_id}}", "context": "{{event.context}}"},
                        "timeout": 60,
                        "on_failure": "continue"
                    },
                    {
                        "name": "notify_user",
                        "action": "notification.send",
                        "parameters": {"user_id": "{{event.user_id}}", "template": "account_locked", "channel": "email"},
                        "timeout": 30,
                        "on_failure": "continue"
                    },
                    {
                        "name": "create_incident",
                        "action": "incident.create",
                        "parameters": {"title": "Unauthorized Access - {{event.user_id}}", "severity": "{{event.severity}}", "details": "{{workflow.context}}"},
                        "timeout": 30,
                        "on_failure": "notify_security_team"
                    }
                ]
            },
            "data_exfiltration": {
                "name": "Data Exfiltration Response",
                "description": "Respond to potential data exfiltration",
                "severity": "critical",
                "triggers": ["data_security.exfiltration_alert", "network.data_transfer_anomaly"],
                "steps": [
                    {
                        "name": "block_traffic",
                        "action": "network.block_traffic",
                        "parameters": {"source_ip": "{{event.source_ip}}", "destination_ip": "{{event.destination_ip}}"},
                        "timeout": 30,
                        "on_failure": "notify_security_team"
                    },
                    {
                        "name": "isolate_host",
                        "action": "network.isolate_host",
                        "parameters": {"host_id": "{{event.host_id}}"},
                        "timeout": 60,
                        "on_failure": "notify_security_team"
                    },
                    {
                        "name": "capture_network_traffic",
                        "action": "network.capture_traffic",
                        "parameters": {"host_id": "{{event.host_id}}", "duration": 300},
                        "timeout": 360,
                        "on_failure": "continue"
                    },
                    {
                        "name": "collect_forensics",
                        "action": "forensics.collect_data",
                        "parameters": {"host_id": "{{event.host_id}}", "data_types": ["memory", "files", "network"]},
                        "timeout": 300,
                        "on_failure": "continue"
                    },
                    {
                        "name": "identify_data",
                        "action": "data_security.identify_data",
                        "parameters": {"transfer_id": "{{event.transfer_id}}"},
                        "timeout": 120,
                        "on_failure": "continue"
                    },
                    {
                        "name": "assess_impact",
                        "action": "risk.assess_data_loss",
                        "parameters": {"data_ids": "{{workflow.identified_data}}"},
                        "timeout": 120,
                        "on_failure": "continue"
                    },
                    {
                        "name": "create_incident",
                        "action": "incident.create",
                        "parameters": {"title": "Data Exfiltration - {{event.host_id}}", "severity": "critical", "details": "{{workflow.context}}"},
                        "timeout": 30,
                        "on_failure": "notify_security_team"
                    },
                    {
                        "name": "notify_data_owner",
                        "action": "notification.send",
                        "parameters": {"user_id": "{{workflow.data_owner}}", "template": "data_exfiltration", "channel": "email"},
                        "timeout": 30,
                        "on_failure": "continue"
                    }
                ]
            },
            "compliance_violation": {
                "name": "Compliance Violation Response",
                "description": "Respond to compliance policy violations",
                "severity": "medium",
                "triggers": ["policy_governance.compliance_violation", "access_control.policy_violation"],
                "steps": [
                    {
                        "name": "document_violation",
                        "action": "compliance.document_violation",
                        "parameters": {"policy_id": "{{event.policy_id}}", "violation_details": "{{event.details}}"},
                        "timeout": 30,
                        "on_failure": "notify_compliance_team"
                    },
                    {
                        "name": "assess_impact",
                        "action": "compliance.assess_impact",
                        "parameters": {"policy_id": "{{event.policy_id}}", "violation_details": "{{event.details}}"},
                        "timeout": 120,
                        "on_failure": "continue"
                    },
                    {
                        "name": "check_user_history",
                        "action": "audit.user_compliance_history",
                        "parameters": {"user_id": "{{event.user_id}}", "time_range": "90d"},
                        "timeout": 60,
                        "on_failure": "continue"
                    },
                    {
                        "name": "notify_user",
                        "action": "notification.send",
                        "parameters": {"user_id": "{{event.user_id}}", "template": "compliance_violation", "channel": "email"},
                        "timeout": 30,
                        "on_failure": "continue"
                    },
                    {
                        "name": "notify_manager",
                        "action": "notification.send",
                        "parameters": {"user_id": "{{workflow.manager_id}}", "template": "compliance_violation_report", "channel": "email"},
                        "timeout": 30,
                        "on_failure": "continue"
                    },
                    {
                        "name": "schedule_training",
                        "action": "compliance.schedule_training",
                        "parameters": {"user_id": "{{event.user_id}}", "policy_id": "{{event.policy_id}}"},
                        "timeout": 60,
                        "on_failure": "continue"
                    },
                    {
                        "name": "create_compliance_report",
                        "action": "compliance.create_report",
                        "parameters": {"violation_id": "{{workflow.violation_id}}", "resolution": "{{workflow.resolution}}"},
                        "timeout": 60,
                        "on_failure": "notify_compliance_team"
                    }
                ]
            }
        }
    
    def _load_integrations(self) -> Dict:
        """
        Load security tool integrations.
        
        Returns:
            Dict containing integrations
        """
        # In production, this would load from a configuration file or database
        # For now, we'll use a simple dictionary
        return {
            "network": {
                "actions": {
                    "isolate_host": {
                        "description": "Isolate a host from the network",
                        "parameters": ["host_id"],
                        "enabled": True
                    },
                    "restore_host": {
                        "description": "Restore network connectivity for a host",
                        "parameters": ["host_id"],
                        "enabled": True
                    },
                    "block_traffic": {
                        "description": "Block network traffic",
                        "parameters": ["source_ip", "destination_ip"],
                        "enabled": True
                    },
                    "capture_traffic": {
                        "description": "Capture network traffic",
                        "parameters": ["host_id", "duration"],
                        "enabled": True
                    }
                }
            },
            "endpoint": {
                "actions": {
                    "full_scan": {
                        "description": "Perform a full scan of an endpoint",
                        "parameters": ["host_id", "scan_type"],
                        "enabled": True
                    },
                    "remediate": {
                        "description": "Remediate a threat on an endpoint",
                        "parameters": ["host_id", "threat_id"],
                        "enabled": True
                    },
                    "verify_clean": {
                        "description": "Verify that an endpoint is clean",
                        "parameters": ["host_id"],
                        "enabled": True
                    }
                }
            },
            "identity": {
                "actions": {
                    "lock_account": {
                        "description": "Lock a user account",
                        "parameters": ["user_id"],
                        "enabled": True
                    },
                    "unlock_account": {
                        "description": "Unlock a user account",
                        "parameters": ["user_id"],
                        "enabled": True
                    },
                    "reset_password": {
                        "description": "Reset a user's password",
                        "parameters": ["user_id"],
                        "enabled": True
                    },
                    "terminate_sessions": {
                        "description": "Terminate all active sessions for a user",
                        "parameters": ["user_id"],
                        "enabled": True
                    }
                }
            },
            "forensics": {
                "actions": {
                    "collect_data": {
                        "description": "Collect forensic data from a host",
                        "parameters": ["host_id", "data_types"],
                        "enabled": True
                    },
                    "analyze_data": {
                        "description": "Analyze collected forensic data",
                        "parameters": ["collection_id"],
                        "enabled": True
                    }
                }
            },
            "threat_intelligence": {
                "actions": {
                    "analyze": {
                        "description": "Analyze an indicator of compromise",
                        "parameters": ["ioc", "context"],
                        "enabled": True
                    },
                    "update_ioc": {
                        "description": "Update the IOC database",
                        "parameters": ["ioc", "context", "resolution"],
                        "enabled": True
                    }
                }
            },
            "audit": {
                "actions": {
                    "user_activity": {
                        "description": "Get user activity logs",
                        "parameters": ["user_id", "time_range"],
                        "enabled": True
                    },
                    "authentication_logs": {
                        "description": "Get authentication logs",
                        "parameters": ["user_id", "time_range"],
                        "enabled": True
                    },
                    "user_compliance_history": {
                        "description": "Get user compliance history",
                        "parameters": ["user_id", "time_range"],
                        "enabled": True
                    }
                }
            },
            "notification": {
                "actions": {
                    "send": {
                        "description": "Send a notification",
                        "parameters": ["user_id", "template", "channel"],
                        "enabled": True
                    }
                }
            },
            "incident": {
                "actions": {
                    "create": {
                        "description": "Create a security incident",
                        "parameters": ["title", "severity", "details"],
                        "enabled": True
                    },
                    "update": {
                        "description": "Update a security incident",
                        "parameters": ["incident_id", "updates"],
                        "enabled": True
                    },
                    "close": {
                        "description": "Close a security incident",
                        "parameters": ["incident_id", "resolution"],
                        "enabled": True
                    }
                }
            },
            "compliance": {
                "actions": {
                    "document_violation": {
                        "description": "Document a compliance violation",
                        "parameters": ["policy_id", "violation_details"],
                        "enabled": True
                    },
                    "assess_impact": {
                        "description": "Assess the impact of a compliance violation",
                        "parameters": ["policy_id", "violation_details"],
                        "enabled": True
                    },
                    "schedule_training": {
                        "description": "Schedule compliance training for a user",
                        "parameters": ["user_id", "policy_id"],
                        "enabled": True
                    },
                    "create_report": {
                        "description": "Create a compliance report",
                        "parameters": ["violation_id", "resolution"],
                        "enabled": True
                    }
                }
            },
            "risk": {
                "actions": {
                    "analyze_user": {
                        "description": "Analyze user risk",
                        "parameters": ["user_id", "context"],
                        "enabled": True
                    },
                    "assess_data_loss": {
                        "description": "Assess the impact of data loss",
                        "parameters": ["data_ids"],
                        "enabled": True
                    }
                }
            },
            "data_security": {
                "actions": {
                    "identify_data": {
                        "description": "Identify data involved in a transfer",
                        "parameters": ["transfer_id"],
                        "enabled": True
                    },
                    "classify_data": {
                        "description": "Classify data sensitivity",
                        "parameters": ["data_id"],
                        "enabled": True
                    }
                }
            }
        }
    
    def start_workflow(self, trigger: str, event: Dict) -> Dict:
        """
        Start a security workflow based on a trigger event.
        
        Args:
            trigger: Workflow trigger
            event: Event data
            
        Returns:
            Dict containing workflow status
        """
        self.logger.info(f"Starting workflow for trigger: {trigger}")
        
        # Find matching playbooks
        matching_playbooks = []
        
        for playbook_id, playbook in self.playbooks.items():
            if trigger in playbook["triggers"]:
                matching_playbooks.append((playbook_id, playbook))
        
        if not matching_playbooks:
            return {
                "status": "error",
                "message": f"No playbooks found for trigger: {trigger}",
                "timestamp": datetime.now().isoformat()
            }
        
        # Check if auto-response is enabled
        if not self.config["auto_response"]["enabled"]:
            return {
                "status": "error",
                "message": "Automated response is disabled",
                "timestamp": datetime.now().isoformat()
            }
        
        # Sort playbooks by severity (highest first)
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        matching_playbooks.sort(key=lambda p: severity_order.get(p[1]["severity"], 0), reverse=True)
        
        # Select the highest severity playbook
        playbook_id, playbook = matching_playbooks[0]
        
        # Check if playbook severity exceeds auto-response threshold
        if severity_order.get(playbook["severity"], 0) > severity_order.get(self.config["auto_response"]["max_severity"], 0):
            return {
                "status": "error",
                "message": f"Playbook severity ({playbook['severity']}) exceeds auto-response threshold ({self.config['auto_response']['max_severity']})",
                "timestamp": datetime.now().isoformat()
            }
        
        # Check if we've reached the maximum number of concurrent workflows
        if len(self.active_workflows) >= self.config["max_concurrent_workflows"]:
            return {
                "status": "error",
                "message": f"Maximum number of concurrent workflows reached ({self.config['max_concurrent_workflows']})",
                "timestamp": datetime.now().isoformat()
            }
        
        # Create workflow
        workflow_id = str(uuid.uuid4())
        
        workflow = {
            "id": workflow_id,
            "playbook_id": playbook_id,
            "trigger": trigger,
            "event": event,
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "timeout": datetime.now().timestamp() + self.config["workflow_timeout"],
            "current_step": 0,
            "steps": playbook["steps"],
            "step_results": [],
            "context": {},
            "errors": []
        }
        
        # Add to active workflows
        self.active_workflows[workflow_id] = workflow
        
        # Start executing the workflow
        self._execute_workflow_step(workflow_id)
        
        return {
            "status": "success",
            "workflow_id": workflow_id,
            "playbook_id": playbook_id,
            "playbook_name": playbook["name"],
            "trigger": trigger,
            "timestamp": datetime.now().isoformat()
        }
    
    def _execute_workflow_step(self, workflow_id: str) -> Dict:
        """
        Execute the current step of a workflow.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Dict containing step execution result
        """
        if workflow_id not in self.active_workflows:
            return {
                "status": "error",
                "message": f"Unknown workflow ID: {workflow_id}",
                "timestamp": datetime.now().isoformat()
            }
        
        workflow = self.active_workflows[workflow_id]
        
        # Check if workflow has timed out
        if datetime.now().timestamp() > workflow["timeout"]:
            workflow["status"] = "timeout"
            workflow["end_time"] = datetime.now().isoformat()
            workflow["errors"].append({
                "step": workflow["current_step"],
                "message": "Workflow timed out",
                "timestamp": datetime.now().isoformat()
            })
            
            # Move to history
            self._complete_workflow(workflow_id)
            
            return {
                "status": "error",
                "message": "Workflow timed out",
                "timestamp": datetime.now().isoformat()
            }
        
        # Check if we've completed all steps
        if workflow["current_step"] >= len(workflow["steps"]):
            workflow["status"] = "completed"
            workflow["end_time"] = datetime.now().isoformat()
            
            # Move to history
            self._complete_workflow(workflow_id)
            
            return {
                "status": "success",
                "message": "Workflow completed successfully",
                "timestamp": datetime.now().isoformat()
            }
        
        # Get current step
        step = workflow["steps"][workflow["current_step"]]
        step_name = step["name"]
        action = step["action"]
        parameters = step["parameters"]
        timeout = step.get("timeout", 60)
        on_failure = step.get("on_failure", "fail")
        
        # Resolve parameter templates
        resolved_parameters = {}
        
        for param_name, param_value in parameters.items():
            if isinstance(param_value, str) and "{{" in param_value and "}}" in param_value:
                resolved_parameters[param_name] = self._resolve_template(param_value, workflow)
            else:
                resolved_parameters[param_name] = param_value
        
        # Check if action is available
        action_category, action_name = action.split(".")
        
        if action_category not in self.integrations:
            workflow["errors"].append({
                "step": workflow["current_step"],
                "message": f"Unknown action category: {action_category}",
                "timestamp": datetime.now().isoformat()
            })
            
            return self._handle_step_failure(workflow_id, on_failure)
        
        if action_name not in self.integrations[action_category]["actions"]:
            workflow["errors"].append({
                "step": workflow["current_step"],
                "message": f"Unknown action: {action}",
                "timestamp": datetime.now().isoformat()
            })
            
            return self._handle_step_failure(workflow_id, on_failure)
        
        action_config = self.integrations[action_category]["actions"][action_name]
        
        if not action_config["enabled"]:
            workflow["errors"].append({
                "step": workflow["current_step"],
                "message": f"Action is disabled: {action}",
                "timestamp": datetime.now().isoformat()
            })
            
            return self._handle_step_failure(workflow_id, on_failure)
        
        # Check if all required parameters are provided
        for param in action_config["parameters"]:
            if param not in resolved_parameters:
                workflow["errors"].append({
                    "step": workflow["current_step"],
                    "message": f"Missing required parameter: {param}",
                    "timestamp": datetime.now().isoformat()
                })
                
                return self._handle_step_failure(workflow_id, on_failure)
        
        # Execute the action
        self.logger.info(f"Executing workflow step: {step_name} ({action})")
        
        # In a real implementation, this would call the actual integration
        # For now, we'll simulate the action execution
        result = self._simulate_action_execution(action_category, action_name, resolved_parameters)
        
        # Record step result
        workflow["step_results"].append({
            "step": workflow["current_step"],
            "name": step_name,
            "action": action,
            "parameters": resolved_parameters,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update workflow context with step result
        workflow["context"][step_name] = result
        
        # Check if step was successful
        if result["status"] == "success":
            # Move to next step
            workflow["current_step"] += 1
            
            # Execute next step
            return self._execute_workflow_step(workflow_id)
        else:
            # Handle step failure
            workflow["errors"].append({
                "step": workflow["current_step"],
                "message": f"Step failed: {result['message']}",
                "timestamp": datetime.now().isoformat()
            })
            
            return self._handle_step_failure(workflow_id, on_failure)
    
    def _resolve_template(self, template: str, workflow: Dict) -> str:
        """
        Resolve a template string using workflow data.
        
        Args:
            template: Template string
            workflow: Workflow data
            
        Returns:
            Resolved string
        """
        result = template
        
        # Replace event variables
        event_vars = re.findall(r"{{event\.([^}]+)}}", template)
        for var in event_vars:
            if var in workflow["event"]:
                result = result.replace(f"{{{{event.{var}}}}}", str(workflow["event"][var]))
        
        # Replace workflow context variables
        context_vars = re.findall(r"{{workflow\.([^}]+)}}", template)
        for var in context_vars:
            if var in workflow["context"]:
                result = result.replace(f"{{{{workflow.{var}}}}}", str(workflow["context"][var]))
        
        return result
    
    def _handle_step_failure(self, workflow_id: str, on_failure: str) -> Dict:
        """
        Handle a workflow step failure.
        
        Args:
            workflow_id: Workflow ID
            on_failure: Failure handling strategy
            
        Returns:
            Dict containing failure handling result
        """
        workflow = self.active_workflows[workflow_id]
        
        if on_failure == "fail":
            # Fail the workflow
            workflow["status"] = "failed"
            workflow["end_time"] = datetime.now().isoformat()
            
            # Move to history
            self._complete_workflow(workflow_id)
            
            return {
                "status": "error",
                "message": "Workflow failed",
                "timestamp": datetime.now().isoformat()
            }
        
        elif on_failure == "continue":
            # Continue to next step
            workflow["current_step"] += 1
            
            # Execute next step
            return self._execute_workflow_step(workflow_id)
        
        elif on_failure == "notify_security_team":
            # Notify security team and continue
            self._simulate_notification("security_team", f"Workflow step failed: {workflow_id}", workflow["errors"][-1])
            
            # Continue to next step
            workflow["current_step"] += 1
            
            # Execute next step
            return self._execute_workflow_step(workflow_id)
        
        elif on_failure == "notify_compliance_team":
            # Notify compliance team and continue
            self._simulate_notification("compliance_team", f"Workflow step failed: {workflow_id}", workflow["errors"][-1])
            
            # Continue to next step
            workflow["current_step"] += 1
            
            # Execute next step
            return self._execute_workflow_step(workflow_id)
        
        else:
            # Unknown on_failure strategy, fail the workflow
            workflow["status"] = "failed"
            workflow["end_time"] = datetime.now().isoformat()
            workflow["errors"].append({
                "step": workflow["current_step"],
                "message": f"Unknown on_failure strategy: {on_failure}",
                "timestamp": datetime.now().isoformat()
            })
            
            # Move to history
            self._complete_workflow(workflow_id)
            
            return {
                "status": "error",
                "message": "Workflow failed",
                "timestamp": datetime.now().isoformat()
            }
    
    def _simulate_action_execution(self, category: str, action: str, parameters: Dict) -> Dict:
        """
        Simulate the execution of an integration action.
        
        Args:
            category: Action category
            action: Action name
            parameters: Action parameters
            
        Returns:
            Dict containing action execution result
        """
        # In a real implementation, this would call the actual integration
        # For now, we'll simulate the action execution with a high success rate
        success = random.random() < 0.9  # 90% success rate
        
        if success:
            result = {
                "status": "success",
                "message": f"Action {category}.{action} executed successfully",
                "timestamp": datetime.now().isoformat()
            }
            
            # Add action-specific result data
            if category == "network" and action == "isolate_host":
                result["host_id"] = parameters["host_id"]
                result["isolation_status"] = "isolated"
            
            elif category == "endpoint" and action == "full_scan":
                result["host_id"] = parameters["host_id"]
                result["scan_id"] = f"scan-{hashlib.md5(datetime.now().isoformat().encode()).hexdigest()[:8]}"
                result["threats_found"] = random.randint(0, 3)
            
            elif category == "forensics" and action == "collect_data":
                result["host_id"] = parameters["host_id"]
                result["collection_id"] = f"collection-{hashlib.md5(datetime.now().isoformat().encode()).hexdigest()[:8]}"
                result["data_size"] = f"{random.randint(100, 1000)} MB"
            
            elif category == "threat_intelligence" and action == "analyze":
                result["ioc"] = parameters["ioc"]
                result["threat_score"] = random.randint(1, 100)
                result["threat_type"] = random.choice(["malware", "phishing", "command_and_control", "ransomware"])
            
            elif category == "data_security" and action == "identify_data":
                result["transfer_id"] = parameters["transfer_id"]
                result["data_ids"] = [f"data-{random.randint(1000, 9999)}" for _ in range(random.randint(1, 5))]
                result["data_types"] = random.choice([["PII"], ["financial"], ["intellectual_property"], ["PII", "financial"]])
            
            elif category == "risk" and action == "assess_data_loss":
                result["data_ids"] = parameters["data_ids"]
                result["risk_score"] = random.randint(1, 100)
                result["potential_impact"] = random.choice(["low", "medium", "high", "critical"])
            
            elif category == "incident" and action == "create":
                result["title"] = parameters["title"]
                result["severity"] = parameters["severity"]
                result["incident_id"] = f"incident-{hashlib.md5(datetime.now().isoformat().encode()).hexdigest()[:8]}"
            
        else:
            result = {
                "status": "error",
                "message": f"Action {category}.{action} failed: Simulated failure",
                "timestamp": datetime.now().isoformat()
            }
        
        return result
    
    def _simulate_notification(self, recipient: str, subject: str, content: Any):
        """
        Simulate sending a notification.
        
        Args:
            recipient: Notification recipient
            subject: Notification subject
            content: Notification content
        """
        self.logger.info(f"Simulated notification to {recipient}: {subject}")
    
    def _complete_workflow(self, workflow_id: str):
        """
        Complete a workflow and move it to history.
        
        Args:
            workflow_id: Workflow ID
        """
        if workflow_id not in self.active_workflows:
            return
        
        workflow = self.active_workflows[workflow_id]
        
        # Add to history
        self.workflow_history.append(workflow)
        
        # Trim history if it exceeds the maximum size
        if len(self.workflow_history) > self.config["max_workflow_history"]:
            self.workflow_history = self.workflow_history[-self.config["max_workflow_history"]:]
        
        # Remove from active workflows
        del self.active_workflows[workflow_id]
        
        self.logger.info(f"Completed workflow {workflow_id} with status {workflow['status']}")
    
    def get_workflow_status(self, workflow_id: str) -> Dict:
        """
        Get the status of a workflow.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Dict containing workflow status
        """
        # Check active workflows
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            
            return {
                "status": "success",
                "workflow_id": workflow_id,
                "workflow_status": workflow["status"],
                "playbook_id": workflow["playbook_id"],
                "trigger": workflow["trigger"],
                "current_step": workflow["current_step"],
                "total_steps": len(workflow["steps"]),
                "start_time": workflow["start_time"],
                "errors": len(workflow["errors"]),
                "timestamp": datetime.now().isoformat()
            }
        
        # Check workflow history
        for workflow in self.workflow_history:
            if workflow["id"] == workflow_id:
                return {
                    "status": "success",
                    "workflow_id": workflow_id,
                    "workflow_status": workflow["status"],
                    "playbook_id": workflow["playbook_id"],
                    "trigger": workflow["trigger"],
                    "current_step": workflow["current_step"],
                    "total_steps": len(workflow["steps"]),
                    "start_time": workflow["start_time"],
                    "end_time": workflow["end_time"],
                    "errors": len(workflow["errors"]),
                    "timestamp": datetime.now().isoformat()
                }
        
        return {
            "status": "error",
            "message": f"Unknown workflow ID: {workflow_id}",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_workflow_details(self, workflow_id: str) -> Dict:
        """
        Get detailed information about a workflow.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Dict containing workflow details
        """
        # Check active workflows
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            
            return {
                "status": "success",
                "workflow_id": workflow_id,
                "workflow": workflow,
                "timestamp": datetime.now().isoformat()
            }
        
        # Check workflow history
        for workflow in self.workflow_history:
            if workflow["id"] == workflow_id:
                return {
                    "status": "success",
                    "workflow_id": workflow_id,
                    "workflow": workflow,
                    "timestamp": datetime.now().isoformat()
                }
        
        return {
            "status": "error",
            "message": f"Unknown workflow ID: {workflow_id}",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_active_workflows(self) -> Dict:
        """
        Get all active workflows.
        
        Returns:
            Dict containing active workflows
        """
        active_workflow_summaries = []
        
        for workflow_id, workflow in self.active_workflows.items():
            active_workflow_summaries.append({
                "workflow_id": workflow_id,
                "playbook_id": workflow["playbook_id"],
                "trigger": workflow["trigger"],
                "status": workflow["status"],
                "current_step": workflow["current_step"],
                "total_steps": len(workflow["steps"]),
                "start_time": workflow["start_time"]
            })
        
        return {
            "status": "success",
            "count": len(active_workflow_summaries),
            "workflows": active_workflow_summaries,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_workflow_history(self, limit: int = None, status: str = None, 
                            playbook_id: str = None) -> Dict:
        """
        Get workflow history.
        
        Args:
            limit: Maximum number of workflows to return
            status: Filter by workflow status
            playbook_id: Filter by playbook ID
            
        Returns:
            Dict containing workflow history
        """
        filtered_history = self.workflow_history
        
        if status:
            filtered_history = [w for w in filtered_history if w["status"] == status]
        
        if playbook_id:
            filtered_history = [w for w in filtered_history if w["playbook_id"] == playbook_id]
        
        # Sort by start time (newest first)
        filtered_history = sorted(
            filtered_history,
            key=lambda w: datetime.fromisoformat(w["start_time"]).timestamp(),
            reverse=True
        )
        
        if limit:
            filtered_history = filtered_history[:limit]
        
        # Create summaries
        workflow_summaries = []
        
        for workflow in filtered_history:
            workflow_summaries.append({
                "workflow_id": workflow["id"],
                "playbook_id": workflow["playbook_id"],
                "trigger": workflow["trigger"],
                "status": workflow["status"],
                "current_step": workflow["current_step"],
                "total_steps": len(workflow["steps"]),
                "start_time": workflow["start_time"],
                "end_time": workflow["end_time"],
                "errors": len(workflow["errors"])
            })
        
        return {
            "status": "success",
            "count": len(workflow_summaries),
            "workflows": workflow_summaries,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_available_playbooks(self) -> Dict:
        """
        Get all available playbooks.
        
        Returns:
            Dict containing available playbooks
        """
        playbook_summaries = []
        
        for playbook_id, playbook in self.playbooks.items():
            playbook_summaries.append({
                "id": playbook_id,
                "name": playbook["name"],
                "description": playbook["description"],
                "severity": playbook["severity"],
                "triggers": playbook["triggers"],
                "steps": len(playbook["steps"])
            })
        
        return {
            "status": "success",
            "count": len(playbook_summaries),
            "playbooks": playbook_summaries,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_available_integrations(self) -> Dict:
        """
        Get all available integrations.
        
        Returns:
            Dict containing available integrations
        """
        integration_summaries = []
        
        for integration_id, integration in self.integrations.items():
            actions = []
            
            for action_id, action in integration["actions"].items():
                actions.append({
                    "id": action_id,
                    "description": action["description"],
                    "parameters": action["parameters"],
                    "enabled": action["enabled"]
                })
            
            integration_summaries.append({
                "id": integration_id,
                "actions": actions
            })
        
        return {
            "status": "success",
            "count": len(integration_summaries),
            "integrations": integration_summaries,
            "timestamp": datetime.now().isoformat()
        }

# Example usage
if __name__ == "__main__":
    agent = SecurityOrchestrationAgent()
    
    # Start a workflow
    event = {
        "host_id": "host-123",
        "threat_id": "threat-456",
        "ioc": "malware-hash-789",
        "severity": "high",
        "context": {
            "detection_source": "endpoint",
            "detection_time": datetime.now().isoformat()
        }
    }
    
    workflow = agent.start_workflow("threat_detection.malware", event)
    print(f"Started workflow: {workflow}")
    
    # Get workflow status
    if workflow["status"] == "success":
        status = agent.get_workflow_status(workflow["workflow_id"])
        print(f"Workflow status: {status}")
        
        # Get workflow details
        details = agent.get_workflow_details(workflow["workflow_id"])
        print(f"Workflow details: {details}")
    
    # Get active workflows
    active = agent.get_active_workflows()
    print(f"Active workflows: {active}")
    
    # Get available playbooks
    playbooks = agent.get_available_playbooks()
    print(f"Available playbooks: {playbooks}")
    
    # Get available integrations
    integrations = agent.get_available_integrations()
    print(f"Available integrations: {integrations}")
