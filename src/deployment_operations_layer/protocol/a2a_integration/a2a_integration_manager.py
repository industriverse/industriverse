"""
A2A Integration Manager

This module manages the integration with the Agent-to-Agent (A2A) Protocol for the Deployment Operations Layer.
It provides standardized communication between agents across different layers and environments.
"""

import logging
import json
import os
import uuid
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class A2AIntegrationManager:
    """
    Manager for A2A protocol integration.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the A2A Integration Manager.
        
        Args:
            config_path: Path to A2A configuration file
        """
        self.config_path = config_path or os.environ.get(
            "A2A_CONFIG_PATH", "/var/lib/industriverse/protocol/a2a_config.json"
        )
        self.config = self._load_config()
        self.session_id = str(uuid.uuid4())
        logger.info("A2A Integration Manager initialized with session ID: %s", self.session_id)
    
    def register_agent(self, 
                     agent_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register an agent with the A2A protocol.
        
        Args:
            agent_definition: Agent definition
            
        Returns:
            Dict containing the registration result
        """
        logger.info(f"Registering agent: {agent_definition.get('name', 'unnamed')}")
        
        try:
            # Validate agent definition
            validation_result = self._validate_agent_definition(agent_definition)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"]
                }
            
            # Generate agent ID if not provided
            if "id" not in agent_definition:
                agent_definition["id"] = str(uuid.uuid4())
            
            # Add registration metadata
            agent_definition["registration"] = {
                "timestamp": self._get_timestamp(),
                "session_id": self.session_id,
                "layer": "deployment_ops"
            }
            
            # Register the agent
            self._register_agent(agent_definition)
            
            return {
                "success": True,
                "agent_id": agent_definition["id"],
                "agent": agent_definition
            }
            
        except Exception as e:
            logger.exception(f"Error registering agent: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: ID of the agent to get
            
        Returns:
            Dict containing the agent
        """
        logger.info(f"Getting agent: {agent_id}")
        
        try:
            # Get the agent
            agent = self._get_agent(agent_id)
            if not agent:
                return {
                    "success": False,
                    "error": f"Agent not found: {agent_id}"
                }
            
            return {
                "success": True,
                "agent": agent
            }
            
        except Exception as e:
            logger.exception(f"Error getting agent: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_agent(self, 
                   agent_id: str, 
                   agent_updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an agent.
        
        Args:
            agent_id: ID of the agent to update
            agent_updates: Updates to apply
            
        Returns:
            Dict containing the update result
        """
        logger.info(f"Updating agent: {agent_id}")
        
        try:
            # Get the agent
            agent = self._get_agent(agent_id)
            if not agent:
                return {
                    "success": False,
                    "error": f"Agent not found: {agent_id}"
                }
            
            # Apply updates
            for key, value in agent_updates.items():
                if key != "id" and key != "registration":
                    if isinstance(value, dict) and key in agent and isinstance(agent[key], dict):
                        # Merge dictionaries
                        agent[key].update(value)
                    else:
                        # Replace value
                        agent[key] = value
            
            # Update registration metadata
            agent["registration"]["updated_at"] = self._get_timestamp()
            
            # Register the updated agent
            self._register_agent(agent)
            
            return {
                "success": True,
                "agent_id": agent_id,
                "agent": agent
            }
            
        except Exception as e:
            logger.exception(f"Error updating agent: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_agents(self, 
                  filter_criteria: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List registered agents.
        
        Args:
            filter_criteria: Optional filter criteria
            
        Returns:
            Dict containing the agents
        """
        logger.info("Listing agents")
        
        try:
            # Get all agents
            agents = self._list_agents()
            
            # Apply filter criteria
            if filter_criteria:
                filtered_agents = []
                for agent in agents:
                    match = True
                    for key, value in filter_criteria.items():
                        if key not in agent or agent[key] != value:
                            match = False
                            break
                    if match:
                        filtered_agents.append(agent)
                agents = filtered_agents
            
            return {
                "success": True,
                "agents": agents
            }
            
        except Exception as e:
            logger.exception(f"Error listing agents: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_message(self, 
                   source_agent_id: str, 
                   target_agent_id: str,
                   message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message from one agent to another.
        
        Args:
            source_agent_id: ID of the source agent
            target_agent_id: ID of the target agent
            message: Message to send
            
        Returns:
            Dict containing the send result
        """
        logger.info(f"Sending message from {source_agent_id} to {target_agent_id}")
        
        try:
            # Validate source agent
            source_agent = self._get_agent(source_agent_id)
            if not source_agent:
                return {
                    "success": False,
                    "error": f"Source agent not found: {source_agent_id}"
                }
            
            # Validate target agent
            target_agent = self._get_agent(target_agent_id)
            if not target_agent:
                return {
                    "success": False,
                    "error": f"Target agent not found: {target_agent_id}"
                }
            
            # Generate message ID if not provided
            if "id" not in message:
                message["id"] = str(uuid.uuid4())
            
            # Add message metadata
            message["metadata"] = message.get("metadata", {})
            message["metadata"].update({
                "timestamp": self._get_timestamp(),
                "source_agent_id": source_agent_id,
                "target_agent_id": target_agent_id,
                "session_id": self.session_id
            })
            
            # Send the message
            send_result = self._send_message(source_agent, target_agent, message)
            
            if not send_result["success"]:
                return {
                    "success": False,
                    "error": send_result["error"]
                }
            
            return {
                "success": True,
                "message_id": message["id"],
                "source_agent_id": source_agent_id,
                "target_agent_id": target_agent_id
            }
            
        except Exception as e:
            logger.exception(f"Error sending message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def receive_message(self, 
                      target_agent_id: str, 
                      message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receive a message for an agent.
        
        Args:
            target_agent_id: ID of the target agent
            message: Message to receive
            
        Returns:
            Dict containing the receive result
        """
        logger.info(f"Receiving message for {target_agent_id}")
        
        try:
            # Validate target agent
            target_agent = self._get_agent(target_agent_id)
            if not target_agent:
                return {
                    "success": False,
                    "error": f"Target agent not found: {target_agent_id}"
                }
            
            # Generate message ID if not provided
            if "id" not in message:
                message["id"] = str(uuid.uuid4())
            
            # Add message metadata
            message["metadata"] = message.get("metadata", {})
            message["metadata"].update({
                "received_at": self._get_timestamp(),
                "target_agent_id": target_agent_id,
                "session_id": self.session_id
            })
            
            # Process the message
            process_result = self._process_message(target_agent, message)
            
            if not process_result["success"]:
                return {
                    "success": False,
                    "error": process_result["error"]
                }
            
            return {
                "success": True,
                "message_id": message["id"],
                "target_agent_id": target_agent_id,
                "processed": True
            }
            
        except Exception as e:
            logger.exception(f"Error receiving message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_agent_card(self, 
                        agent_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an agent card for A2A protocol.
        
        Args:
            agent_definition: Agent definition
            
        Returns:
            Dict containing the agent card
        """
        logger.info(f"Creating agent card for: {agent_definition.get('name', 'unnamed')}")
        
        try:
            # Extract required fields
            name = agent_definition.get("name", "Unnamed Agent")
            description = agent_definition.get("description", "")
            agent_id = agent_definition.get("id", str(uuid.uuid4()))
            
            # Get capabilities
            capabilities = agent_definition.get("capabilities", [])
            
            # Create the agent card
            agent_card = {
                "agentId": agent_id,
                "displayName": name,
                "description": description,
                "capabilities": capabilities,
                "industryTags": agent_definition.get("industry_tags", []),
                "priority": agent_definition.get("priority", "medium"),
                "version": "1.0",
                "apiVersion": "v1"
            }
            
            # Add logo if available
            if "logo_url" in agent_definition:
                agent_card["logoUrl"] = agent_definition["logo_url"]
            
            # Add contact info if available
            if "contact_email" in agent_definition:
                agent_card["contactEmail"] = agent_definition["contact_email"]
            
            # Add workflow templates if available
            if "workflow_templates" in agent_definition:
                agent_card["workflowTemplates"] = agent_definition["workflow_templates"]
            
            return {
                "success": True,
                "agent_card": agent_card
            }
            
        except Exception as e:
            logger.exception(f"Error creating agent card: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load A2A configuration from file.
        
        Returns:
            Dict containing A2A configuration
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"A2A configuration file not found: {self.config_path}")
                return self._get_default_config()
                
        except Exception as e:
            logger.exception(f"Error loading A2A configuration: {str(e)}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default A2A configuration.
        
        Returns:
            Dict containing default A2A configuration
        """
        return {
            "protocol_version": "1.0",
            "api_version": "v1",
            "discovery": {
                "enabled": True,
                "method": "registry"
            },
            "authentication": {
                "enabled": True,
                "method": "token"
            },
            "message_delivery": {
                "retry_count": 3,
                "retry_delay": 5,
                "timeout": 30
            },
            "extensions": {
                "industry_tags": {
                    "enabled": True,
                    "version": "1.0"
                },
                "priority": {
                    "enabled": True,
                    "version": "1.0"
                },
                "workflow_templates": {
                    "enabled": True,
                    "version": "1.0"
                }
            }
        }
    
    def _validate_agent_definition(self, agent_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate an agent definition.
        
        Args:
            agent_definition: Agent definition to validate
            
        Returns:
            Dict containing validation result
        """
        # Check required fields
        required_fields = ["name", "description", "capabilities"]
        for field in required_fields:
            if field not in agent_definition:
                return {
                    "valid": False,
                    "error": f"Missing required field: {field}"
                }
        
        # Validate capabilities
        capabilities = agent_definition.get("capabilities", [])
        if not isinstance(capabilities, list):
            return {
                "valid": False,
                "error": "Capabilities must be a list"
            }
        
        # In a real implementation, this would perform more detailed validation
        
        return {
            "valid": True
        }
    
    def _register_agent(self, agent: Dict[str, Any]):
        """
        Register an agent in the storage.
        
        Args:
            agent: Agent to register
        """
        # In a real implementation, this would store the agent in a database or other storage
        # For this implementation, we'll just log it
        logger.info(f"Registered A2A agent: {agent['id']}")
    
    def _get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an agent from storage.
        
        Args:
            agent_id: ID of the agent to get
            
        Returns:
            Agent if found, None otherwise
        """
        # In a real implementation, this would retrieve the agent from a database or other storage
        # For this implementation, we'll just return a simulated agent
        return {
            "id": agent_id,
            "name": "Simulated Agent",
            "description": "This is a simulated agent for demonstration purposes",
            "capabilities": ["deployment", "monitoring", "recovery"],
            "registration": {
                "timestamp": self._get_timestamp(),
                "session_id": self.session_id,
                "layer": "deployment_ops"
            }
        }
    
    def _list_agents(self) -> List[Dict[str, Any]]:
        """
        List agents from storage.
        
        Returns:
            List of agents
        """
        # In a real implementation, this would retrieve agents from a database or other storage
        # For this implementation, we'll just return simulated agents
        return [
            {
                "id": str(uuid.uuid4()),
                "name": "Deployer Agent",
                "description": "Agent responsible for deployment operations",
                "capabilities": ["deployment", "rollback", "verification"],
                "registration": {
                    "timestamp": self._get_timestamp(),
                    "session_id": self.session_id,
                    "layer": "deployment_ops"
                }
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Monitor Agent",
                "description": "Agent responsible for monitoring deployments",
                "capabilities": ["monitoring", "alerting", "reporting"],
                "registration": {
                    "timestamp": self._get_timestamp(),
                    "session_id": self.session_id,
                    "layer": "deployment_ops"
                }
            }
        ]
    
    def _send_message(self, 
                    source_agent: Dict[str, Any], 
                    target_agent: Dict[str, Any],
                    message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message from one agent to another.
        
        Args:
            source_agent: Source agent
            target_agent: Target agent
            message: Message to send
            
        Returns:
            Dict containing the send result
        """
        # In a real implementation, this would use the A2A protocol to send the message
        # For this implementation, we'll just return a simulated result
        return {
            "success": True,
            "message_id": message["id"]
        }
    
    def _process_message(self, 
                       target_agent: Dict[str, Any], 
                       message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message for an agent.
        
        Args:
            target_agent: Target agent
            message: Message to process
            
        Returns:
            Dict containing the process result
        """
        # In a real implementation, this would process the message according to the A2A protocol
        # For this implementation, we'll just return a simulated result
        return {
            "success": True,
            "message_id": message["id"]
        }
    
    def _get_timestamp(self):
        """Get the current timestamp."""
        import datetime
        return datetime.datetime.utcnow().isoformat()
