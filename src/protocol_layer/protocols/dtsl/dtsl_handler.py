"""
Digital Twin Swarm Language (DTSL) Handler for Industriverse Protocol Layer

This module implements the handler for the Digital Twin Swarm Language (DTSL),
allowing for the declarative configuration, coordination, and orchestration
of digital twin swarms within the Industriverse ecosystem.

Features:
1. Parsing and validation of DTSL definitions (e.g., in YAML or JSON format).
2. Execution engine for DTSL scripts, managing twin lifecycles and interactions.
3. Integration with protocol components (MCP, A2A) for twin communication.
4. State management and synchronization for distributed twin swarms.
5. Dynamic adaptation of swarm behavior based on real-time data and events.
6. Interface for defining twin capabilities, relationships, and data flows.
"""

import uuid
import json
import yaml # Requires PyYAML installation
import time
import asyncio
import logging
from collections import defaultdict
from typing import Dict, List, Any, Optional, Union, Callable, Awaitable, Tuple, Set

from protocols.protocol_base import ProtocolComponent, ProtocolService, ProtocolAgent
from protocols.agent_interface import AgentTask, AgentWorkflow
from protocols.message_formats import (
    BaseMessage, RequestMessage, ResponseMessage, EventMessage,
    CommandMessage, QueryMessage, ErrorMessage, MessageFactory,
    MessagePriority, SecurityLevel, MessageStatus
)
from protocols.discovery_service import DiscoveryService, AsyncDiscoveryService
from protocols.mcp.mcp_handler import MCPHandler, AsyncMCPHandler # Assuming these exist

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=\'%(asctime)s - %(name)s - %(levelname)s - %(message)s\'
)
logger = logging.getLogger(__name__)


