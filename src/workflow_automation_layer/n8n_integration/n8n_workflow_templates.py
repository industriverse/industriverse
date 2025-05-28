"""
n8n Workflow Templates Module for Industriverse Workflow Automation Layer

This module provides templates for common n8n workflows that integrate with Industriverse.
These templates can be used to quickly create workflows for common automation scenarios.
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any, Union

from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)


class WorkflowTemplate(BaseModel):
    """Model representing an n8n workflow template."""
    id: str
    name: str
    description: str
    category: str
    tags: List[str] = Field(default_factory=list)
    nodes: List[Dict[str, Any]]
    connections: Dict[str, Any]
    variables: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class N8nWorkflowTemplates:
    """
    Provides templates for common n8n workflows that integrate with Industriverse.
    
    This class loads workflow templates from JSON files and provides methods to
    retrieve and customize them for specific use cases.
    """
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the N8nWorkflowTemplates.
        
        Args:
            templates_dir: Optional directory containing workflow template JSON files
        """
        self.templates: Dict[str, WorkflowTemplate] = {}
        
        # Load built-in templates
        self._load_built_in_templates()
        
        # Load templates from directory if provided
        if templates_dir:
            self._load_templates_from_directory(templates_dir)
        
        logger.info(f"Loaded {len(self.templates)} n8n workflow templates")
    
    def _load_built_in_templates(self):
        """Load built-in workflow templates."""
        # Human Approval Workflow
        self.templates["human_approval"] = WorkflowTemplate(
            id="human_approval",
            name="Human Approval Workflow",
            description="Workflow for human approval of tasks or decisions",
            category="Human-in-the-Loop",
            tags=["approval", "human", "intervention"],
            nodes=[
                {
                    "id": "trigger",
                    "name": "Industriverse Trigger",
                    "type": "n8n-nodes-base.industriverseTrigger",
                    "parameters": {
                        "eventType": "human_intervention_required",
                        "authentication": True,
                        "authKey": "{{$env.INDUSTRIVERSE_AUTH_KEY}}"
                    },
                    "typeVersion": 1,
                    "position": [250, 300]
                },
                {
                    "id": "slack",
                    "name": "Slack",
                    "type": "n8n-nodes-base.slack",
                    "parameters": {
                        "operation": "sendMessage",
                        "channel": "{{$env.SLACK_APPROVAL_CHANNEL}}",
                        "text": "=Approval Required: {{$json.title}}\n\n{{$json.description}}\n\nWorkflow: {{$json.workflow_id}}\nTask: {{$json.task_id}}\nPriority: {{$json.priority}}\n\nClick here to respond: {{$env.APPROVAL_URL}}?id={{$json.intervention_id}}",
                        "otherOptions": {
                            "attachments": [
                                {
                                    "blocks": [
                                        {
                                            "type": "actions",
                                            "elements": [
                                                {
                                                    "type": "button",
                                                    "text": {
                                                        "type": "plain_text",
                                                        "text": "Approve"
                                                    },
                                                    "style": "primary",
                                                    "value": "approve",
                                                    "url": "{{$env.APPROVAL_URL}}?id={{$json.intervention_id}}&action=approve"
                                                },
                                                {
                                                    "type": "button",
                                                    "text": {
                                                        "type": "plain_text",
                                                        "text": "Reject"
                                                    },
                                                    "style": "danger",
                                                    "value": "reject",
                                                    "url": "{{$env.APPROVAL_URL}}?id={{$json.intervention_id}}&action=reject"
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    },
                    "typeVersion": 1,
                    "position": [450, 300]
                },
                {
                    "id": "webhook",
                    "name": "Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "parameters": {
                        "path": "approval/{{$json.intervention_id}}",
                        "responseMode": "lastNode",
                        "options": {
                            "responseHeaders": {
                                "entries": [
                                    {
                                        "name": "Content-Type",
                                        "value": "application/json"
                                    }
                                ]
                            }
                        }
                    },
                    "typeVersion": 1,
                    "position": [250, 500]
                },
                {
                    "id": "response",
                    "name": "Industriverse Response",
                    "type": "n8n-nodes-base.industriverseTriggerResponse",
                    "parameters": {
                        "interventionId": "={{$json.intervention_id}}",
                        "decision": "={{$json.action}}",
                        "comments": "={{$json.comments}}",
                        "responderId": "={{$json.user_id || 'n8n_user'}}",
                        "responseData": "={{$json.data || {}}}"
                    },
                    "typeVersion": 1,
                    "position": [450, 500]
                },
                {
                    "id": "confirmation",
                    "name": "Response Page",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "parameters": {
                        "options": {
                            "responseBody": "{\n  \"success\": true,\n  \"message\": \"Thank you for your response.\"\n}",
                            "responseCode": 200
                        }
                    },
                    "typeVersion": 1,
                    "position": [650, 500]
                }
            ],
            connections={
                "trigger": {
                    "main": [
                        [
                            {
                                "node": "slack",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "webhook": {
                    "main": [
                        [
                            {
                                "node": "response",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "response": {
                    "main": [
                        [
                            {
                                "node": "confirmation",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            },
            variables={
                "INDUSTRIVERSE_AUTH_KEY": "",
                "SLACK_APPROVAL_CHANNEL": "approvals",
                "APPROVAL_URL": "https://example.com/approve"
            }
        )
        
        # Data Processing Workflow
        self.templates["data_processing"] = WorkflowTemplate(
            id="data_processing",
            name="Data Processing Workflow",
            description="Workflow for processing data from external sources and sending to Industriverse",
            category="Data Integration",
            tags=["data", "processing", "integration"],
            nodes=[
                {
                    "id": "trigger",
                    "name": "Schedule Trigger",
                    "type": "n8n-nodes-base.scheduleTrigger",
                    "parameters": {
                        "interval": [
                            {
                                "field": "hours",
                                "value": 1
                            }
                        ]
                    },
                    "typeVersion": 1,
                    "position": [250, 300]
                },
                {
                    "id": "http",
                    "name": "HTTP Request",
                    "type": "n8n-nodes-base.httpRequest",
                    "parameters": {
                        "url": "={{$env.DATA_SOURCE_URL}}",
                        "method": "GET",
                        "authentication": "genericCredentialType",
                        "genericAuthType": "httpHeaderAuth",
                        "options": {}
                    },
                    "typeVersion": 1,
                    "position": [450, 300]
                },
                {
                    "id": "function",
                    "name": "Transform Data",
                    "type": "n8n-nodes-base.function",
                    "parameters": {
                        "functionCode": "// Transform the data to Industriverse format\nconst data = $input.all()[0].json;\n\n// Example transformation\nconst transformed = {\n  timestamp: new Date().toISOString(),\n  source: 'external_api',\n  data: data.results || data,\n  metadata: {\n    source_url: $env.DATA_SOURCE_URL,\n    record_count: Array.isArray(data.results) ? data.results.length : 1\n  }\n};\n\nreturn [{json: transformed}];"
                    },
                    "typeVersion": 1,
                    "position": [650, 300]
                },
                {
                    "id": "industriverse",
                    "name": "Trigger Industriverse Workflow",
                    "type": "n8n-nodes-base.industriverseTriggerWorkflow",
                    "parameters": {
                        "workflowId": "={{$env.INDUSTRIVERSE_WORKFLOW_ID}}",
                        "inputData": "={{$json}}",
                        "executionMode": "reactive",
                        "waitForCompletion": false
                    },
                    "typeVersion": 1,
                    "position": [850, 300]
                }
            ],
            connections={
                "trigger": {
                    "main": [
                        [
                            {
                                "node": "http",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "http": {
                    "main": [
                        [
                            {
                                "node": "function",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "function": {
                    "main": [
                        [
                            {
                                "node": "industriverse",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            },
            variables={
                "DATA_SOURCE_URL": "https://api.example.com/data",
                "INDUSTRIVERSE_WORKFLOW_ID": "data_processing_workflow"
            }
        )
        
        # Error Handling Workflow
        self.templates["error_handling"] = WorkflowTemplate(
            id="error_handling",
            name="Error Handling Workflow",
            description="Workflow for handling errors in Industriverse workflows",
            category="Error Handling",
            tags=["error", "handling", "monitoring"],
            nodes=[
                {
                    "id": "trigger",
                    "name": "Industriverse Trigger",
                    "type": "n8n-nodes-base.industriverseTrigger",
                    "parameters": {
                        "eventType": "human_intervention_required",
                        "authentication": True,
                        "authKey": "{{$env.INDUSTRIVERSE_AUTH_KEY}}",
                        "customEventName": "error"
                    },
                    "typeVersion": 1,
                    "position": [250, 300]
                },
                {
                    "id": "switch",
                    "name": "Error Type Switch",
                    "type": "n8n-nodes-base.switch",
                    "parameters": {
                        "dataType": "string",
                        "value1": "={{$json.context_data.error_type}}",
                        "rules": {
                            "rules": [
                                {
                                    "value2": "validation",
                                    "operation": "equal"
                                },
                                {
                                    "value2": "connection",
                                    "operation": "equal"
                                },
                                {
                                    "value2": "timeout",
                                    "operation": "equal"
                                }
                            ]
                        }
                    },
                    "typeVersion": 1,
                    "position": [450, 300]
                },
                {
                    "id": "validation",
                    "name": "Handle Validation Error",
                    "type": "n8n-nodes-base.function",
                    "parameters": {
                        "functionCode": "// Handle validation error\nconst error = $input.all()[0].json;\n\n// Log the error\nconsole.log('Validation error:', error);\n\n// Prepare response\nreturn [{\n  json: {\n    intervention_id: error.intervention_id,\n    action: 'reject',\n    comments: 'Validation error detected. Please check the input data.',\n    data: {\n      error_type: 'validation',\n      error_details: error.context_data.error_details,\n      suggested_fix: 'Review input data format and constraints.'\n    }\n  }\n}];"
                    },
                    "typeVersion": 1,
                    "position": [650, 200]
                },
                {
                    "id": "connection",
                    "name": "Handle Connection Error",
                    "type": "n8n-nodes-base.function",
                    "parameters": {
                        "functionCode": "// Handle connection error\nconst error = $input.all()[0].json;\n\n// Log the error\nconsole.log('Connection error:', error);\n\n// Prepare response\nreturn [{\n  json: {\n    intervention_id: error.intervention_id,\n    action: 'retry',\n    comments: 'Connection error detected. Will retry automatically.',\n    data: {\n      error_type: 'connection',\n      error_details: error.context_data.error_details,\n      retry_count: error.context_data.retry_count || 0,\n      max_retries: 3\n    }\n  }\n}];"
                    },
                    "typeVersion": 1,
                    "position": [650, 300]
                },
                {
                    "id": "timeout",
                    "name": "Handle Timeout Error",
                    "type": "n8n-nodes-base.function",
                    "parameters": {
                        "functionCode": "// Handle timeout error\nconst error = $input.all()[0].json;\n\n// Log the error\nconsole.log('Timeout error:', error);\n\n// Prepare response\nreturn [{\n  json: {\n    intervention_id: error.intervention_id,\n    action: 'escalate',\n    comments: 'Timeout error detected. Escalating to human operator.',\n    data: {\n      error_type: 'timeout',\n      error_details: error.context_data.error_details,\n      timeout_seconds: error.context_data.timeout_seconds\n    }\n  }\n}];"
                    },
                    "typeVersion": 1,
                    "position": [650, 400]
                },
                {
                    "id": "default",
                    "name": "Handle Other Error",
                    "type": "n8n-nodes-base.function",
                    "parameters": {
                        "functionCode": "// Handle other error types\nconst error = $input.all()[0].json;\n\n// Log the error\nconsole.log('Unknown error:', error);\n\n// Prepare response\nreturn [{\n  json: {\n    intervention_id: error.intervention_id,\n    action: 'escalate',\n    comments: 'Unknown error detected. Escalating to human operator.',\n    data: {\n      error_type: error.context_data.error_type || 'unknown',\n      error_details: error.context_data.error_details\n    }\n  }\n}];"
                    },
                    "typeVersion": 1,
                    "position": [650, 500]
                },
                {
                    "id": "response",
                    "name": "Industriverse Response",
                    "type": "n8n-nodes-base.industriverseTriggerResponse",
                    "parameters": {
                        "interventionId": "={{$json.intervention_id}}",
                        "decision": "={{$json.action}}",
                        "comments": "={{$json.comments}}",
                        "responderId": "error_handler",
                        "responseData": "={{$json.data}}"
                    },
                    "typeVersion": 1,
                    "position": [850, 300]
                },
                {
                    "id": "notification",
                    "name": "Send Notification",
                    "type": "n8n-nodes-base.slack",
                    "parameters": {
                        "operation": "sendMessage",
                        "channel": "{{$env.ERROR_NOTIFICATION_CHANNEL}}",
                        "text": "=Error in Industriverse workflow: {{$json.intervention_id}}\n\nType: {{$json.data.error_type}}\nDetails: {{$json.data.error_details}}\nAction: {{$json.action}}"
                    },
                    "typeVersion": 1,
                    "position": [1050, 300]
                }
            ],
            connections={
                "trigger": {
                    "main": [
                        [
                            {
                                "node": "switch",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "switch": {
                    "main": [
                        [
                            {
                                "node": "validation",
                                "type": "main",
                                "index": 0
                            }
                        ],
                        [
                            {
                                "node": "connection",
                                "type": "main",
                                "index": 0
                            }
                        ],
                        [
                            {
                                "node": "timeout",
                                "type": "main",
                                "index": 0
                            }
                        ],
                        [
                            {
                                "node": "default",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "validation": {
                    "main": [
                        [
                            {
                                "node": "response",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "connection": {
                    "main": [
                        [
                            {
                                "node": "response",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "timeout": {
                    "main": [
                        [
                            {
                                "node": "response",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "default": {
                    "main": [
                        [
                            {
                                "node": "response",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "response": {
                    "main": [
                        [
                            {
                                "node": "notification",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            },
            variables={
                "INDUSTRIVERSE_AUTH_KEY": "",
                "ERROR_NOTIFICATION_CHANNEL": "errors"
            }
        )
    
    def _load_templates_from_directory(self, templates_dir: str):
        """
        Load workflow templates from a directory.
        
        Args:
            templates_dir: Directory containing workflow template JSON files
        """
        if not os.path.isdir(templates_dir):
            logger.warning(f"Templates directory not found: {templates_dir}")
            return
        
        # Load each JSON file in the directory
        for filename in os.listdir(templates_dir):
            if not filename.endswith(".json"):
                continue
            
            file_path = os.path.join(templates_dir, filename)
            try:
                with open(file_path, "r") as f:
                    template_data = json.load(f)
                
                # Create template object
                template = WorkflowTemplate(**template_data)
                
                # Add to templates
                self.templates[template.id] = template
                
                logger.debug(f"Loaded template from {filename}: {template.name}")
            
            except Exception as e:
                logger.error(f"Failed to load template from {filename}: {e}")
    
    def get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """
        Get a workflow template by ID.
        
        Args:
            template_id: The ID of the template
            
        Returns:
            The workflow template if found, None otherwise
        """
        return self.templates.get(template_id)
    
    def list_templates(self, category: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        List all workflow templates, optionally filtered by category or tags.
        
        Args:
            category: Optional category to filter by
            tags: Optional list of tags to filter by
            
        Returns:
            A list of workflow templates
        """
        result = []
        
        for template_id, template in self.templates.items():
            # Apply filters
            if category and template.category != category:
                continue
            
            if tags and not all(tag in template.tags for tag in tags):
                continue
            
            # Add to result
            result.append({
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "tags": template.tags
            })
        
        return result
    
    def customize_template(self, template_id: str, variables: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Customize a workflow template with specific variables.
        
        Args:
            template_id: The ID of the template
            variables: Variables to customize the template with
            
        Returns:
            The customized workflow data if the template was found, None otherwise
        """
        template = self.get_template(template_id)
        if not template:
            return None
        
        # Create a copy of the template
        workflow_data = template.dict()
        
        # Replace variables in the workflow data
        workflow_data_str = json.dumps(workflow_data)
        
        for var_name, var_value in variables.items():
            # Replace {{$env.VAR_NAME}} with the actual value
            placeholder = f"{{{{$env.{var_name}}}}}"
            workflow_data_str = workflow_data_str.replace(placeholder, str(var_value))
        
        # Parse back to dict
        workflow_data = json.loads(workflow_data_str)
        
        return workflow_data
