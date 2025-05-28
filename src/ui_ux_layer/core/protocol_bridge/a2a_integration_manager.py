"""
A2A Integration Manager for Protocol Bridge

This module manages the Agent-to-Agent (A2A) Protocol integration within the Protocol Bridge
of the Industriverse UI/UX Layer. It implements bidirectional communication, agent discovery,
and collaboration features using Google's A2A protocol.

The A2A Integration Manager:
1. Implements A2A message formatting and parsing
2. Handles agent discovery and capabilities advertisement
3. Manages agent collaboration and task delegation
4. Provides an API for sending and receiving A2A messages
5. Implements industry-specific enhancements to the A2A protocol

Author: Manus
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import time
import uuid
import threading
import queue
import requests
import base64
import hashlib
import os

# Local imports
from ..context_engine.context_awareness_engine import ContextAwarenessEngine

# Configure logging
logger = logging.getLogger(__name__)

class A2AMessageType(Enum):
    """Enumeration of A2A message types."""
    AGENT_CARD = "agent_card"
    AGENT_DISCOVERY = "agent_discovery"
    AGENT_CAPABILITIES = "agent_capabilities"
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    TASK_UPDATE = "task_update"
    TASK_COMPLETION = "task_completion"
    ARTIFACT_TRANSFER = "artifact_transfer"
    ARTIFACT_REQUEST = "artifact_request"
    ARTIFACT_RESPONSE = "artifact_response"
    COLLABORATION_REQUEST = "collaboration_request"
    COLLABORATION_RESPONSE = "collaboration_response"
    COLLABORATION_UPDATE = "collaboration_update"
    ERROR = "error"

class A2AIntegrationManager:
    """
    Manages the Agent-to-Agent (A2A) Protocol integration within the Protocol Bridge.
    
    This class is responsible for implementing bidirectional communication, agent discovery,
    and collaboration features using Google's A2A protocol with industry-specific enhancements.
    """
    
    def __init__(
        self, 
        context_engine: ContextAwarenessEngine,
        config: Dict = None
    ):
        """
        Initialize the A2A Integration Manager.
        
        Args:
            context_engine: The Context Awareness Engine instance
            config: Optional configuration dictionary
        """
        self.context_engine = context_engine
        self.config = config or {}
        
        # Default configuration
        self.default_config = {
            "a2a_version": "1.0",
            "agent_id": f"industriverse.ui_ux_layer.{uuid.uuid4()}",
            "agent_name": "Industriverse UI/UX Layer",
            "agent_description": "UI/UX Layer for the Industriverse platform",
            "discovery_interval": 300,  # seconds
            "heartbeat_interval": 60,   # seconds
            "reconnect_interval": 5,    # seconds
            "max_reconnect_attempts": 10,
            "message_timeout": 30,      # seconds
            "max_queue_size": 1000,
            "artifact_storage_path": "/tmp/a2a_artifacts",
            "registry_endpoint": "https://a2a-registry.example.com/api/v1",
            "direct_endpoints": {},
            "industry_tags": ["manufacturing", "logistics", "energy", "retail"],
            "schema_version": "1.0"
        }
        
        # Merge provided config with defaults
        self._merge_config()
        
        # Ensure artifact storage directory exists
        os.makedirs(self.config["artifact_storage_path"], exist_ok=True)
        
        # Known agents by agent ID
        self.known_agents = {}
        
        # Agent capabilities by agent ID
        self.agent_capabilities = {}
        
        # Active tasks by task ID
        self.active_tasks = {}
        
        # Active collaborations by collaboration ID
        self.active_collaborations = {}
        
        # Artifact metadata by artifact ID
        self.artifact_metadata = {}
        
        # Message handlers by message type
        self.message_handlers = {}
        
        # Default message handlers
        self.default_handlers = self._create_default_handlers()
        
        # Pending responses by message ID
        self.pending_responses = {}
        
        # Response events by message ID
        self.response_events = {}
        
        # Outgoing message queue
        self.outgoing_queue = queue.Queue(maxsize=self.config["max_queue_size"])
        
        # Connection status by agent ID
        self.connection_status = {}
        
        # Task handlers by task type
        self.task_handlers = {}
        
        # Workflow templates
        self.workflow_templates = self._load_workflow_templates()
        
        # Register as context listener
        self.context_engine.register_context_listener(self._handle_context_change)
        
        # Start worker threads
        self.running = True
        self.outgoing_thread = threading.Thread(target=self._outgoing_worker)
        self.outgoing_thread.daemon = True
        self.outgoing_thread.start()
        
        self.discovery_thread = threading.Thread(target=self._discovery_worker)
        self.discovery_thread.daemon = True
        self.discovery_thread.start()
        
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_worker)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()
        
        logger.info("A2A Integration Manager initialized")
    
    def _merge_config(self) -> None:
        """Merge provided configuration with defaults."""
        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value
            elif isinstance(value, dict) and isinstance(self.config[key], dict):
                # Merge nested dictionaries
                for nested_key, nested_value in value.items():
                    if nested_key not in self.config[key]:
                        self.config[key][nested_key] = nested_value
    
    def _create_default_handlers(self) -> Dict:
        """
        Create default message handlers.
        
        Returns:
            Dictionary of default handlers by message type
        """
        return {
            A2AMessageType.AGENT_CARD.value: self._handle_agent_card,
            A2AMessageType.AGENT_DISCOVERY.value: self._handle_agent_discovery,
            A2AMessageType.AGENT_CAPABILITIES.value: self._handle_agent_capabilities,
            A2AMessageType.TASK_REQUEST.value: self._handle_task_request,
            A2AMessageType.TASK_RESPONSE.value: self._handle_task_response,
            A2AMessageType.TASK_UPDATE.value: self._handle_task_update,
            A2AMessageType.TASK_COMPLETION.value: self._handle_task_completion,
            A2AMessageType.ARTIFACT_TRANSFER.value: self._handle_artifact_transfer,
            A2AMessageType.ARTIFACT_REQUEST.value: self._handle_artifact_request,
            A2AMessageType.ARTIFACT_RESPONSE.value: self._handle_artifact_response,
            A2AMessageType.COLLABORATION_REQUEST.value: self._handle_collaboration_request,
            A2AMessageType.COLLABORATION_RESPONSE.value: self._handle_collaboration_response,
            A2AMessageType.COLLABORATION_UPDATE.value: self._handle_collaboration_update,
            A2AMessageType.ERROR.value: self._handle_error
        }
    
    def _load_workflow_templates(self) -> Dict:
        """
        Load workflow templates.
        
        Returns:
            Dictionary of workflow templates by template ID
        """
        # In a real implementation, this would load from configuration files
        # For now, we'll define some basic templates inline
        
        return {
            "manufacturing_quality_inspection": {
                "id": "manufacturing_quality_inspection",
                "name": "Manufacturing Quality Inspection",
                "description": "Workflow for quality inspection in manufacturing",
                "version": "1.0",
                "industry_tags": ["manufacturing"],
                "steps": [
                    {
                        "id": "data_collection",
                        "name": "Data Collection",
                        "description": "Collect quality data from sensors",
                        "required_capabilities": ["sensor_data_processing"]
                    },
                    {
                        "id": "analysis",
                        "name": "Analysis",
                        "description": "Analyze quality data",
                        "required_capabilities": ["data_analysis"]
                    },
                    {
                        "id": "reporting",
                        "name": "Reporting",
                        "description": "Generate quality report",
                        "required_capabilities": ["report_generation"]
                    }
                ]
            },
            "logistics_route_optimization": {
                "id": "logistics_route_optimization",
                "name": "Logistics Route Optimization",
                "description": "Workflow for optimizing delivery routes",
                "version": "1.0",
                "industry_tags": ["logistics"],
                "steps": [
                    {
                        "id": "data_collection",
                        "name": "Data Collection",
                        "description": "Collect delivery locations and constraints",
                        "required_capabilities": ["location_data_processing"]
                    },
                    {
                        "id": "optimization",
                        "name": "Optimization",
                        "description": "Optimize delivery routes",
                        "required_capabilities": ["route_optimization"]
                    },
                    {
                        "id": "scheduling",
                        "name": "Scheduling",
                        "description": "Schedule deliveries",
                        "required_capabilities": ["scheduling"]
                    }
                ]
            },
            "energy_consumption_analysis": {
                "id": "energy_consumption_analysis",
                "name": "Energy Consumption Analysis",
                "description": "Workflow for analyzing energy consumption",
                "version": "1.0",
                "industry_tags": ["energy"],
                "steps": [
                    {
                        "id": "data_collection",
                        "name": "Data Collection",
                        "description": "Collect energy consumption data",
                        "required_capabilities": ["energy_data_processing"]
                    },
                    {
                        "id": "analysis",
                        "name": "Analysis",
                        "description": "Analyze energy consumption patterns",
                        "required_capabilities": ["data_analysis"]
                    },
                    {
                        "id": "optimization",
                        "name": "Optimization",
                        "description": "Suggest energy optimization strategies",
                        "required_capabilities": ["energy_optimization"]
                    }
                ]
            },
            "retail_inventory_management": {
                "id": "retail_inventory_management",
                "name": "Retail Inventory Management",
                "description": "Workflow for managing retail inventory",
                "version": "1.0",
                "industry_tags": ["retail"],
                "steps": [
                    {
                        "id": "data_collection",
                        "name": "Data Collection",
                        "description": "Collect inventory data",
                        "required_capabilities": ["inventory_data_processing"]
                    },
                    {
                        "id": "analysis",
                        "name": "Analysis",
                        "description": "Analyze inventory levels and trends",
                        "required_capabilities": ["data_analysis"]
                    },
                    {
                        "id": "forecasting",
                        "name": "Forecasting",
                        "description": "Forecast future inventory needs",
                        "required_capabilities": ["demand_forecasting"]
                    },
                    {
                        "id": "ordering",
                        "name": "Ordering",
                        "description": "Generate purchase orders",
                        "required_capabilities": ["order_management"]
                    }
                ]
            }
        }
    
    def _handle_context_change(self, event: Dict) -> None:
        """
        Handle context change events.
        
        Args:
            event: Context change event
        """
        context_type = event.get("type")
        
        # Handle industry context changes
        if context_type == "industry":
            industry_data = event.get("data", {})
            
            # Update industry tags if industry changes
            if "industry" in industry_data:
                industry = industry_data["industry"]
                self._update_industry_tags(industry)
        
        # Handle task context changes
        elif context_type == "task":
            task_data = event.get("data", {})
            
            # Update active tasks if task state changes
            if "task_id" in task_data and "task_state" in task_data:
                task_id = task_data["task_id"]
                task_state = task_data["task_state"]
                
                if task_id in self.active_tasks:
                    self.active_tasks[task_id]["state"] = task_state
                    
                    # Notify collaborators of task update
                    self._notify_task_update(task_id, task_state)
    
    def _update_industry_tags(self, industry: str) -> None:
        """
        Update industry tags based on current industry.
        
        Args:
            industry: Current industry
        """
        # Map industry to tags
        industry_tag_map = {
            "manufacturing": ["manufacturing", "production", "assembly", "quality_control"],
            "logistics": ["logistics", "transportation", "warehousing", "supply_chain"],
            "energy": ["energy", "utilities", "power_generation", "distribution"],
            "retail": ["retail", "sales", "inventory", "customer_experience"]
        }
        
        # Update industry tags
        if industry in industry_tag_map:
            self.config["industry_tags"] = industry_tag_map[industry]
            
            logger.info(f"Updated industry tags: {self.config['industry_tags']}")
    
    def _notify_task_update(self, task_id: str, task_state: str) -> None:
        """
        Notify collaborators of task update.
        
        Args:
            task_id: Task ID
            task_state: New task state
        """
        # Get task details
        task = self.active_tasks.get(task_id)
        if not task:
            return
        
        # Get collaborators
        collaborators = task.get("collaborators", [])
        
        # Create task update message
        message = {
            "protocol": "a2a",
            "version": self.config["a2a_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": A2AMessageType.TASK_UPDATE.value,
            "source": self.config["agent_id"],
            "timestamp": time.time(),
            "schema_version": self.config["schema_version"],
            "payload": {
                "task_id": task_id,
                "task_state": task_state,
                "update_timestamp": time.time(),
                "update_description": f"Task state changed to {task_state}"
            }
        }
        
        # Send to all collaborators
        for collaborator in collaborators:
            if collaborator != self.config["agent_id"]:
                message_copy = message.copy()
                message_copy["destination"] = collaborator
                self.send_a2a_message(message_copy)
    
    def _outgoing_worker(self) -> None:
        """Background thread for sending outgoing messages."""
        while self.running:
            try:
                # Get next message from queue
                message, destination = self.outgoing_queue.get(timeout=1.0)
                
                # Send message
                self._send_message_to_destination(message, destination)
                
                # Mark task as done
                self.outgoing_queue.task_done()
            except queue.Empty:
                # Queue empty, continue
                pass
            except Exception as e:
                logger.error(f"Error in outgoing worker: {str(e)}")
                time.sleep(1)  # Avoid tight loop on error
    
    def _send_message_to_destination(self, message: Dict, destination: str) -> bool:
        """
        Send a message to a specific destination.
        
        Args:
            message: Message to send
            destination: Destination agent ID
            
        Returns:
            Boolean indicating success
        """
        # Check if we have a direct endpoint for this agent
        if destination in self.config["direct_endpoints"]:
            endpoint = self.config["direct_endpoints"][destination]
            return self._send_direct_message(endpoint, message)
        
        # Fall back to registry-based routing
        return self._send_registry_message(destination, message)
    
    def _send_direct_message(self, endpoint: str, message: Dict) -> bool:
        """
        Send a message directly to an endpoint.
        
        Args:
            endpoint: Destination endpoint URL
            message: Message to send
            
        Returns:
            Boolean indicating success
        """
        try:
            # Send HTTP POST request
            response = requests.post(
                endpoint,
                json=message,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            # Check response
            if response.status_code == 200:
                return True
            else:
                logger.error(
                    f"HTTP error sending to {endpoint}: "
                    f"{response.status_code} - {response.text}"
                )
                return False
        except Exception as e:
            logger.error(f"Error sending direct message to {endpoint}: {str(e)}")
            return False
    
    def _send_registry_message(self, destination: str, message: Dict) -> bool:
        """
        Send a message via the registry.
        
        Args:
            destination: Destination agent ID
            message: Message to send
            
        Returns:
            Boolean indicating success
        """
        try:
            # Send HTTP POST request to registry
            response = requests.post(
                f"{self.config['registry_endpoint']}/messages",
                json={
                    "destination": destination,
                    "message": message
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            # Check response
            if response.status_code == 200:
                return True
            else:
                logger.error(
                    f"Registry error sending to {destination}: "
                    f"{response.status_code} - {response.text}"
                )
                return False
        except Exception as e:
            logger.error(f"Error sending registry message to {destination}: {str(e)}")
            return False
    
    def _discovery_worker(self) -> None:
        """Background thread for agent discovery."""
        # Initial discovery
        self._perform_discovery()
        
        while self.running:
            try:
                # Sleep until next discovery
                time.sleep(self.config["discovery_interval"])
                
                # Perform discovery
                self._perform_discovery()
            except Exception as e:
                logger.error(f"Error in discovery worker: {str(e)}")
                time.sleep(60)  # Longer sleep on error
    
    def _perform_discovery(self) -> None:
        """Perform agent discovery."""
        logger.info("Performing agent discovery")
        
        try:
            # Create discovery message
            message = {
                "protocol": "a2a",
                "version": self.config["a2a_version"],
                "message_id": str(uuid.uuid4()),
                "message_type": A2AMessageType.AGENT_DISCOVERY.value,
                "source": self.config["agent_id"],
                "destination": "registry",
                "timestamp": time.time(),
                "schema_version": self.config["schema_version"],
                "payload": {
                    "agent_card": self._create_agent_card(),
                    "discovery_scope": {
                        "industry_tags": self.config["industry_tags"],
                        "capabilities": ["ui_rendering", "user_interaction", "context_awareness"]
                    }
                }
            }
            
            # Send to registry
            response = requests.post(
                f"{self.config['registry_endpoint']}/discovery",
                json=message,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            # Process response
            if response.status_code == 200:
                discovery_results = response.json()
                self._process_discovery_results(discovery_results)
            else:
                logger.error(
                    f"Discovery error: {response.status_code} - {response.text}"
                )
        except Exception as e:
            logger.error(f"Error performing discovery: {str(e)}")
    
    def _create_agent_card(self) -> Dict:
        """
        Create agent card for this agent.
        
        Returns:
            Agent card dictionary
        """
        return {
            "agent_id": self.config["agent_id"],
            "agent_name": self.config["agent_name"],
            "agent_description": self.config["agent_description"],
            "agent_version": self.config["a2a_version"],
            "agent_capabilities": [
                "ui_rendering",
                "user_interaction",
                "context_awareness",
                "capsule_management",
                "workflow_visualization"
            ],
            "industry_tags": self.config["industry_tags"],
            "contact_endpoints": {
                "direct": f"https://industriverse.example.com/a2a/{self.config['agent_id']}"
            },
            "schema_version": self.config["schema_version"],
            "priority_support": True
        }
    
    def _process_discovery_results(self, results: Dict) -> None:
        """
        Process discovery results.
        
        Args:
            results: Discovery results
        """
        agents = results.get("agents", [])
        
        # Update known agents
        for agent_card in agents:
            agent_id = agent_card.get("agent_id")
            
            if agent_id and agent_id != self.config["agent_id"]:
                # Store agent card
                self.known_agents[agent_id] = agent_card
                
                # Update connection status
                if agent_id not in self.connection_status:
                    self.connection_status[agent_id] = {
                        "connected": True,
                        "last_contact": time.time(),
                        "direct_endpoint": agent_card.get("contact_endpoints", {}).get("direct")
                    }
                else:
                    self.connection_status[agent_id]["connected"] = True
                    self.connection_status[agent_id]["last_contact"] = time.time()
                    self.connection_status[agent_id]["direct_endpoint"] = agent_card.get("contact_endpoints", {}).get("direct")
                
                # Store direct endpoint if available
                direct_endpoint = agent_card.get("contact_endpoints", {}).get("direct")
                if direct_endpoint:
                    self.config["direct_endpoints"][agent_id] = direct_endpoint
                
                # Request capabilities if not already known
                if agent_id not in self.agent_capabilities:
                    self._request_agent_capabilities(agent_id)
        
        logger.info(f"Updated {len(agents)} agents from discovery")
    
    def _request_agent_capabilities(self, agent_id: str) -> None:
        """
        Request capabilities from an agent.
        
        Args:
            agent_id: Agent ID to request capabilities from
        """
        # Create capabilities request message
        message = {
            "protocol": "a2a",
            "version": self.config["a2a_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": A2AMessageType.AGENT_CAPABILITIES.value,
            "source": self.config["agent_id"],
            "destination": agent_id,
            "timestamp": time.time(),
            "schema_version": self.config["schema_version"],
            "payload": {
                "request_type": "capabilities_request"
            }
        }
        
        # Send message
        self.send_a2a_message(message)
    
    def _heartbeat_worker(self) -> None:
        """Background thread for sending heartbeat messages."""
        while self.running:
            try:
                # Send heartbeats to all known agents
                for agent_id, status in self.connection_status.items():
                    # Check if heartbeat is due
                    last_contact = status.get("last_contact", 0)
                    if time.time() - last_contact >= self.config["heartbeat_interval"]:
                        self._send_heartbeat(agent_id)
                
                # Sleep until next check
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in heartbeat worker: {str(e)}")
                time.sleep(5)  # Avoid tight loop on error
    
    def _send_heartbeat(self, agent_id: str) -> None:
        """
        Send a heartbeat message to an agent.
        
        Args:
            agent_id: Agent ID to send heartbeat to
        """
        # Create heartbeat message (using agent card as heartbeat)
        message = {
            "protocol": "a2a",
            "version": self.config["a2a_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": A2AMessageType.AGENT_CARD.value,
            "source": self.config["agent_id"],
            "destination": agent_id,
            "timestamp": time.time(),
            "schema_version": self.config["schema_version"],
            "payload": {
                "agent_card": self._create_agent_card()
            }
        }
        
        # Send message
        if self.send_a2a_message(message):
            # Update last contact time
            if agent_id in self.connection_status:
                self.connection_status[agent_id]["last_contact"] = time.time()
    
    # Message handlers
    
    def _handle_agent_card(self, message: Dict, source_agent: str) -> None:
        """
        Handle agent card message.
        
        Args:
            message: A2A message
            source_agent: Source agent ID
        """
        payload = message.get("payload", {})
        agent_card = payload.get("agent_card", {})
        
        agent_id = agent_card.get("agent_id")
        
        if not agent_id:
            logger.error("Missing agent_id in agent card")
            return
        
        # Store agent card
        self.known_agents[agent_id] = agent_card
        
        # Update connection status
        if agent_id not in self.connection_status:
            self.connection_status[agent_id] = {
                "connected": True,
                "last_contact": time.time(),
                "direct_endpoint": agent_card.get("contact_endpoints", {}).get("direct")
            }
        else:
            self.connection_status[agent_id]["connected"] = True
            self.connection_status[agent_id]["last_contact"] = time.time()
            self.connection_status[agent_id]["direct_endpoint"] = agent_card.get("contact_endpoints", {}).get("direct")
        
        # Store direct endpoint if available
        direct_endpoint = agent_card.get("contact_endpoints", {}).get("direct")
        if direct_endpoint:
            self.config["direct_endpoints"][agent_id] = direct_endpoint
        
        logger.debug(f"Updated agent card for {agent_id}")
    
    def _handle_agent_discovery(self, message: Dict, source_agent: str) -> None:
        """
        Handle agent discovery message.
        
        Args:
            message: A2A message
            source_agent: Source agent ID
        """
        payload = message.get("payload", {})
        agent_card = payload.get("agent_card", {})
        discovery_scope = payload.get("discovery_scope", {})
        
        # Store agent card
        agent_id = agent_card.get("agent_id")
        if agent_id:
            self.known_agents[agent_id] = agent_card
            
            # Update connection status
            if agent_id not in self.connection_status:
                self.connection_status[agent_id] = {
                    "connected": True,
                    "last_contact": time.time(),
                    "direct_endpoint": agent_card.get("contact_endpoints", {}).get("direct")
                }
            else:
                self.connection_status[agent_id]["connected"] = True
                self.connection_status[agent_id]["last_contact"] = time.time()
                self.connection_status[agent_id]["direct_endpoint"] = agent_card.get("contact_endpoints", {}).get("direct")
            
            # Store direct endpoint if available
            direct_endpoint = agent_card.get("contact_endpoints", {}).get("direct")
            if direct_endpoint:
                self.config["direct_endpoints"][agent_id] = direct_endpoint
        
        # Respond with our agent card if we match the discovery scope
        if self._matches_discovery_scope(discovery_scope):
            # Create response message
            response = {
                "protocol": "a2a",
                "version": self.config["a2a_version"],
                "message_id": str(uuid.uuid4()),
                "message_type": A2AMessageType.AGENT_CARD.value,
                "source": self.config["agent_id"],
                "destination": source_agent,
                "timestamp": time.time(),
                "schema_version": self.config["schema_version"],
                "payload": {
                    "agent_card": self._create_agent_card()
                }
            }
            
            # Send response
            self.send_a2a_message(response)
    
    def _matches_discovery_scope(self, discovery_scope: Dict) -> bool:
        """
        Check if this agent matches a discovery scope.
        
        Args:
            discovery_scope: Discovery scope to check against
            
        Returns:
            Boolean indicating match
        """
        # Check industry tags
        if "industry_tags" in discovery_scope:
            scope_tags = discovery_scope["industry_tags"]
            agent_tags = self.config["industry_tags"]
            
            # Check if any tags match
            if not any(tag in agent_tags for tag in scope_tags):
                return False
        
        # Check capabilities
        if "capabilities" in discovery_scope:
            scope_capabilities = discovery_scope["capabilities"]
            agent_capabilities = [
                "ui_rendering",
                "user_interaction",
                "context_awareness",
                "capsule_management",
                "workflow_visualization"
            ]
            
            # Check if any capabilities match
            if not any(cap in agent_capabilities for cap in scope_capabilities):
                return False
        
        return True
    
    def _handle_agent_capabilities(self, message: Dict, source_agent: str) -> None:
        """
        Handle agent capabilities message.
        
        Args:
            message: A2A message
            source_agent: Source agent ID
        """
        payload = message.get("payload", {})
        request_type = payload.get("request_type")
        
        if request_type == "capabilities_request":
            # This is a request for our capabilities
            self._send_capabilities_response(source_agent, message.get("message_id"))
        else:
            # This is a capabilities response
            capabilities = payload.get("capabilities", {})
            agent_id = source_agent
            
            if agent_id:
                # Store capabilities
                self.agent_capabilities[agent_id] = capabilities
                
                logger.debug(f"Updated capabilities for {agent_id}")
    
    def _send_capabilities_response(self, destination: str, request_id: str) -> None:
        """
        Send capabilities response.
        
        Args:
            destination: Destination agent ID
            request_id: Request message ID
        """
        # Create capabilities
        capabilities = {
            "ui_capabilities": [
                "responsive_design",
                "adaptive_layout",
                "dark_mode",
                "accessibility_features",
                "multi_language",
                "touch_support",
                "voice_interface",
                "ar_vr_support"
            ],
            "interaction_capabilities": [
                "gesture_recognition",
                "voice_commands",
                "haptic_feedback",
                "context_aware_interactions",
                "adaptive_interfaces",
                "multi_modal_input"
            ],
            "visualization_capabilities": [
                "data_visualization",
                "workflow_visualization",
                "digital_twin_visualization",
                "real_time_monitoring",
                "trend_analysis",
                "anomaly_highlighting"
            ],
            "workflow_templates": list(self.workflow_templates.keys())
        }
        
        # Create response message
        response = {
            "protocol": "a2a",
            "version": self.config["a2a_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": A2AMessageType.AGENT_CAPABILITIES.value,
            "source": self.config["agent_id"],
            "destination": destination,
            "timestamp": time.time(),
            "in_response_to": request_id,
            "schema_version": self.config["schema_version"],
            "payload": {
                "request_type": "capabilities_response",
                "capabilities": capabilities
            }
        }
        
        # Send response
        self.send_a2a_message(response)
    
    def _handle_task_request(self, message: Dict, source_agent: str) -> None:
        """
        Handle task request message.
        
        Args:
            message: A2A message
            source_agent: Source agent ID
        """
        message_id = message.get("message_id")
        payload = message.get("payload", {})
        task_type = payload.get("task_type")
        task_input = payload.get("task_input", {})
        task_priority = payload.get("priority", 3)  # Default to medium priority
        
        if not task_type:
            self._send_error_response(
                source_agent,
                message_id,
                "missing_task_type",
                "Missing task_type in task request"
            )
            return
        
        # Check if we can handle this task type
        can_handle = False
        handler = None
        
        if task_type in self.task_handlers:
            can_handle = True
            handler = self.task_handlers[task_type]
        elif task_type in ["render_ui", "update_ui", "show_notification"]:
            # Built-in task types
            can_handle = True
            handler = self._handle_ui_task
        
        if not can_handle:
            self._send_error_response(
                source_agent,
                message_id,
                "unsupported_task_type",
                f"Unsupported task type: {task_type}"
            )
            return
        
        # Create task ID
        task_id = str(uuid.uuid4())
        
        # Store task
        self.active_tasks[task_id] = {
            "task_id": task_id,
            "task_type": task_type,
            "task_input": task_input,
            "requester": source_agent,
            "state": "accepted",
            "priority": task_priority,
            "created_at": time.time(),
            "updated_at": time.time(),
            "collaborators": [source_agent, self.config["agent_id"]]
        }
        
        # Send task response
        response = {
            "protocol": "a2a",
            "version": self.config["a2a_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": A2AMessageType.TASK_RESPONSE.value,
            "source": self.config["agent_id"],
            "destination": source_agent,
            "timestamp": time.time(),
            "in_response_to": message_id,
            "schema_version": self.config["schema_version"],
            "payload": {
                "task_id": task_id,
                "task_state": "accepted",
                "estimated_completion": time.time() + 60  # Estimate 1 minute
            }
        }
        
        self.send_a2a_message(response)
        
        # Process task in background
        threading.Thread(target=self._process_task, args=(task_id, handler)).start()
    
    def _handle_ui_task(self, task_id: str, task_data: Dict) -> Dict:
        """
        Handle UI-related task.
        
        Args:
            task_id: Task ID
            task_data: Task data
            
        Returns:
            Task result
        """
        task_type = task_data.get("task_type")
        task_input = task_data.get("task_input", {})
        
        if task_type == "render_ui":
            # Simulate rendering UI
            component_type = task_input.get("component_type", "unknown")
            component_data = task_input.get("component_data", {})
            
            logger.info(f"Rendering UI component: {component_type}")
            
            # Update context with UI rendering event
            self.context_engine.update_context(
                "ui",
                {
                    "action": "render",
                    "component_type": component_type,
                    "component_data": component_data
                }
            )
            
            return {
                "success": True,
                "component_id": str(uuid.uuid4()),
                "render_time": time.time()
            }
        
        elif task_type == "update_ui":
            # Simulate updating UI
            component_id = task_input.get("component_id", "unknown")
            update_data = task_input.get("update_data", {})
            
            logger.info(f"Updating UI component: {component_id}")
            
            # Update context with UI update event
            self.context_engine.update_context(
                "ui",
                {
                    "action": "update",
                    "component_id": component_id,
                    "update_data": update_data
                }
            )
            
            return {
                "success": True,
                "update_time": time.time()
            }
        
        elif task_type == "show_notification":
            # Simulate showing notification
            notification_type = task_input.get("notification_type", "info")
            notification_message = task_input.get("message", "")
            
            logger.info(f"Showing notification: {notification_type} - {notification_message}")
            
            # Update context with notification event
            self.context_engine.update_context(
                "ui",
                {
                    "action": "notify",
                    "notification_type": notification_type,
                    "notification_message": notification_message
                }
            )
            
            return {
                "success": True,
                "notification_id": str(uuid.uuid4()),
                "display_time": time.time()
            }
        
        return {
            "success": False,
            "error": f"Unknown UI task type: {task_type}"
        }
    
    def _process_task(self, task_id: str, handler: callable) -> None:
        """
        Process a task in background.
        
        Args:
            task_id: Task ID to process
            handler: Task handler function
        """
        try:
            # Get task data
            task_data = self.active_tasks.get(task_id)
            if not task_data:
                logger.error(f"Task {task_id} not found")
                return
            
            # Update task state
            task_data["state"] = "processing"
            task_data["updated_at"] = time.time()
            
            # Notify requester of state change
            self._notify_task_update(task_id, "processing")
            
            # Process task
            result = handler(task_id, task_data)
            
            # Update task state
            task_data["state"] = "completed"
            task_data["updated_at"] = time.time()
            task_data["result"] = result
            
            # Send task completion
            self._send_task_completion(task_id, result)
        except Exception as e:
            logger.error(f"Error processing task {task_id}: {str(e)}")
            
            # Update task state
            if task_id in self.active_tasks:
                self.active_tasks[task_id]["state"] = "failed"
                self.active_tasks[task_id]["updated_at"] = time.time()
                self.active_tasks[task_id]["error"] = str(e)
                
                # Send task completion with error
                self._send_task_completion(task_id, None, str(e))
    
    def _send_task_completion(self, task_id: str, result: Dict = None, error: str = None) -> None:
        """
        Send task completion message.
        
        Args:
            task_id: Task ID
            result: Optional task result
            error: Optional error message
        """
        # Get task data
        task_data = self.active_tasks.get(task_id)
        if not task_data:
            logger.error(f"Task {task_id} not found")
            return
        
        # Get requester
        requester = task_data.get("requester")
        if not requester:
            logger.error(f"No requester for task {task_id}")
            return
        
        # Create completion message
        message = {
            "protocol": "a2a",
            "version": self.config["a2a_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": A2AMessageType.TASK_COMPLETION.value,
            "source": self.config["agent_id"],
            "destination": requester,
            "timestamp": time.time(),
            "schema_version": self.config["schema_version"],
            "payload": {
                "task_id": task_id,
                "task_state": "completed" if error is None else "failed",
                "completion_time": time.time()
            }
        }
        
        # Add result or error
        if result is not None:
            message["payload"]["result"] = result
        
        if error is not None:
            message["payload"]["error"] = error
        
        # Send message
        self.send_a2a_message(message)
    
    def _handle_task_response(self, message: Dict, source_agent: str) -> None:
        """
        Handle task response message.
        
        Args:
            message: A2A message
            source_agent: Source agent ID
        """
        # This is handled by the pending responses mechanism
        # No additional processing needed here
        pass
    
    def _handle_task_update(self, message: Dict, source_agent: str) -> None:
        """
        Handle task update message.
        
        Args:
            message: A2A message
            source_agent: Source agent ID
        """
        payload = message.get("payload", {})
        task_id = payload.get("task_id")
        task_state = payload.get("task_state")
        
        if not task_id or not task_state:
            logger.error("Missing task_id or task_state in task update")
            return
        
        # Update task if we know about it
        if task_id in self.active_tasks:
            self.active_tasks[task_id]["state"] = task_state
            self.active_tasks[task_id]["updated_at"] = time.time()
            
            # Add update info
            if "updates" not in self.active_tasks[task_id]:
                self.active_tasks[task_id]["updates"] = []
            
            self.active_tasks[task_id]["updates"].append({
                "state": task_state,
                "timestamp": time.time(),
                "source": source_agent,
                "description": payload.get("update_description", "")
            })
            
            logger.debug(f"Updated task {task_id} state to {task_state}")
    
    def _handle_task_completion(self, message: Dict, source_agent: str) -> None:
        """
        Handle task completion message.
        
        Args:
            message: A2A message
            source_agent: Source agent ID
        """
        payload = message.get("payload", {})
        task_id = payload.get("task_id")
        task_state = payload.get("task_state")
        result = payload.get("result")
        error = payload.get("error")
        
        if not task_id:
            logger.error("Missing task_id in task completion")
            return
        
        # Update task if we know about it
        if task_id in self.active_tasks:
            self.active_tasks[task_id]["state"] = task_state
            self.active_tasks[task_id]["updated_at"] = time.time()
            self.active_tasks[task_id]["completed_at"] = payload.get("completion_time", time.time())
            
            if result is not None:
                self.active_tasks[task_id]["result"] = result
            
            if error is not None:
                self.active_tasks[task_id]["error"] = error
            
            logger.info(f"Task {task_id} completed with state {task_state}")
            
            # Process task result if needed
            if task_state == "completed" and result is not None:
                self._process_task_result(task_id, result)
    
    def _process_task_result(self, task_id: str, result: Dict) -> None:
        """
        Process a completed task result.
        
        Args:
            task_id: Task ID
            result: Task result
        """
        # Get task data
        task_data = self.active_tasks.get(task_id)
        if not task_data:
            return
        
        task_type = task_data.get("task_type")
        
        # Handle different task types
        if task_type == "data_visualization":
            # Update UI with visualization
            visualization_data = result.get("visualization_data")
            if visualization_data:
                self.context_engine.update_context(
                    "ui",
                    {
                        "action": "update_visualization",
                        "visualization_data": visualization_data
                    }
                )
        elif task_type == "workflow_execution":
            # Update workflow state
            workflow_state = result.get("workflow_state")
            if workflow_state:
                self.context_engine.update_context(
                    "workflow",
                    {
                        "action": "update_state",
                        "workflow_state": workflow_state
                    }
                )
    
    def _handle_artifact_transfer(self, message: Dict, source_agent: str) -> None:
        """
        Handle artifact transfer message.
        
        Args:
            message: A2A message
            source_agent: Source agent ID
        """
        payload = message.get("payload", {})
        artifact_id = payload.get("artifact_id")
        artifact_type = payload.get("artifact_type")
        artifact_data = payload.get("artifact_data")
        artifact_metadata = payload.get("artifact_metadata", {})
        
        if not artifact_id or not artifact_type or not artifact_data:
            logger.error("Missing required fields in artifact transfer")
            return
        
        try:
            # Store artifact data
            artifact_path = os.path.join(
                self.config["artifact_storage_path"],
                f"{artifact_id}.data"
            )
            
            # Decode if base64 encoded
            if payload.get("encoding") == "base64":
                artifact_bytes = base64.b64decode(artifact_data)
                with open(artifact_path, "wb") as f:
                    f.write(artifact_bytes)
            else:
                # Assume JSON or string data
                with open(artifact_path, "w") as f:
                    if isinstance(artifact_data, dict):
                        json.dump(artifact_data, f)
                    else:
                        f.write(str(artifact_data))
            
            # Store metadata
            self.artifact_metadata[artifact_id] = {
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "source_agent": source_agent,
                "received_at": time.time(),
                "file_path": artifact_path,
                "metadata": artifact_metadata
            }
            
            logger.info(f"Received artifact {artifact_id} of type {artifact_type} from {source_agent}")
            
            # Send acknowledgement
            self._send_artifact_response(
                source_agent,
                artifact_id,
                "received",
                message.get("message_id")
            )
            
            # Process artifact if needed
            self._process_artifact(artifact_id)
        except Exception as e:
            logger.error(f"Error handling artifact transfer: {str(e)}")
            
            # Send error response
            self._send_artifact_response(
                source_agent,
                artifact_id,
                "error",
                message.get("message_id"),
                str(e)
            )
    
    def _process_artifact(self, artifact_id: str) -> None:
        """
        Process a received artifact.
        
        Args:
            artifact_id: Artifact ID to process
        """
        # Get artifact metadata
        metadata = self.artifact_metadata.get(artifact_id)
        if not metadata:
            return
        
        artifact_type = metadata.get("artifact_type")
        file_path = metadata.get("file_path")
        
        # Handle different artifact types
        if artifact_type == "visualization":
            # Update UI with visualization
            self.context_engine.update_context(
                "ui",
                {
                    "action": "show_visualization",
                    "artifact_id": artifact_id,
                    "file_path": file_path
                }
            )
        elif artifact_type == "report":
            # Show report
            self.context_engine.update_context(
                "ui",
                {
                    "action": "show_report",
                    "artifact_id": artifact_id,
                    "file_path": file_path
                }
            )
        elif artifact_type == "workflow_template":
            # Load workflow template
            try:
                with open(file_path, "r") as f:
                    template_data = json.load(f)
                
                # Add to workflow templates
                template_id = template_data.get("id")
                if template_id:
                    self.workflow_templates[template_id] = template_data
                    logger.info(f"Added workflow template: {template_id}")
            except Exception as e:
                logger.error(f"Error loading workflow template: {str(e)}")
    
    def _send_artifact_response(
        self, 
        destination: str, 
        artifact_id: str, 
        status: str, 
        request_id: str,
        error: str = None
    ) -> None:
        """
        Send artifact response message.
        
        Args:
            destination: Destination agent ID
            artifact_id: Artifact ID
            status: Response status
            request_id: Request message ID
            error: Optional error message
        """
        # Create response message
        message = {
            "protocol": "a2a",
            "version": self.config["a2a_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": A2AMessageType.ARTIFACT_RESPONSE.value,
            "source": self.config["agent_id"],
            "destination": destination,
            "timestamp": time.time(),
            "in_response_to": request_id,
            "schema_version": self.config["schema_version"],
            "payload": {
                "artifact_id": artifact_id,
                "status": status,
                "timestamp": time.time()
            }
        }
        
        # Add error if provided
        if error is not None:
            message["payload"]["error"] = error
        
        # Send message
        self.send_a2a_message(message)
    
    def _handle_artifact_request(self, message: Dict, source_agent: str) -> None:
        """
        Handle artifact request message.
        
        Args:
            message: A2A message
            source_agent: Source agent ID
        """
        message_id = message.get("message_id")
        payload = message.get("payload", {})
        artifact_id = payload.get("artifact_id")
        
        if not artifact_id:
            self._send_error_response(
                source_agent,
                message_id,
                "missing_artifact_id",
                "Missing artifact_id in artifact request"
            )
            return
        
        # Check if we have this artifact
        if artifact_id not in self.artifact_metadata:
            self._send_error_response(
                source_agent,
                message_id,
                "unknown_artifact",
                f"Unknown artifact: {artifact_id}"
            )
            return
        
        # Get artifact metadata
        metadata = self.artifact_metadata[artifact_id]
        file_path = metadata.get("file_path")
        
        try:
            # Read artifact data
            with open(file_path, "rb") as f:
                artifact_data = f.read()
            
            # Encode as base64
            artifact_data_b64 = base64.b64encode(artifact_data).decode("utf-8")
            
            # Create response message
            response = {
                "protocol": "a2a",
                "version": self.config["a2a_version"],
                "message_id": str(uuid.uuid4()),
                "message_type": A2AMessageType.ARTIFACT_TRANSFER.value,
                "source": self.config["agent_id"],
                "destination": source_agent,
                "timestamp": time.time(),
                "in_response_to": message_id,
                "schema_version": self.config["schema_version"],
                "payload": {
                    "artifact_id": artifact_id,
                    "artifact_type": metadata.get("artifact_type"),
                    "artifact_data": artifact_data_b64,
                    "encoding": "base64",
                    "artifact_metadata": metadata.get("metadata", {})
                }
            }
            
            # Send response
            self.send_a2a_message(response)
            
            logger.info(f"Sent artifact {artifact_id} to {source_agent}")
        except Exception as e:
            logger.error(f"Error sending artifact {artifact_id}: {str(e)}")
            
            self._send_error_response(
                source_agent,
                message_id,
                "artifact_transfer_error",
                f"Error transferring artifact: {str(e)}"
            )
    
    def _handle_artifact_response(self, message: Dict, source_agent: str) -> None:
        """
        Handle artifact response message.
        
        Args:
            message: A2A message
            source_agent: Source agent ID
        """
        # This is handled by the pending responses mechanism
        # No additional processing needed here
        pass
    
    def _handle_collaboration_request(self, message: Dict, source_agent: str) -> None:
        """
        Handle collaboration request message.
        
        Args:
            message: A2A message
            source_agent: Source agent ID
        """
        message_id = message.get("message_id")
        payload = message.get("payload", {})
        collaboration_type = payload.get("collaboration_type")
        collaboration_data = payload.get("collaboration_data", {})
        
        if not collaboration_type:
            self._send_error_response(
                source_agent,
                message_id,
                "missing_collaboration_type",
                "Missing collaboration_type in collaboration request"
            )
            return
        
        # Check if we can handle this collaboration type
        can_handle = False
        
        if collaboration_type in ["workflow_execution", "data_visualization", "ui_coordination"]:
            can_handle = True
        
        if not can_handle:
            self._send_error_response(
                source_agent,
                message_id,
                "unsupported_collaboration_type",
                f"Unsupported collaboration type: {collaboration_type}"
            )
            return
        
        # Create collaboration ID
        collaboration_id = str(uuid.uuid4())
        
        # Store collaboration
        self.active_collaborations[collaboration_id] = {
            "collaboration_id": collaboration_id,
            "collaboration_type": collaboration_type,
            "collaboration_data": collaboration_data,
            "initiator": source_agent,
            "participants": [source_agent, self.config["agent_id"]],
            "state": "active",
            "created_at": time.time(),
            "updated_at": time.time()
        }
        
        # Send collaboration response
        response = {
            "protocol": "a2a",
            "version": self.config["a2a_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": A2AMessageType.COLLABORATION_RESPONSE.value,
            "source": self.config["agent_id"],
            "destination": source_agent,
            "timestamp": time.time(),
            "in_response_to": message_id,
            "schema_version": self.config["schema_version"],
            "payload": {
                "collaboration_id": collaboration_id,
                "status": "accepted",
                "response_data": {
                    "capabilities": [
                        "ui_rendering",
                        "user_interaction",
                        "context_awareness"
                    ]
                }
            }
        }
        
        self.send_a2a_message(response)
        
        logger.info(f"Accepted collaboration {collaboration_id} of type {collaboration_type} from {source_agent}")
        
        # Process collaboration in background
        threading.Thread(target=self._process_collaboration, args=(collaboration_id,)).start()
    
    def _process_collaboration(self, collaboration_id: str) -> None:
        """
        Process a collaboration in background.
        
        Args:
            collaboration_id: Collaboration ID to process
        """
        try:
            # Get collaboration data
            collaboration = self.active_collaborations.get(collaboration_id)
            if not collaboration:
                logger.error(f"Collaboration {collaboration_id} not found")
                return
            
            collaboration_type = collaboration.get("collaboration_type")
            collaboration_data = collaboration.get("collaboration_data", {})
            
            # Handle different collaboration types
            if collaboration_type == "workflow_execution":
                self._handle_workflow_collaboration(collaboration_id, collaboration_data)
            elif collaboration_type == "data_visualization":
                self._handle_visualization_collaboration(collaboration_id, collaboration_data)
            elif collaboration_type == "ui_coordination":
                self._handle_ui_coordination_collaboration(collaboration_id, collaboration_data)
        except Exception as e:
            logger.error(f"Error processing collaboration {collaboration_id}: {str(e)}")
            
            # Update collaboration state
            if collaboration_id in self.active_collaborations:
                self.active_collaborations[collaboration_id]["state"] = "error"
                self.active_collaborations[collaboration_id]["error"] = str(e)
                self.active_collaborations[collaboration_id]["updated_at"] = time.time()
    
    def _handle_workflow_collaboration(self, collaboration_id: str, collaboration_data: Dict) -> None:
        """
        Handle workflow execution collaboration.
        
        Args:
            collaboration_id: Collaboration ID
            collaboration_data: Collaboration data
        """
        workflow_id = collaboration_data.get("workflow_id")
        workflow_template_id = collaboration_data.get("workflow_template_id")
        
        logger.info(f"Processing workflow collaboration: {workflow_id} (template: {workflow_template_id})")
        
        # Update context with workflow data
        self.context_engine.update_context(
            "workflow",
            {
                "action": "start_collaboration",
                "workflow_id": workflow_id,
                "workflow_template_id": workflow_template_id,
                "collaboration_id": collaboration_id
            }
        )
        
        # Send collaboration update
        self._send_collaboration_update(
            collaboration_id,
            "ui_ready",
            {
                "ui_components": ["workflow_canvas", "task_list", "progress_tracker"]
            }
        )
    
    def _handle_visualization_collaboration(self, collaboration_id: str, collaboration_data: Dict) -> None:
        """
        Handle data visualization collaboration.
        
        Args:
            collaboration_id: Collaboration ID
            collaboration_data: Collaboration data
        """
        visualization_id = collaboration_data.get("visualization_id")
        data_source = collaboration_data.get("data_source")
        
        logger.info(f"Processing visualization collaboration: {visualization_id} (source: {data_source})")
        
        # Update context with visualization data
        self.context_engine.update_context(
            "visualization",
            {
                "action": "start_collaboration",
                "visualization_id": visualization_id,
                "data_source": data_source,
                "collaboration_id": collaboration_id
            }
        )
        
        # Send collaboration update
        self._send_collaboration_update(
            collaboration_id,
            "ui_ready",
            {
                "ui_components": ["data_visualization", "filter_panel", "export_tools"]
            }
        )
    
    def _handle_ui_coordination_collaboration(self, collaboration_id: str, collaboration_data: Dict) -> None:
        """
        Handle UI coordination collaboration.
        
        Args:
            collaboration_id: Collaboration ID
            collaboration_data: Collaboration data
        """
        coordination_id = collaboration_data.get("coordination_id")
        ui_elements = collaboration_data.get("ui_elements", [])
        
        logger.info(f"Processing UI coordination collaboration: {coordination_id}")
        
        # Update context with UI coordination data
        self.context_engine.update_context(
            "ui",
            {
                "action": "start_coordination",
                "coordination_id": coordination_id,
                "ui_elements": ui_elements,
                "collaboration_id": collaboration_id
            }
        )
        
        # Send collaboration update
        self._send_collaboration_update(
            collaboration_id,
            "coordination_ready",
            {
                "coordinated_elements": ui_elements
            }
        )
    
    def _send_collaboration_update(
        self, 
        collaboration_id: str, 
        update_type: str, 
        update_data: Dict
    ) -> None:
        """
        Send collaboration update message.
        
        Args:
            collaboration_id: Collaboration ID
            update_type: Update type
            update_data: Update data
        """
        # Get collaboration
        collaboration = self.active_collaborations.get(collaboration_id)
        if not collaboration:
            logger.error(f"Collaboration {collaboration_id} not found")
            return
        
        # Get participants
        participants = collaboration.get("participants", [])
        
        # Create update message
        message = {
            "protocol": "a2a",
            "version": self.config["a2a_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": A2AMessageType.COLLABORATION_UPDATE.value,
            "source": self.config["agent_id"],
            "timestamp": time.time(),
            "schema_version": self.config["schema_version"],
            "payload": {
                "collaboration_id": collaboration_id,
                "update_type": update_type,
                "update_data": update_data,
                "timestamp": time.time()
            }
        }
        
        # Send to all participants except self
        for participant in participants:
            if participant != self.config["agent_id"]:
                message_copy = message.copy()
                message_copy["destination"] = participant
                self.send_a2a_message(message_copy)
    
    def _handle_collaboration_response(self, message: Dict, source_agent: str) -> None:
        """
        Handle collaboration response message.
        
        Args:
            message: A2A message
            source_agent: Source agent ID
        """
        # This is handled by the pending responses mechanism
        # No additional processing needed here
        pass
    
    def _handle_collaboration_update(self, message: Dict, source_agent: str) -> None:
        """
        Handle collaboration update message.
        
        Args:
            message: A2A message
            source_agent: Source agent ID
        """
        payload = message.get("payload", {})
        collaboration_id = payload.get("collaboration_id")
        update_type = payload.get("update_type")
        update_data = payload.get("update_data", {})
        
        if not collaboration_id or not update_type:
            logger.error("Missing collaboration_id or update_type in collaboration update")
            return
        
        # Update collaboration if we know about it
        if collaboration_id in self.active_collaborations:
            collaboration = self.active_collaborations[collaboration_id]
            
            # Add update info
            if "updates" not in collaboration:
                collaboration["updates"] = []
            
            collaboration["updates"].append({
                "update_type": update_type,
                "update_data": update_data,
                "source": source_agent,
                "timestamp": time.time()
            })
            
            collaboration["updated_at"] = time.time()
            
            logger.debug(f"Received collaboration update: {update_type} for {collaboration_id}")
            
            # Process update
            self._process_collaboration_update(collaboration_id, update_type, update_data, source_agent)
    
    def _process_collaboration_update(
        self, 
        collaboration_id: str, 
        update_type: str, 
        update_data: Dict,
        source_agent: str
    ) -> None:
        """
        Process a collaboration update.
        
        Args:
            collaboration_id: Collaboration ID
            update_type: Update type
            update_data: Update data
            source_agent: Source agent ID
        """
        # Get collaboration
        collaboration = self.active_collaborations.get(collaboration_id)
        if not collaboration:
            return
        
        collaboration_type = collaboration.get("collaboration_type")
        
        # Handle different update types based on collaboration type
        if collaboration_type == "workflow_execution":
            if update_type == "workflow_progress":
                # Update workflow progress
                progress = update_data.get("progress")
                current_step = update_data.get("current_step")
                
                self.context_engine.update_context(
                    "workflow",
                    {
                        "action": "update_progress",
                        "workflow_id": collaboration.get("collaboration_data", {}).get("workflow_id"),
                        "progress": progress,
                        "current_step": current_step
                    }
                )
            elif update_type == "workflow_completed":
                # Handle workflow completion
                result = update_data.get("result")
                
                self.context_engine.update_context(
                    "workflow",
                    {
                        "action": "complete_workflow",
                        "workflow_id": collaboration.get("collaboration_data", {}).get("workflow_id"),
                        "result": result
                    }
                )
                
                # Update collaboration state
                collaboration["state"] = "completed"
        
        elif collaboration_type == "data_visualization":
            if update_type == "data_update":
                # Update visualization data
                data_update = update_data.get("data")
                
                self.context_engine.update_context(
                    "visualization",
                    {
                        "action": "update_data",
                        "visualization_id": collaboration.get("collaboration_data", {}).get("visualization_id"),
                        "data_update": data_update
                    }
                )
            elif update_type == "visualization_settings":
                # Update visualization settings
                settings = update_data.get("settings")
                
                self.context_engine.update_context(
                    "visualization",
                    {
                        "action": "update_settings",
                        "visualization_id": collaboration.get("collaboration_data", {}).get("visualization_id"),
                        "settings": settings
                    }
                )
        
        elif collaboration_type == "ui_coordination":
            if update_type == "ui_event":
                # Handle UI event
                event_type = update_data.get("event_type")
                event_data = update_data.get("event_data")
                
                self.context_engine.update_context(
                    "ui",
                    {
                        "action": "handle_coordinated_event",
                        "coordination_id": collaboration.get("collaboration_data", {}).get("coordination_id"),
                        "event_type": event_type,
                        "event_data": event_data
                    }
                )
    
    def _handle_error(self, message: Dict, source_agent: str) -> None:
        """
        Handle error message.
        
        Args:
            message: A2A message
            source_agent: Source agent ID
        """
        payload = message.get("payload", {})
        error_code = payload.get("error_code")
        error_message = payload.get("error_message")
        in_response_to = message.get("in_response_to")
        
        logger.error(
            f"Received error from {source_agent}: "
            f"[{error_code}] {error_message} "
            f"(in response to: {in_response_to})"
        )
    
    def _send_error_response(
        self, 
        destination: str, 
        in_response_to: str, 
        error_code: str, 
        error_message: str
    ) -> None:
        """
        Send error response message.
        
        Args:
            destination: Destination agent ID
            in_response_to: Request message ID
            error_code: Error code
            error_message: Error message
        """
        # Create error message
        message = {
            "protocol": "a2a",
            "version": self.config["a2a_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": A2AMessageType.ERROR.value,
            "source": self.config["agent_id"],
            "destination": destination,
            "timestamp": time.time(),
            "in_response_to": in_response_to,
            "schema_version": self.config["schema_version"],
            "payload": {
                "error_code": error_code,
                "error_message": error_message
            }
        }
        
        # Send message
        self.send_a2a_message(message)
    
    # Public API
    
    def register_message_handler(self, message_type: str, handler: callable) -> bool:
        """
        Register a message handler.
        
        Args:
            message_type: Message type to handle
            handler: Handler function
            
        Returns:
            Boolean indicating success
        """
        # Verify message type
        if not any(t.value == message_type for t in A2AMessageType):
            logger.error(f"Invalid message type: {message_type}")
            return False
        
        # Register handler
        self.message_handlers[message_type] = handler
        
        logger.debug(f"Registered handler for {message_type} messages")
        return True
    
    def unregister_message_handler(self, message_type: str) -> bool:
        """
        Unregister a message handler.
        
        Args:
            message_type: Message type to unregister
            
        Returns:
            Boolean indicating success
        """
        if message_type in self.message_handlers:
            del self.message_handlers[message_type]
            logger.debug(f"Unregistered handler for {message_type} messages")
            return True
        
        return False
    
    def register_task_handler(self, task_type: str, handler: callable) -> bool:
        """
        Register a task handler.
        
        Args:
            task_type: Task type to handle
            handler: Handler function
            
        Returns:
            Boolean indicating success
        """
        self.task_handlers[task_type] = handler
        logger.debug(f"Registered handler for {task_type} tasks")
        return True
    
    def unregister_task_handler(self, task_type: str) -> bool:
        """
        Unregister a task handler.
        
        Args:
            task_type: Task type to unregister
            
        Returns:
            Boolean indicating success
        """
        if task_type in self.task_handlers:
            del self.task_handlers[task_type]
            logger.debug(f"Unregistered handler for {task_type} tasks")
            return True
        
        return False
    
    def send_a2a_message(self, message: Dict) -> bool:
        """
        Send an A2A message.
        
        Args:
            message: A2A message to send
            
        Returns:
            Boolean indicating success
        """
        # Validate message
        if not self._validate_a2a_message(message):
            return False
        
        # Get destination
        destination = message.get("destination")
        
        try:
            # Add to outgoing queue
            self.outgoing_queue.put((message, destination), timeout=1.0)
            return True
        except queue.Full:
            logger.error("Outgoing message queue full, message dropped")
            return False
    
    def _validate_a2a_message(self, message: Dict) -> bool:
        """
        Validate an A2A message.
        
        Args:
            message: A2A message to validate
            
        Returns:
            Boolean indicating validity
        """
        # Check required fields
        required_fields = [
            "protocol", "version", "message_id", "message_type",
            "source", "destination", "timestamp"
        ]
        
        for field in required_fields:
            if field not in message:
                logger.error(f"Missing required field in A2A message: {field}")
                return False
        
        # Check protocol
        if message["protocol"] != "a2a":
            logger.error(f"Invalid protocol in message: {message['protocol']}")
            return False
        
        # Check version compatibility
        if message["version"] != self.config["a2a_version"]:
            logger.warning(
                f"A2A version mismatch: message={message['version']}, "
                f"local={self.config['a2a_version']}"
            )
            # Continue processing despite version mismatch
        
        # Check message type
        if not any(t.value == message["message_type"] for t in A2AMessageType):
            logger.error(f"Invalid message type: {message['message_type']}")
            return False
        
        return True
    
    def send_a2a_message_sync(self, message: Dict, timeout: float = None) -> Optional[Dict]:
        """
        Send an A2A message and wait for response.
        
        Args:
            message: A2A message to send
            timeout: Optional timeout in seconds
            
        Returns:
            Response message or None on timeout/error
        """
        # Use default timeout if not specified
        if timeout is None:
            timeout = self.config["message_timeout"]
        
        # Validate message
        if not self._validate_a2a_message(message):
            return None
        
        # Get message ID
        message_id = message.get("message_id")
        
        # Create response event
        response_event = threading.Event()
        self.response_events[message_id] = response_event
        
        # Initialize pending response
        self.pending_responses[message_id] = None
        
        try:
            # Send message
            if not self.send_a2a_message(message):
                logger.error("Failed to send message")
                return None
            
            # Wait for response
            if response_event.wait(timeout):
                # Response received
                return self.pending_responses[message_id]
            else:
                # Timeout
                logger.warning(f"Timeout waiting for response to {message_id}")
                return None
        finally:
            # Clean up
            if message_id in self.response_events:
                del self.response_events[message_id]
            
            if message_id in self.pending_responses:
                del self.pending_responses[message_id]
    
    def discover_agents(self, industry_tags: List[str] = None, capabilities: List[str] = None) -> List[Dict]:
        """
        Discover agents with specific industry tags or capabilities.
        
        Args:
            industry_tags: Optional list of industry tags to filter by
            capabilities: Optional list of capabilities to filter by
            
        Returns:
            List of matching agent cards
        """
        # Use configured tags if none provided
        if industry_tags is None:
            industry_tags = self.config["industry_tags"]
        
        # Create discovery message
        message = {
            "protocol": "a2a",
            "version": self.config["a2a_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": A2AMessageType.AGENT_DISCOVERY.value,
            "source": self.config["agent_id"],
            "destination": "registry",
            "timestamp": time.time(),
            "schema_version": self.config["schema_version"],
            "payload": {
                "agent_card": self._create_agent_card(),
                "discovery_scope": {
                    "industry_tags": industry_tags
                }
            }
        }
        
        # Add capabilities if provided
        if capabilities:
            message["payload"]["discovery_scope"]["capabilities"] = capabilities
        
        try:
            # Send to registry
            response = requests.post(
                f"{self.config['registry_endpoint']}/discovery",
                json=message,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            # Process response
            if response.status_code == 200:
                discovery_results = response.json()
                agents = discovery_results.get("agents", [])
                
                # Update known agents
                for agent_card in agents:
                    agent_id = agent_card.get("agent_id")
                    
                    if agent_id and agent_id != self.config["agent_id"]:
                        # Store agent card
                        self.known_agents[agent_id] = agent_card
                
                return agents
            else:
                logger.error(
                    f"Discovery error: {response.status_code} - {response.text}"
                )
                return []
        except Exception as e:
            logger.error(f"Error performing discovery: {str(e)}")
            return []
    
    def get_agent_capabilities(self, agent_id: str, timeout: float = None) -> Optional[Dict]:
        """
        Get capabilities from an agent.
        
        Args:
            agent_id: Agent ID to get capabilities from
            timeout: Optional timeout in seconds
            
        Returns:
            Agent capabilities or None on timeout/error
        """
        # Check if we already have capabilities
        if agent_id in self.agent_capabilities:
            return self.agent_capabilities[agent_id]
        
        # Create capabilities request message
        message = {
            "protocol": "a2a",
            "version": self.config["a2a_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": A2AMessageType.AGENT_CAPABILITIES.value,
            "source": self.config["agent_id"],
            "destination": agent_id,
            "timestamp": time.time(),
            "schema_version": self.config["schema_version"],
            "payload": {
                "request_type": "capabilities_request"
            }
        }
        
        # Send message and wait for response
        response = self.send_a2a_message_sync(message, timeout)
        
        if response:
            capabilities = response.get("payload", {}).get("capabilities")
            
            if capabilities:
                # Store capabilities
                self.agent_capabilities[agent_id] = capabilities
            
            return capabilities
        else:
            return None
    
    def request_task(
        self, 
        agent_id: str, 
        task_type: str, 
        task_input: Dict, 
        priority: int = 3,
        timeout: float = None
    ) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Request a task from another agent.
        
        Args:
            agent_id: Agent ID to request task from
            task_type: Type of task to request
            task_input: Task input data
            priority: Task priority (1-5, 1 highest)
            timeout: Optional timeout in seconds
            
        Returns:
            Tuple of (success, task_id, response_data)
        """
        # Create task request message
        message = {
            "protocol": "a2a",
            "version": self.config["a2a_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": A2AMessageType.TASK_REQUEST.value,
            "source": self.config["agent_id"],
            "destination": agent_id,
            "timestamp": time.time(),
            "schema_version": self.config["schema_version"],
            "payload": {
                "task_type": task_type,
                "task_input": task_input,
                "priority": priority
            }
        }
        
        # Send message and wait for response
        response = self.send_a2a_message_sync(message, timeout)
        
        if response:
            payload = response.get("payload", {})
            task_id = payload.get("task_id")
            task_state = payload.get("task_state")
            
            if task_id and task_state == "accepted":
                # Store task
                self.active_tasks[task_id] = {
                    "task_id": task_id,
                    "task_type": task_type,
                    "task_input": task_input,
                    "handler": agent_id,
                    "state": task_state,
                    "priority": priority,
                    "created_at": time.time(),
                    "updated_at": time.time(),
                    "estimated_completion": payload.get("estimated_completion"),
                    "collaborators": [agent_id, self.config["agent_id"]]
                }
                
                return (True, task_id, payload)
            else:
                return (False, None, payload)
        else:
            return (False, None, None)
    
    def send_artifact(
        self, 
        agent_id: str, 
        artifact_type: str, 
        artifact_data: Any, 
        metadata: Dict = None,
        timeout: float = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Send an artifact to another agent.
        
        Args:
            agent_id: Agent ID to send artifact to
            artifact_type: Type of artifact
            artifact_data: Artifact data (bytes, string, or dict)
            metadata: Optional artifact metadata
            timeout: Optional timeout in seconds
            
        Returns:
            Tuple of (success, artifact_id, error_message)
        """
        # Generate artifact ID
        artifact_id = str(uuid.uuid4())
        
        # Prepare artifact data
        if isinstance(artifact_data, bytes):
            # Binary data, encode as base64
            artifact_data_encoded = base64.b64encode(artifact_data).decode("utf-8")
            encoding = "base64"
        elif isinstance(artifact_data, dict):
            # JSON data, use as is
            artifact_data_encoded = artifact_data
            encoding = "json"
        else:
            # String data, use as is
            artifact_data_encoded = str(artifact_data)
            encoding = "text"
        
        # Create artifact transfer message
        message = {
            "protocol": "a2a",
            "version": self.config["a2a_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": A2AMessageType.ARTIFACT_TRANSFER.value,
            "source": self.config["agent_id"],
            "destination": agent_id,
            "timestamp": time.time(),
            "schema_version": self.config["schema_version"],
            "payload": {
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "artifact_data": artifact_data_encoded,
                "encoding": encoding,
                "artifact_metadata": metadata or {}
            }
        }
        
        # Send message and wait for response
        response = self.send_a2a_message_sync(message, timeout)
        
        if response:
            payload = response.get("payload", {})
            status = payload.get("status")
            error = payload.get("error")
            
            if status == "received":
                return (True, artifact_id, None)
            else:
                return (False, artifact_id, error)
        else:
            return (False, artifact_id, "Timeout or communication error")
    
    def request_artifact(
        self, 
        agent_id: str, 
        artifact_id: str, 
        timeout: float = None
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Request an artifact from another agent.
        
        Args:
            agent_id: Agent ID to request artifact from
            artifact_id: Artifact ID to request
            timeout: Optional timeout in seconds
            
        Returns:
            Tuple of (success, artifact_data, error_message)
        """
        # Create artifact request message
        message = {
            "protocol": "a2a",
            "version": self.config["a2a_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": A2AMessageType.ARTIFACT_REQUEST.value,
            "source": self.config["agent_id"],
            "destination": agent_id,
            "timestamp": time.time(),
            "schema_version": self.config["schema_version"],
            "payload": {
                "artifact_id": artifact_id
            }
        }
        
        # Send message and wait for response
        response = self.send_a2a_message_sync(message, timeout)
        
        if response:
            payload = response.get("payload", {})
            
            if response.get("message_type") == A2AMessageType.ARTIFACT_TRANSFER.value:
                # Successful response
                artifact_data = payload.get("artifact_data")
                artifact_type = payload.get("artifact_type")
                encoding = payload.get("encoding")
                artifact_metadata = payload.get("artifact_metadata", {})
                
                # Decode if needed
                if encoding == "base64" and artifact_data:
                    try:
                        artifact_data = base64.b64decode(artifact_data)
                    except Exception as e:
                        return (False, None, f"Error decoding artifact: {str(e)}")
                
                # Store artifact
                try:
                    artifact_path = os.path.join(
                        self.config["artifact_storage_path"],
                        f"{artifact_id}.data"
                    )
                    
                    if isinstance(artifact_data, bytes):
                        with open(artifact_path, "wb") as f:
                            f.write(artifact_data)
                    else:
                        with open(artifact_path, "w") as f:
                            if isinstance(artifact_data, dict):
                                json.dump(artifact_data, f)
                            else:
                                f.write(str(artifact_data))
                    
                    # Store metadata
                    self.artifact_metadata[artifact_id] = {
                        "artifact_id": artifact_id,
                        "artifact_type": artifact_type,
                        "source_agent": agent_id,
                        "received_at": time.time(),
                        "file_path": artifact_path,
                        "metadata": artifact_metadata
                    }
                    
                    return (True, self.artifact_metadata[artifact_id], None)
                except Exception as e:
                    return (False, None, f"Error storing artifact: {str(e)}")
            else:
                # Error response
                error = payload.get("error", "Unknown error")
                return (False, None, error)
        else:
            return (False, None, "Timeout or communication error")
    
    def request_collaboration(
        self, 
        agent_id: str, 
        collaboration_type: str, 
        collaboration_data: Dict, 
        timeout: float = None
    ) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Request collaboration with another agent.
        
        Args:
            agent_id: Agent ID to collaborate with
            collaboration_type: Type of collaboration
            collaboration_data: Collaboration data
            timeout: Optional timeout in seconds
            
        Returns:
            Tuple of (success, collaboration_id, response_data)
        """
        # Create collaboration request message
        message = {
            "protocol": "a2a",
            "version": self.config["a2a_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": A2AMessageType.COLLABORATION_REQUEST.value,
            "source": self.config["agent_id"],
            "destination": agent_id,
            "timestamp": time.time(),
            "schema_version": self.config["schema_version"],
            "payload": {
                "collaboration_type": collaboration_type,
                "collaboration_data": collaboration_data
            }
        }
        
        # Send message and wait for response
        response = self.send_a2a_message_sync(message, timeout)
        
        if response:
            payload = response.get("payload", {})
            collaboration_id = payload.get("collaboration_id")
            status = payload.get("status")
            
            if collaboration_id and status == "accepted":
                # Store collaboration
                self.active_collaborations[collaboration_id] = {
                    "collaboration_id": collaboration_id,
                    "collaboration_type": collaboration_type,
                    "collaboration_data": collaboration_data,
                    "initiator": self.config["agent_id"],
                    "participants": [agent_id, self.config["agent_id"]],
                    "state": "active",
                    "created_at": time.time(),
                    "updated_at": time.time(),
                    "response_data": payload.get("response_data")
                }
                
                return (True, collaboration_id, payload)
            else:
                return (False, None, payload)
        else:
            return (False, None, None)
    
    def send_collaboration_update(
        self, 
        collaboration_id: str, 
        update_type: str, 
        update_data: Dict
    ) -> bool:
        """
        Send collaboration update.
        
        Args:
            collaboration_id: Collaboration ID
            update_type: Update type
            update_data: Update data
            
        Returns:
            Boolean indicating success
        """
        # Verify collaboration exists
        if collaboration_id not in self.active_collaborations:
            logger.error(f"Collaboration {collaboration_id} not found")
            return False
        
        # Get collaboration
        collaboration = self.active_collaborations[collaboration_id]
        
        # Get participants
        participants = collaboration.get("participants", [])
        
        # Create update message
        message = {
            "protocol": "a2a",
            "version": self.config["a2a_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": A2AMessageType.COLLABORATION_UPDATE.value,
            "source": self.config["agent_id"],
            "timestamp": time.time(),
            "schema_version": self.config["schema_version"],
            "payload": {
                "collaboration_id": collaboration_id,
                "update_type": update_type,
                "update_data": update_data,
                "timestamp": time.time()
            }
        }
        
        # Send to all participants except self
        success = True
        for participant in participants:
            if participant != self.config["agent_id"]:
                message_copy = message.copy()
                message_copy["destination"] = participant
                if not self.send_a2a_message(message_copy):
                    success = False
        
        # Update collaboration
        collaboration["updated_at"] = time.time()
        
        # Add update to history
        if "updates" not in collaboration:
            collaboration["updates"] = []
        
        collaboration["updates"].append({
            "update_type": update_type,
            "update_data": update_data,
            "source": self.config["agent_id"],
            "timestamp": time.time()
        })
        
        return success
    
    def get_known_agents(self, industry_tag: str = None) -> List[Dict]:
        """
        Get known agents.
        
        Args:
            industry_tag: Optional industry tag to filter by
            
        Returns:
            List of agent cards
        """
        if industry_tag:
            # Filter by industry tag
            return [
                agent for agent in self.known_agents.values()
                if industry_tag in agent.get("industry_tags", [])
            ]
        else:
            # Return all
            return list(self.known_agents.values())
    
    def get_active_tasks(self, state: str = None) -> List[Dict]:
        """
        Get active tasks.
        
        Args:
            state: Optional state to filter by
            
        Returns:
            List of active tasks
        """
        if state:
            # Filter by state
            return [
                task for task in self.active_tasks.values()
                if task.get("state") == state
            ]
        else:
            # Return all
            return list(self.active_tasks.values())
    
    def get_active_collaborations(self, collaboration_type: str = None) -> List[Dict]:
        """
        Get active collaborations.
        
        Args:
            collaboration_type: Optional collaboration type to filter by
            
        Returns:
            List of active collaborations
        """
        if collaboration_type:
            # Filter by collaboration type
            return [
                collab for collab in self.active_collaborations.values()
                if collab.get("collaboration_type") == collaboration_type
            ]
        else:
            # Return all
            return list(self.active_collaborations.values())
    
    def get_workflow_templates(self, industry_tag: str = None) -> List[Dict]:
        """
        Get workflow templates.
        
        Args:
            industry_tag: Optional industry tag to filter by
            
        Returns:
            List of workflow templates
        """
        if industry_tag:
            # Filter by industry tag
            return [
                template for template in self.workflow_templates.values()
                if industry_tag in template.get("industry_tags", [])
            ]
        else:
            # Return all
            return list(self.workflow_templates.values())
    
    def shutdown(self) -> None:
        """Shutdown the A2A Integration Manager."""
        logger.info("Shutting down A2A Integration Manager")
        
        # Stop worker threads
        self.running = False
        
        # Wait for threads to exit
        if self.outgoing_thread.is_alive():
            self.outgoing_thread.join(timeout=2)
        
        if self.discovery_thread.is_alive():
            self.discovery_thread.join(timeout=2)
        
        if self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=2)
"""
