"""
n8n Adapter Agent Module for the Workflow Automation Layer.

This agent acts as a dedicated adapter for interacting with the n8n instance,
translating Industriverse workflow tasks into n8n workflows and vice versa.
It handles authentication, API calls, and data mapping between the two systems.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

import requests  # Assuming requests library is available for HTTP calls

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class N8nAdapterAgent:
    """Agent for adapting Industriverse workflows to n8n."""

    def __init__(self, workflow_runtime, n8n_config: Dict[str, Any]):
        """Initialize the n8n adapter agent.

        Args:
            workflow_runtime: The workflow runtime instance.
            n8n_config: Configuration for connecting to n8n (url, api_key).
        """
        self.workflow_runtime = workflow_runtime
        self.agent_id = "n8n-adapter-agent"
        self.agent_capabilities = ["n8n_integration", "workflow_translation", "api_interaction"]
        self.supported_protocols = ["MCP", "A2A"]
        self.n8n_url = n8n_config.get("url")
        self.n8n_api_key = n8n_config.get("api_key")
        self.active_n8n_workflows = {}  # Store for active n8n workflows linked to Industriverse
        self.translation_cache = {}  # Cache for translated workflow snippets
        
        if not self.n8n_url or not self.n8n_api_key:
            logger.error("n8n URL or API key not provided in config")
            raise ValueError("n8n URL and API key are required")
            
        logger.info(f"n8n Adapter Agent initialized for n8n instance at {self.n8n_url}")

    def _get_n8n_headers(self) -> Dict[str, str]:
        """Get headers for n8n API requests."""
        return {
            "Accept": "application/json",
            "X-N8N-API-KEY": self.n8n_api_key,
            "Content-Type": "application/json"
        }

    async def translate_to_n8n(self, industriverse_task: Dict[str, Any]) -> Dict[str, Any]:
        """Translate an Industriverse task into an n8n workflow snippet.

        Args:
            industriverse_task: The Industriverse task manifest.

        Returns:
            Dict containing the n8n workflow snippet or error.
        """
        try:
            task_id = industriverse_task.get("task_id")
            task_type = industriverse_task.get("task_type")
            parameters = industriverse_task.get("parameters", {})
            
            # Check cache first
            cache_key = f"{task_id}-{task_type}-{json.dumps(parameters, sort_keys=True)}"
            if cache_key in self.translation_cache:
                return {
                    "success": True,
                    "n8n_snippet": self.translation_cache[cache_key]
                }
            
            # Basic translation logic (highly simplified)
            # In a real implementation, this would involve complex mapping based on task_type
            n8n_nodes = []
            n8n_connections = {}
            
            # Example: Create a simple webhook trigger and HTTP request node
            if task_type == "http_request":
                webhook_node_id = str(uuid.uuid4())
                http_node_id = str(uuid.uuid4())
                
                n8n_nodes.append({
                    "parameters": {
                        "httpMethod": "POST",
                        "path": f"webhook/{task_id}",
                        "responseMode": "onReceived",
                        "options": {}
                    },
                    "name": f"Webhook Trigger for {task_id}",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [800, 300],
                    "id": webhook_node_id
                })
                
                n8n_nodes.append({
                    "parameters": {
                        "url": parameters.get("url"),
                        "method": parameters.get("method", "GET"),
                        "sendHeaders": True,
                        "headerParameters": {
                            "parameters": parameters.get("headers", [])
                        },
                        "sendBody": parameters.get("method", "GET") in ["POST", "PUT", "PATCH"],
                        "specifyBody": "json",
                        "jsonBody": json.dumps(parameters.get("body", {})),
                        "options": {}
                    },
                    "name": f"HTTP Request for {task_id}",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 1,
                    "position": [1000, 300],
                    "id": http_node_id
                })
                
                n8n_connections = {
                    webhook_node_id: {
                        "main": [
                            [{"node": http_node_id, "type": "main", "index": 0}]
                        ]
                    }
                }
            else:
                # Default: Create a simple start node
                start_node_id = str(uuid.uuid4())
                n8n_nodes.append({
                    "parameters": {},
                    "name": f"Start Node for {task_id}",
                    "type": "n8n-nodes-base.start",
                    "typeVersion": 1,
                    "position": [800, 300],
                    "id": start_node_id
                })
            
            n8n_snippet = {
                "nodes": n8n_nodes,
                "connections": n8n_connections
            }
            
            # Cache the result
            self.translation_cache[cache_key] = n8n_snippet
            
            return {
                "success": True,
                "n8n_snippet": n8n_snippet
            }
            
        except Exception as e:
            logger.error(f"Error translating task {task_id} to n8n: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def create_n8n_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow in n8n.

        Args:
            workflow_data: Data for the n8n workflow (nodes, connections, name, etc.).

        Returns:
            Dict containing the created n8n workflow ID or error.
        """
        try:
            api_url = f"{self.n8n_url}/api/v1/workflows"
            headers = self._get_n8n_headers()
            
            payload = {
                "name": workflow_data.get("name", "Industriverse Workflow"),
                "nodes": workflow_data.get("nodes", []),
                "connections": workflow_data.get("connections", {}),
                "active": workflow_data.get("active", False),
                "settings": workflow_data.get("settings", {}),
                "tags": workflow_data.get("tags", [])
            }
            
            response = await asyncio.to_thread(
                requests.post, api_url, headers=headers, json=payload
            )
            response.raise_for_status()  # Raise exception for bad status codes
            
            result = response.json()
            n8n_workflow_id = result.get("id")
            
            if not n8n_workflow_id:
                return {
                    "success": False,
                    "error": "n8n API did not return workflow ID"
                }
            
            # Store mapping
            industriverse_workflow_id = workflow_data.get("industriverse_workflow_id")
            if industriverse_workflow_id:
                self.active_n8n_workflows[n8n_workflow_id] = {
                    "industriverse_workflow_id": industriverse_workflow_id,
                    "name": payload["name"],
                    "created_at": datetime.utcnow().isoformat()
                }
            
            logger.info(f"Created n8n workflow {n8n_workflow_id} for Industriverse workflow {industriverse_workflow_id}")
            
            return {
                "success": True,
                "n8n_workflow_id": n8n_workflow_id
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating n8n workflow (HTTP Error): {str(e)}")
            return {"success": False, "error": f"HTTP Error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error creating n8n workflow: {str(e)}")
            return {"success": False, "error": str(e)}

    async def update_n8n_workflow(self, n8n_workflow_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing workflow in n8n.

        Args:
            n8n_workflow_id: ID of the n8n workflow to update.
            workflow_data: Updated data for the n8n workflow.

        Returns:
            Dict containing update status.
        """
        try:
            api_url = f"{self.n8n_url}/api/v1/workflows/{n8n_workflow_id}"
            headers = self._get_n8n_headers()
            
            payload = {
                "name": workflow_data.get("name"),
                "nodes": workflow_data.get("nodes"),
                "connections": workflow_data.get("connections"),
                "active": workflow_data.get("active"),
                "settings": workflow_data.get("settings"),
                "tags": workflow_data.get("tags")
            }
            
            # Remove None values
            payload = {k: v for k, v in payload.items() if v is not None}
            
            response = await asyncio.to_thread(
                requests.put, api_url, headers=headers, json=payload
            )
            response.raise_for_status()
            
            logger.info(f"Updated n8n workflow {n8n_workflow_id}")
            
            return {"success": True}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating n8n workflow {n8n_workflow_id} (HTTP Error): {str(e)}")
            return {"success": False, "error": f"HTTP Error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error updating n8n workflow {n8n_workflow_id}: {str(e)}")
            return {"success": False, "error": str(e)}

    async def activate_n8n_workflow(self, n8n_workflow_id: str) -> Dict[str, Any]:
        """Activate an n8n workflow.

        Args:
            n8n_workflow_id: ID of the n8n workflow to activate.

        Returns:
            Dict containing activation status.
        """
        try:
            api_url = f"{self.n8n_url}/api/v1/workflows/{n8n_workflow_id}/activate"
            headers = self._get_n8n_headers()
            
            response = await asyncio.to_thread(
                requests.post, api_url, headers=headers
            )
            response.raise_for_status()
            
            logger.info(f"Activated n8n workflow {n8n_workflow_id}")
            
            return {"success": True}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error activating n8n workflow {n8n_workflow_id} (HTTP Error): {str(e)}")
            return {"success": False, "error": f"HTTP Error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error activating n8n workflow {n8n_workflow_id}: {str(e)}")
            return {"success": False, "error": str(e)}

    async def deactivate_n8n_workflow(self, n8n_workflow_id: str) -> Dict[str, Any]:
        """Deactivate an n8n workflow.

        Args:
            n8n_workflow_id: ID of the n8n workflow to deactivate.

        Returns:
            Dict containing deactivation status.
        """
        try:
            api_url = f"{self.n8n_url}/api/v1/workflows/{n8n_workflow_id}/deactivate"
            headers = self._get_n8n_headers()
            
            response = await asyncio.to_thread(
                requests.post, api_url, headers=headers
            )
            response.raise_for_status()
            
            logger.info(f"Deactivated n8n workflow {n8n_workflow_id}")
            
            return {"success": True}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deactivating n8n workflow {n8n_workflow_id} (HTTP Error): {str(e)}")
            return {"success": False, "error": f"HTTP Error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error deactivating n8n workflow {n8n_workflow_id}: {str(e)}")
            return {"success": False, "error": str(e)}

    async def delete_n8n_workflow(self, n8n_workflow_id: str) -> Dict[str, Any]:
        """Delete an n8n workflow.

        Args:
            n8n_workflow_id: ID of the n8n workflow to delete.

        Returns:
            Dict containing deletion status.
        """
        try:
            api_url = f"{self.n8n_url}/api/v1/workflows/{n8n_workflow_id}"
            headers = self._get_n8n_headers()
            
            response = await asyncio.to_thread(
                requests.delete, api_url, headers=headers
            )
            response.raise_for_status()
            
            # Remove from active mapping
            if n8n_workflow_id in self.active_n8n_workflows:
                del self.active_n8n_workflows[n8n_workflow_id]
            
            logger.info(f"Deleted n8n workflow {n8n_workflow_id}")
            
            return {"success": True}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting n8n workflow {n8n_workflow_id} (HTTP Error): {str(e)}")
            return {"success": False, "error": f"HTTP Error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error deleting n8n workflow {n8n_workflow_id}: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_n8n_workflow_status(self, n8n_workflow_id: str) -> Dict[str, Any]:
        """Get the status of an n8n workflow.

        Args:
            n8n_workflow_id: ID of the n8n workflow.

        Returns:
            Dict containing workflow status or error.
        """
        try:
            api_url = f"{self.n8n_url}/api/v1/workflows/{n8n_workflow_id}"
            headers = self._get_n8n_headers()
            
            response = await asyncio.to_thread(
                requests.get, api_url, headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "success": True,
                "status": {
                    "active": result.get("active"),
                    "name": result.get("name"),
                    "createdAt": result.get("createdAt"),
                    "updatedAt": result.get("updatedAt"),
                    "tags": result.get("tags", [])
                }
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting n8n workflow status {n8n_workflow_id} (HTTP Error): {str(e)}")
            return {"success": False, "error": f"HTTP Error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error getting n8n workflow status {n8n_workflow_id}: {str(e)}")
            return {"success": False, "error": str(e)}

    async def trigger_n8n_webhook(self, webhook_path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger an n8n webhook.

        Args:
            webhook_path: The path of the webhook (e.g., webhook/task_id).
            data: Data to send to the webhook.

        Returns:
            Dict containing trigger status.
        """
        try:
            webhook_url = f"{self.n8n_url}/{webhook_path}"
            headers = {"Content-Type": "application/json"}
            
            response = await asyncio.to_thread(
                requests.post, webhook_url, headers=headers, json=data
            )
            response.raise_for_status()
            
            logger.info(f"Triggered n8n webhook at {webhook_path}")
            
            return {"success": True, "response": response.text}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error triggering n8n webhook {webhook_path} (HTTP Error): {str(e)}")
            return {"success": False, "error": f"HTTP Error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error triggering n8n webhook {webhook_path}: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_agent_manifest(self) -> Dict[str, Any]:
        """Get the agent manifest.

        Returns:
            Dict containing agent manifest information.
        """
        return {
            "agent_id": self.agent_id,
            "layer": "workflow_layer",
            "capabilities": self.agent_capabilities,
            "supported_protocols": self.supported_protocols,
            "resilience_mode": "retry_with_backoff",
            "ui_capsule_support": {
                "capsule_editable": False,  # Adapter logic is internal
                "n8n_embedded": False,
                "editable_nodes": []
            }
        }

    async def handle_protocol_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a protocol message.

        Args:
            message: Protocol message to handle.

        Returns:
            Dict containing handling result.
        """
        try:
            message_type = message.get("message_type")
            payload = message.get("payload", {})
            
            if message_type == "translate_to_n8n":
                return await self.translate_to_n8n(payload.get("industriverse_task", {}))
            elif message_type == "create_n8n_workflow":
                return await self.create_n8n_workflow(payload.get("workflow_data", {}))
            elif message_type == "update_n8n_workflow":
                n8n_workflow_id = payload.get("n8n_workflow_id")
                workflow_data = payload.get("workflow_data", {})
                return await self.update_n8n_workflow(n8n_workflow_id, workflow_data)
            elif message_type == "activate_n8n_workflow":
                n8n_workflow_id = payload.get("n8n_workflow_id")
                return await self.activate_n8n_workflow(n8n_workflow_id)
            elif message_type == "deactivate_n8n_workflow":
                n8n_workflow_id = payload.get("n8n_workflow_id")
                return await self.deactivate_n8n_workflow(n8n_workflow_id)
            elif message_type == "delete_n8n_workflow":
                n8n_workflow_id = payload.get("n8n_workflow_id")
                return await self.delete_n8n_workflow(n8n_workflow_id)
            elif message_type == "get_n8n_workflow_status":
                n8n_workflow_id = payload.get("n8n_workflow_id")
                return await self.get_n8n_workflow_status(n8n_workflow_id)
            elif message_type == "trigger_n8n_webhook":
                webhook_path = payload.get("webhook_path")
                data = payload.get("data", {})
                return await self.trigger_n8n_webhook(webhook_path, data)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported message type: {message_type}"
                }
                
        except Exception as e:
            logger.error(f"Error handling protocol message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