class DigitalTwinInstance:
    """
    Represents a running instance of a digital twin managed by DTSL.
    """
    def __init__(self, twin_id: str, twin_type: str, config: Dict[str, Any], dtsl_handler: \"DTSLHandler\"):
        self.twin_id = twin_id
        self.twin_type = twin_type
        self.config = config
        self.dtsl_handler = dtsl_handler
        self.state: Dict[str, Any] = config.get("initial_state", {})
        self.status: str = "initializing" # initializing, running, paused, stopped, error
        self.last_update: float = time.time()
        self.subscriptions: Set[str] = set() # Topics or other twins this twin subscribes to
        self.capabilities: List[str] = config.get("capabilities", [])
        self.logger = logging.getLogger(f"{__name__}.DigitalTwin.{self.twin_id[:8]}")
        self.logger.info(f"Initialized twin instance {self.twin_id} of type {self.twin_type}")

    async def update_state(self, new_state: Dict[str, Any], source: str = "internal") -> None:
        """Update the twin\"s state and potentially notify others."""
        updated = False
        for key, value in new_state.items():
            if key not in self.state or self.state[key] != value:
                self.state[key] = value
                updated = True
        
        if updated:
            self.last_update = time.time()
            self.logger.debug(f"State updated by {source}: {new_state}")
            # Publish state change event via DTSL handler/MCP
            await self.dtsl_handler.publish_twin_event(
                self.twin_id,
                "state_update",
                {"updated_state": new_state, "full_state": self.state}
            )

    async def process_message(self, message: BaseMessage) -> Optional[BaseMessage]:
        """Process an incoming message directed to this twin."""
        self.logger.debug(f"Received message: {message.message_type} from {message.sender_id}")
        # Placeholder for twin-specific message handling logic
        # This could involve updating state, triggering actions, etc.
        if isinstance(message, CommandMessage):
            if message.command == "set_state":
                await self.update_state(message.params, source=message.sender_id)
                return MessageFactory.create_response(message.message_id, MessageStatus.SUCCESS)
            elif message.command == "get_state":
                return MessageFactory.create_response(message.message_id, MessageStatus.SUCCESS, self.state)
            elif message.command == "start":
                self.status = "running"
                self.logger.info("Twin started")
                await self.dtsl_handler.publish_twin_event(self.twin_id, "status_change", {"status": self.status})
                return MessageFactory.create_response(message.message_id, MessageStatus.SUCCESS)
            elif message.command == "stop":
                self.status = "stopped"
                self.logger.info("Twin stopped")
                await self.dtsl_handler.publish_twin_event(self.twin_id, "status_change", {"status": self.status})
                return MessageFactory.create_response(message.message_id, MessageStatus.SUCCESS)
        
        return MessageFactory.create_error("unsupported_operation", f"Operation not supported by twin {self.twin_id}", related_message_id=message.message_id)

    def get_status(self) -> Dict[str, Any]:
        return {
            "twin_id": self.twin_id,
            "twin_type": self.twin_type,
            "status": self.status,
            "state": self.state,
            "last_update": self.last_update,
            "capabilities": self.capabilities
        }


class DTSLHandler(ProtocolService):
    """
    Handles the parsing, validation, and execution of DTSL definitions.
    Manages the lifecycle and interactions of digital twin swarms.
    """
    
    def __init__(
        self,
        service_id: str = None,
        mcp_handler: Union[MCPHandler, AsyncMCPHandler] = None,
        discovery_service: Union[DiscoveryService, AsyncDiscoveryService] = None,
        config: Dict[str, Any] = None
    ):
        super().__init__(service_id or str(uuid.uuid4()), "dtsl_handler")
        self.mcp_handler = mcp_handler
        self.discovery_service = discovery_service
        self.config = config or {}
        
        self.twin_definitions: Dict[str, Dict[str, Any]] = {} # twin_type -> definition
        self.swarm_definitions: Dict[str, Dict[str, Any]] = {} # swarm_id -> definition
        self.running_twins: Dict[str, DigitalTwinInstance] = {} # twin_id -> instance
        self.running_swarms: Dict[str, Dict[str, Any]] = {} # swarm_id -> runtime_info
        
        self.is_async = isinstance(mcp_handler, AsyncMCPHandler)
        self.lock = asyncio.Lock() if self.is_async else None # Use lock for async operations
        
        self.logger = logging.getLogger(f"{__name__}.DTSLHandler.{self.component_id[:8]}")
        self.logger.info(f"DTSL Handler initialized (Async: {self.is_async}) with ID {self.component_id}")
        
        # Add capabilities
        self.add_capability("dtsl_parsing", "Parse and validate DTSL definitions")
        self.add_capability("dtsl_execution", "Execute DTSL scripts and manage swarms")
        self.add_capability("twin_lifecycle_management", "Manage digital twin instances")
        self.add_capability("swarm_coordination", "Coordinate interactions within and between swarms")

    # --- Definition Management ---

    def load_twin_definition(self, twin_type: str, definition: Dict[str, Any]) -> bool:
        """Load or update a digital twin type definition."""
        # TODO: Add validation against a DTSL schema
        self.twin_definitions[twin_type] = definition
        self.logger.info(f"Loaded definition for twin type: {twin_type}")
        return True

    def load_swarm_definition(self, swarm_id: str, definition: Dict[str, Any]) -> bool:
        """Load or update a swarm definition."""
        # TODO: Add validation against a DTSL schema
        if "twins" not in definition or not isinstance(definition["twins"], list):
            self.logger.error(f"Invalid swarm definition for {swarm_id}: missing or invalid \"twins\" list.")
            return False
        self.swarm_definitions[swarm_id] = definition
        self.logger.info(f"Loaded definition for swarm: {swarm_id}")
        return True

    def parse_dtsl_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse a DTSL file (assuming YAML or JSON)."""
        try:
            with open(file_path, \"r\") as f:
                if file_path.endswith(\".yaml\") or file_path.endswith(\".yml\"):
                    content = yaml.safe_load(f)
                elif file_path.endswith(\".json\"):
                    content = json.load(f)
                else:
                    self.logger.error(f"Unsupported file type for DTSL: {file_path}")
                    return None
            # TODO: Validate content against DTSL schema
            return content
        except FileNotFoundError:
            self.logger.error(f"DTSL file not found: {file_path}")
            return None
        except Exception as e:
            self.logger.exception(f"Error parsing DTSL file {file_path}: {e}")
            return None

    # --- Swarm and Twin Lifecycle Management (Async versions) ---

    async def _create_twin_instance(self, twin_config: Dict[str, Any]) -> Optional[DigitalTwinInstance]:
        twin_id = twin_config.get("id", str(uuid.uuid4()))
        twin_type = twin_config.get("type")
        
        if not twin_type:
            self.logger.error("Twin config missing \"type\"")
            return None
            
        if twin_type not in self.twin_definitions:
            self.logger.error(f"Unknown twin type: {twin_type}")
            return None
            
        definition = self.twin_definitions[twin_type]
        # Merge definition config with instance config (instance overrides)
        full_config = {**definition.get("config", {}), **twin_config.get("config", {})}
        full_config["initial_state"] = {**definition.get("initial_state", {}), **twin_config.get("initial_state", {})}
        full_config["capabilities"] = list(set(definition.get("capabilities", []) + twin_config.get("capabilities", [])))

        async with self.lock:
            if twin_id in self.running_twins:
                self.logger.warning(f"Twin instance {twin_id} already exists.")
                return self.running_twins[twin_id]
            
            instance = DigitalTwinInstance(twin_id, twin_type, full_config, self)
            self.running_twins[twin_id] = instance
            instance.status = "running" # Mark as running immediately after creation
            await self.publish_twin_event(twin_id, "twin_created", instance.get_status())
            await self.publish_twin_event(twin_id, "status_change", {"status": instance.status})
            return instance

    async def start_swarm(self, swarm_id: str) -> bool:
        """Start a defined swarm."""
        if swarm_id not in self.swarm_definitions:
            self.logger.error(f"Swarm definition not found: {swarm_id}")
            return False
            
        async with self.lock:
            if swarm_id in self.running_swarms:
                self.logger.warning(f"Swarm {swarm_id} is already running.")
                return True
            
            definition = self.swarm_definitions[swarm_id]
            self.running_swarms[swarm_id] = {
                "definition": definition,
                "status": "starting",
                "twin_ids": set(),
                "start_time": time.time()
            }

        self.logger.info(f"Starting swarm: {swarm_id}")
        twin_creation_tasks = []
        for twin_config in definition.get("twins", []):
            twin_creation_tasks.append(self._create_twin_instance(twin_config))
            
        results = await asyncio.gather(*twin_creation_tasks, return_exceptions=True)
        
        created_twin_ids = set()
        has_errors = False
        for i, result in enumerate(results):
            if isinstance(result, DigitalTwinInstance):
                created_twin_ids.add(result.twin_id)
            else:
                has_errors = True
                twin_config = definition["twins"][i]
                self.logger.error(f"Failed to create twin {twin_config.get(\"id\")} of type {twin_config.get(\"type\")}: {result}")

        async with self.lock:
            if swarm_id in self.running_swarms:
                 self.running_swarms[swarm_id]["twin_ids"] = created_twin_ids
                 self.running_swarms[swarm_id]["status"] = "error" if has_errors else "running"
                 self.logger.info(f"Swarm {swarm_id} started. Status: {self.running_swarms[swarm_id][\"status\"]}. Twins: {len(created_twin_ids)}")
                 await self.publish_swarm_event(swarm_id, "swarm_status_change", {"status": self.running_swarms[swarm_id]["status"]})
                 return not has_errors
            else:
                 # Swarm might have been stopped concurrently
                 self.logger.warning(f"Swarm {swarm_id} was stopped during startup.")
                 # Clean up twins created for this swarm if necessary
                 cleanup_tasks = [self.stop_twin(tid) for tid in created_twin_ids]
                 await asyncio.gather(*cleanup_tasks)
                 return False

    async def stop_swarm(self, swarm_id: str) -> bool:
        """Stop a running swarm and its associated twins."""
        async with self.lock:
            if swarm_id not in self.running_swarms:
                self.logger.warning(f"Swarm {swarm_id} is not running.")
                return True
            
            swarm_info = self.running_swarms.pop(swarm_id)
            twin_ids_to_stop = swarm_info.get("twin_ids", set())
            swarm_info["status"] = "stopping"
            await self.publish_swarm_event(swarm_id, "swarm_status_change", {"status": "stopping"})

        self.logger.info(f"Stopping swarm: {swarm_id}")
        stop_tasks = [self.stop_twin(twin_id) for twin_id in twin_ids_to_stop]
        await asyncio.gather(*stop_tasks, return_exceptions=True)
        
        self.logger.info(f"Swarm {swarm_id} stopped.")
        await self.publish_swarm_event(swarm_id, "swarm_status_change", {"status": "stopped"})
        return True

    async def stop_twin(self, twin_id: str) -> bool:
        """Stop a specific twin instance."""
        async with self.lock:
            if twin_id not in self.running_twins:
                self.logger.warning(f"Twin {twin_id} not found or already stopped.")
                return True
            instance = self.running_twins.pop(twin_id)
            instance.status = "stopped"
        
        self.logger.info(f"Stopped twin: {twin_id}")
        await self.publish_twin_event(twin_id, "status_change", {"status": "stopped"})
        await self.publish_twin_event(twin_id, "twin_deleted", {"twin_id": twin_id})
        # TODO: Add any necessary cleanup logic for the twin
        return True

    # --- Communication and Event Handling (Async) ---

    async def publish_twin_event(self, twin_id: str, event_type: str, payload: Dict[str, Any]) -> None:
        """Publish an event originating from a twin."""
        if not self.mcp_handler:
            self.logger.warning("MCP Handler not configured, cannot publish twin event")
            return
            
        event_message = MessageFactory.create_event(
            event_type=f"dtsl.twin.{event_type}",
            payload=payload,
            sender_id=twin_id, # Event source is the twin itself
            metadata={"origin_service": self.component_id}
        )
        # Publish to a general twin topic or specific subscribers
        # For simplicity, broadcast via MCP handler (assuming it handles pub/sub)
        await self.mcp_handler.publish_message(event_message, topic=f"dtsl/twins/{twin_id}/events")
        self.logger.debug(f"Published twin event: {event_type} for {twin_id}")

    async def publish_swarm_event(self, swarm_id: str, event_type: str, payload: Dict[str, Any]) -> None:
        """Publish an event related to a swarm."""
        if not self.mcp_handler:
            self.logger.warning("MCP Handler not configured, cannot publish swarm event")
            return
            
        event_message = MessageFactory.create_event(
            event_type=f"dtsl.swarm.{event_type}",
            payload=payload,
            sender_id=self.component_id, # Event source is the handler
            metadata={"swarm_id": swarm_id}
        )
        await self.mcp_handler.publish_message(event_message, topic=f"dtsl/swarms/{swarm_id}/events")
        self.logger.debug(f"Published swarm event: {event_type} for {swarm_id}")

    async def route_message_to_twin(self, message: BaseMessage) -> Optional[BaseMessage]:
        """Route an incoming message to the appropriate twin instance."""
        target_twin_id = message.receiver_id
        instance = None
        async with self.lock:
            if target_twin_id in self.running_twins:
                instance = self.running_twins[target_twin_id]
            
        if instance:
            if instance.status == "running":
                try:
                    response = await instance.process_message(message)
                    return response
                except Exception as e:
                    instance.logger.exception(f"Error processing message: {e}")
                    instance.status = "error"
                    await self.publish_twin_event(instance.twin_id, "status_change", {"status": "error", "error": str(e)})
                    return MessageFactory.create_error("twin_processing_error", str(e), related_message_id=message.message_id)
            else:
                self.logger.warning(f"Message received for non-running twin {target_twin_id} (status: {instance.status})")
                return MessageFactory.create_error("twin_not_running", f"Twin {target_twin_id} is not running (status: {instance.status})", related_message_id=message.message_id)
        else:
            self.logger.error(f"Target twin instance not found: {target_twin_id}")
            return MessageFactory.create_error("twin_not_found", f"Twin instance {target_twin_id} not found", related_message_id=message.message_id)

    # --- ProtocolService Methods (Async) ---

    async def process_message_async(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process messages directed to the DTSL handler or managed twins."""
        msg_obj = MessageFactory.create_from_dict(message)
        if not msg_obj:
            return MessageFactory.create_error("invalid_message", "Could not parse message").to_dict()

        response_payload = None
        status = MessageStatus.SUCCESS
        response_obj = None

        # Check if message is for a specific twin
        async with self.lock:
             is_for_twin = msg_obj.receiver_id in self.running_twins

        if is_for_twin:
            response_obj = await self.route_message_to_twin(msg_obj)
        
        # Else, process message for the handler itself
        elif isinstance(msg_obj, CommandMessage):
            if msg_obj.command == "load_twin_definition":
                params = msg_obj.params
                if "twin_type" in params and "definition" in params:
                    success = self.load_twin_definition(params["twin_type"], params["definition"])
                    response_payload = {"status": "twin_definition_loaded" if success else "load_failed"}
                    if not success: status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing twin_type or definition"}
            elif msg_obj.command == "load_swarm_definition":
                params = msg_obj.params
                if "swarm_id" in params and "definition" in params:
                    success = self.load_swarm_definition(params["swarm_id"], params["definition"])
                    response_payload = {"status": "swarm_definition_loaded" if success else "load_failed"}
                    if not success: status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing swarm_id or definition"}
            elif msg_obj.command == "start_swarm":
                params = msg_obj.params
                if "swarm_id" in params:
                    success = await self.start_swarm(params["swarm_id"])
                    response_payload = {"status": "swarm_started" if success else "start_failed"}
                    if not success: status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing swarm_id"}
            elif msg_obj.command == "stop_swarm":
                params = msg_obj.params
                if "swarm_id" in params:
                    success = await self.stop_swarm(params["swarm_id"])
                    response_payload = {"status": "swarm_stopped" if success else "stop_failed"}
                    if not success: status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing swarm_id"}
            elif msg_obj.command == "create_twin": # Allow creating individual twins
                 params = msg_obj.params
                 if "config" in params:
                     instance = await self._create_twin_instance(params["config"])
                     if instance:
                         response_payload = {"status": "twin_created", "twin_id": instance.twin_id}
                     else:
                         status = MessageStatus.FAILED
                         response_payload = {"error": "Failed to create twin"}
                 else:
                     status = MessageStatus.FAILED
                     response_payload = {"error": "Missing twin config"}
            elif msg_obj.command == "stop_twin":
                 params = msg_obj.params
                 if "twin_id" in params:
                     success = await self.stop_twin(params["twin_id"])
                     response_payload = {"status": "twin_stopped" if success else "stop_failed"}
                     if not success: status = MessageStatus.FAILED
                 else:
                     status = MessageStatus.FAILED
                     response_payload = {"error": "Missing twin_id"}
            else:
                status = MessageStatus.FAILED
                response_payload = {"error": f"Unsupported command: {msg_obj.command}"}
        
        elif isinstance(msg_obj, QueryMessage):
            async with self.lock:
                if msg_obj.query == "get_twin_definitions":
                    response_payload = self.twin_definitions
                elif msg_obj.query == "get_swarm_definitions":
                    response_payload = self.swarm_definitions
                elif msg_obj.query == "get_running_twins":
                    response_payload = {tid: twin.get_status() for tid, twin in self.running_twins.items()}
                elif msg_obj.query == "get_running_swarms":
                    response_payload = self.running_swarms
                elif msg_obj.query == "get_twin_status":
                    params = msg_obj.params
                    if "twin_id" in params:
                        twin = self.running_twins.get(params["twin_id"])
                        response_payload = twin.get_status() if twin else None
                        if twin is None: status = MessageStatus.FAILED
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Missing twin_id"}
                elif msg_obj.query == "get_swarm_status":
                    params = msg_obj.params
                    if "swarm_id" in params:
                        response_payload = self.running_swarms.get(params["swarm_id"])
                        if response_payload is None: status = MessageStatus.FAILED
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Missing swarm_id"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": f"Unsupported query: {msg_obj.query}"}
        else:
            # Ignore other message types for the handler itself
            return None

        # Create response if not already handled by twin routing
        if response_obj:
            return response_obj.to_dict() if response_obj else None
        else:
            response = MessageFactory.create_response(
                correlation_id=msg_obj.message_id,
                status=status,
                payload=response_payload,
                sender_id=self.component_id,
                receiver_id=msg_obj.sender_id
            )
            return response.to_dict()

    def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.is_async:
            # Synchronous execution (basic implementation, might block)
            # Consider using a thread pool for actual sync execution
            self.logger.warning("Running DTSL handler synchronously - may block")
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(self.process_message_async(message))
            finally:
                loop.close()
        else:
            # Should be called via process_message_async in async environments
            self.logger.error("process_message called directly on Async DTSL Handler")
            return MessageFactory.create_error("internal_error", "Incorrect async method call").to_dict()

    async def health_check(self) -> Dict[str, Any]:
        async with self.lock:
            num_twin_defs = len(self.twin_definitions)
            num_swarm_defs = len(self.swarm_definitions)
            num_running_twins = len(self.running_twins)
            num_running_swarms = len(self.running_swarms)
            num_error_twins = sum(1 for t in self.running_twins.values() if t.status == \"error\")
        
        return {
            "status": "healthy",
            "twin_definitions": num_twin_defs,
            "swarm_definitions": num_swarm_defs,
            "running_twins": num_running_twins,
            "running_swarms": num_running_swarms,
            "error_twins": num_error_twins,
            "mcp_handler_status": "configured" if self.mcp_handler else "not_configured",
            "discovery_service_status": "configured" if self.discovery_service else "not_configured"
        }

    async def get_manifest(self) -> Dict[str, Any]:
        manifest = await super().get_manifest()
        health = await self.health_check()
        manifest.update(health)
        return manifest

"""
