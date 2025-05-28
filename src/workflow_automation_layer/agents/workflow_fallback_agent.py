"""
Workflow Fallback Agent Module for the Workflow Automation Layer.

This agent handles workflow failures, providing fallback mechanisms, 
retries, and escalation paths to ensure business continuity.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowFallbackAgent:
    """Agent for handling workflow failures and providing fallback mechanisms."""

    def __init__(self, workflow_runtime):
        """Initialize the workflow fallback agent.

        Args:
            workflow_runtime: The workflow runtime instance.
        """
        self.workflow_runtime = workflow_runtime
        self.agent_id = "workflow-fallback-agent"
        self.agent_capabilities = ["failure_handling", "retry_management", "escalation"]
        self.supported_protocols = ["MCP", "A2A"]
        self.fallback_history = {}  # History of fallback actions
        self.retry_counters = {}  # Track retry attempts
        
        logger.info("Workflow Fallback Agent initialized")

    async def handle_failure(self, failure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a workflow or task failure.

        Args:
            failure_data: Failure data including workflow_id, task_id, error, etc.

        Returns:
            Dict containing fallback action and details.
        """
        try:
            # Validate required fields
            required_fields = ["workflow_id", "error_type"]
            for field in required_fields:
                if field not in failure_data:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            workflow_id = failure_data["workflow_id"]
            error_type = failure_data["error_type"]
            task_id = failure_data.get("task_id")  # Optional, may be workflow-level failure
            
            # Generate fallback ID
            fallback_id = str(uuid.uuid4())
            
            # Get workflow manifest
            workflow_manifest = await self.workflow_runtime.get_workflow_manifest(workflow_id)
            if not workflow_manifest:
                return {
                    "success": False,
                    "error": f"Workflow manifest not found for workflow {workflow_id}"
                }
            
            # Get fallback configuration from workflow manifest
            fallback_config = workflow_manifest.get("fallback_configuration", {})
            
            # Determine fallback action based on error type and configuration
            fallback_action = await self._determine_fallback_action(
                workflow_id, task_id, error_type, fallback_config, failure_data
            )
            
            # Execute fallback action
            action_result = await self._execute_fallback_action(fallback_action, failure_data)
            
            # Store fallback history
            self.fallback_history[fallback_id] = {
                "workflow_id": workflow_id,
                "task_id": task_id,
                "error_type": error_type,
                "timestamp": datetime.utcnow().isoformat(),
                "fallback_action": fallback_action,
                "action_result": action_result
            }
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "handle_failure",
                "reason": f"Handled failure for workflow {workflow_id} with action {fallback_action['action']}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry
            self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Handled failure for workflow {workflow_id} with action {fallback_action['action']}")
            
            return {
                "success": True,
                "fallback_id": fallback_id,
                "workflow_id": workflow_id,
                "task_id": task_id,
                "error_type": error_type,
                "fallback_action": fallback_action,
                "action_result": action_result
            }
            
        except Exception as e:
            logger.error(f"Error handling failure: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _determine_fallback_action(
        self, 
        workflow_id: str, 
        task_id: Optional[str], 
        error_type: str, 
        fallback_config: Dict[str, Any],
        failure_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Determine the appropriate fallback action.

        Args:
            workflow_id: ID of the workflow.
            task_id: ID of the task (if applicable).
            error_type: Type of error.
            fallback_config: Fallback configuration from workflow manifest.
            failure_data: Original failure data.

        Returns:
            Dict containing fallback action details.
        """
        # Check if there's a specific rule for this error type
        error_rules = fallback_config.get("error_rules", {})
        if error_type in error_rules:
            rule = error_rules[error_type]
            action = rule.get("action", "retry")
            
            if action == "retry":
                max_retries = rule.get("max_retries", 3)
                retry_delay = rule.get("retry_delay", 5)
                
                # Check retry counter
                retry_key = f"{workflow_id}:{task_id or 'workflow'}"
                current_retries = self.retry_counters.get(retry_key, 0)
                
                if current_retries < max_retries:
                    # Increment retry counter
                    self.retry_counters[retry_key] = current_retries + 1
                    
                    return {
                        "action": "retry",
                        "retry_count": current_retries + 1,
                        "max_retries": max_retries,
                        "retry_delay": retry_delay,
                        "reason": f"Retrying {current_retries + 1}/{max_retries} after error: {error_type}"
                    }
                else:
                    # Max retries reached, escalate
                    return {
                        "action": "escalate",
                        "escalation_target": rule.get("escalation_target", "human_intervention_agent"),
                        "reason": f"Max retries ({max_retries}) reached for error: {error_type}"
                    }
            elif action == "escalate":
                return {
                    "action": "escalate",
                    "escalation_target": rule.get("escalation_target", "human_intervention_agent"),
                    "reason": f"Direct escalation for error: {error_type}"
                }
            elif action == "abort":
                return {
                    "action": "abort",
                    "reason": f"Aborting due to error: {error_type}"
                }
            elif action == "alternative_path":
                return {
                    "action": "alternative_path",
                    "alternative_workflow_id": rule.get("alternative_workflow_id"),
                    "reason": f"Using alternative path for error: {error_type}"
                }
        
        # No specific rule, use default behavior
        default_action = fallback_config.get("default_action", "retry")
        
        if default_action == "retry":
            max_retries = fallback_config.get("default_max_retries", 3)
            retry_delay = fallback_config.get("default_retry_delay", 5)
            
            # Check retry counter
            retry_key = f"{workflow_id}:{task_id or 'workflow'}"
            current_retries = self.retry_counters.get(retry_key, 0)
            
            if current_retries < max_retries:
                # Increment retry counter
                self.retry_counters[retry_key] = current_retries + 1
                
                return {
                    "action": "retry",
                    "retry_count": current_retries + 1,
                    "max_retries": max_retries,
                    "retry_delay": retry_delay,
                    "reason": f"Default retry {current_retries + 1}/{max_retries} for error: {error_type}"
                }
            else:
                # Max retries reached, escalate
                return {
                    "action": "escalate",
                    "escalation_target": fallback_config.get("default_escalation_target", "human_intervention_agent"),
                    "reason": f"Default max retries ({max_retries}) reached for error: {error_type}"
                }
        elif default_action == "escalate":
            return {
                "action": "escalate",
                "escalation_target": fallback_config.get("default_escalation_target", "human_intervention_agent"),
                "reason": f"Default escalation for error: {error_type}"
            }
        elif default_action == "abort":
            return {
                "action": "abort",
                "reason": f"Default abort for error: {error_type}"
            }
        else:
            # Unknown action, escalate to be safe
            return {
                "action": "escalate",
                "escalation_target": "human_intervention_agent",
                "reason": f"Unknown fallback action: {default_action}, escalating for error: {error_type}"
            }

    async def _execute_fallback_action(self, fallback_action: Dict[str, Any], failure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the determined fallback action.

        Args:
            fallback_action: Fallback action details.
            failure_data: Original failure data.

        Returns:
            Dict containing execution result.
        """
        action = fallback_action["action"]
        workflow_id = failure_data["workflow_id"]
        task_id = failure_data.get("task_id")
        
        if action == "retry":
            retry_delay = fallback_action.get("retry_delay", 5)
            retry_count = fallback_action.get("retry_count", 1)
            
            # Wait for retry delay
            await asyncio.sleep(retry_delay)
            
            # Retry task or workflow
            if task_id:
                # Retry specific task
                retry_result = await self.workflow_runtime.retry_task(workflow_id, task_id)
            else:
                # Retry entire workflow
                retry_result = await self.workflow_runtime.retry_workflow(workflow_id)
            
            return {
                "action_executed": "retry",
                "retry_count": retry_count,
                "retry_delay": retry_delay,
                "retry_result": retry_result
            }
            
        elif action == "escalate":
            escalation_target = fallback_action.get("escalation_target", "human_intervention_agent")
            
            # Prepare escalation data
            escalation_data = {
                "workflow_id": workflow_id,
                "task_id": task_id,
                "error_type": failure_data["error_type"],
                "error_details": failure_data.get("error_details", {}),
                "escalation_reason": fallback_action["reason"],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send escalation to target agent
            if escalation_target == "human_intervention_agent":
                # Get human intervention agent
                human_agent = self.workflow_runtime.get_agent("human_intervention")
                if human_agent:
                    escalation_result = await human_agent.request_intervention(escalation_data)
                else:
                    escalation_result = {
                        "success": False,
                        "error": "Human intervention agent not found"
                    }
            else:
                # Send to specified agent
                target_agent = self.workflow_runtime.get_agent(escalation_target)
                if target_agent:
                    escalation_result = await target_agent.handle_escalation(escalation_data)
                else:
                    escalation_result = {
                        "success": False,
                        "error": f"Escalation target agent {escalation_target} not found"
                    }
            
            return {
                "action_executed": "escalate",
                "escalation_target": escalation_target,
                "escalation_result": escalation_result
            }
            
        elif action == "abort":
            # Abort workflow
            abort_result = await self.workflow_runtime.abort_workflow(
                workflow_id, 
                reason=fallback_action["reason"]
            )
            
            return {
                "action_executed": "abort",
                "abort_result": abort_result
            }
            
        elif action == "alternative_path":
            alternative_workflow_id = fallback_action.get("alternative_workflow_id")
            
            if alternative_workflow_id:
                # Start alternative workflow
                alternative_result = await self.workflow_runtime.start_workflow(
                    alternative_workflow_id,
                    {
                        "original_workflow_id": workflow_id,
                        "original_error": failure_data["error_type"],
                        "original_task_id": task_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
            else:
                alternative_result = {
                    "success": False,
                    "error": "No alternative workflow ID specified"
                }
            
            return {
                "action_executed": "alternative_path",
                "alternative_workflow_id": alternative_workflow_id,
                "alternative_result": alternative_result
            }
            
        else:
            return {
                "action_executed": "unknown",
                "error": f"Unknown action: {action}"
            }

    async def reset_retry_counter(self, reset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Reset retry counter for a workflow or task.

        Args:
            reset_data: Reset data including workflow_id, task_id, etc.

        Returns:
            Dict containing reset status.
        """
        try:
            # Validate required fields
            if "workflow_id" not in reset_data:
                return {
                    "success": False,
                    "error": "Missing required field: workflow_id"
                }
            
            workflow_id = reset_data["workflow_id"]
            task_id = reset_data.get("task_id")
            
            # Create retry key
            retry_key = f"{workflow_id}:{task_id or 'workflow'}"
            
            # Check if retry counter exists
            if retry_key in self.retry_counters:
                old_value = self.retry_counters[retry_key]
                del self.retry_counters[retry_key]
                
                logger.info(f"Reset retry counter for {retry_key} from {old_value} to 0")
                
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "task_id": task_id,
                    "old_value": old_value,
                    "new_value": 0
                }
            else:
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "task_id": task_id,
                    "message": "No retry counter found to reset"
                }
            
        except Exception as e:
            logger.error(f"Error resetting retry counter: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_fallback_history(self, workflow_id: str = None) -> Dict[str, Any]:
        """Get history of fallback actions.

        Args:
            workflow_id: Optional ID of workflow to filter by.

        Returns:
            Dict containing fallback history.
        """
        if workflow_id:
            # Filter by workflow ID
            history = {
                fallback_id: data
                for fallback_id, data in self.fallback_history.items()
                if data["workflow_id"] == workflow_id
            }
        else:
            # Return all history
            history = self.fallback_history
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "fallback_count": len(history),
            "fallbacks": history
        }

    async def get_retry_counters(self, workflow_id: str = None) -> Dict[str, Any]:
        """Get current retry counters.

        Args:
            workflow_id: Optional ID of workflow to filter by.

        Returns:
            Dict containing retry counters.
        """
        if workflow_id:
            # Filter by workflow ID
            counters = {
                key: value
                for key, value in self.retry_counters.items()
                if key.startswith(f"{workflow_id}:")
            }
        else:
            # Return all counters
            counters = self.retry_counters
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "counter_count": len(counters),
            "counters": counters
        }

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
            "resilience_mode": "quorum_vote",
            "ui_capsule_support": {
                "capsule_editable": True,
                "n8n_embedded": True,
                "editable_nodes": ["fallback_strategy_node", "escalation_node"]
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
            
            if message_type == "handle_failure":
                return await self.handle_failure(message.get("payload", {}))
            elif message_type == "reset_retry_counter":
                return await self.reset_retry_counter(message.get("payload", {}))
            elif message_type == "get_fallback_history":
                payload = message.get("payload", {})
                workflow_id = payload.get("workflow_id")
                return await self.get_fallback_history(workflow_id)
            elif message_type == "get_retry_counters":
                payload = message.get("payload", {})
                workflow_id = payload.get("workflow_id")
                return await self.get_retry_counters(workflow_id)
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
