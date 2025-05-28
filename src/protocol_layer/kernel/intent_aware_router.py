"""
Intent-Aware Router for Industriverse Protocol Layer

This module implements the Intent-Aware Router component of the Protocol Kernel Intelligence,
enabling semantic understanding and intelligent routing of protocol messages based on intent.

Features:
1. Intent extraction from protocol messages
2. Semantic understanding of message content
3. Intelligent routing based on intent and context
4. Adaptive learning from routing patterns
5. Integration with Protocol Kernel Intelligence
"""

import uuid
import time
import asyncio
import logging
import json
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Callable, Awaitable, Tuple, Set
from dataclasses import dataclass, field

from protocols.protocol_base import ProtocolComponent, ProtocolService
from protocols.message_formats import (
    BaseMessage, RequestMessage, ResponseMessage, EventMessage,
    CommandMessage, QueryMessage, ErrorMessage, MessageFactory,
    MessagePriority, SecurityLevel, MessageStatus
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntentCategory(Enum):
    """Categories of message intents."""
    QUERY = "query"
    COMMAND = "command"
    NOTIFICATION = "notification"
    DATA_TRANSFER = "data_transfer"
    CONTROL = "control"
    DISCOVERY = "discovery"
    NEGOTIATION = "negotiation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    MONITORING = "monitoring"
    UNKNOWN = "unknown"


class RoutingStrategy(Enum):
    """Strategies for message routing."""
    DIRECT = "direct"  # Direct to specified receiver
    BROADCAST = "broadcast"  # Broadcast to all matching components
    MULTICAST = "multicast"  # Send to a specific group
    NEAREST = "nearest"  # Send to nearest matching component
    LOAD_BALANCED = "load_balanced"  # Distribute among matching components
    CAPABILITY_BASED = "capability_based"  # Route based on capabilities
    INTENT_BASED = "intent_based"  # Route based on intent analysis
    CONTEXT_AWARE = "context_aware"  # Route based on context
    ADAPTIVE = "adaptive"  # Adapt based on historical patterns


@dataclass
class IntentAnalysis:
    """
    Represents the analysis of a message's intent.
    """
    message_id: str
    primary_intent: IntentCategory
    confidence: float  # 0.0 - 1.0
    secondary_intents: Dict[IntentCategory, float] = field(default_factory=dict)
    extracted_entities: Dict[str, Any] = field(default_factory=dict)
    context_factors: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "message_id": self.message_id,
            "primary_intent": self.primary_intent.value,
            "confidence": self.confidence,
            "secondary_intents": {intent.value: conf for intent, conf in self.secondary_intents.items()},
            "extracted_entities": self.extracted_entities,
            "context_factors": self.context_factors,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IntentAnalysis':
        """Create from dictionary representation."""
        analysis = cls(
            message_id=data["message_id"],
            primary_intent=IntentCategory(data["primary_intent"]),
            confidence=data["confidence"],
            extracted_entities=data.get("extracted_entities", {}),
            context_factors=data.get("context_factors", {}),
            timestamp=data.get("timestamp", time.time())
        )
        for intent_str, conf in data.get("secondary_intents", {}).items():
            analysis.secondary_intents[IntentCategory(intent_str)] = conf
        return analysis


@dataclass
class RoutingDecision:
    """
    Represents a routing decision for a message.
    """
    message_id: str
    strategy: RoutingStrategy
    target_components: List[str]
    priority: MessagePriority
    intent_analysis_id: Optional[str] = None
    reasoning: str = ""
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "message_id": self.message_id,
            "strategy": self.strategy.value,
            "target_components": self.target_components,
            "priority": self.priority.value,
            "intent_analysis_id": self.intent_analysis_id,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RoutingDecision':
        """Create from dictionary representation."""
        return cls(
            message_id=data["message_id"],
            strategy=RoutingStrategy(data["strategy"]),
            target_components=data["target_components"],
            priority=MessagePriority(data["priority"]),
            intent_analysis_id=data.get("intent_analysis_id"),
            reasoning=data.get("reasoning", ""),
            timestamp=data.get("timestamp", time.time())
        )


class IntentAwareRouter(ProtocolService):
    """
    Service for intent-aware routing of protocol messages.
    """
    
    def __init__(
        self,
        service_id: str = None,
        config: Dict[str, Any] = None
    ):
        super().__init__(service_id or str(uuid.uuid4()), "intent_aware_router")
        self.config = config or {}
        
        # Initialize storage
        self.intent_analyses: Dict[str, IntentAnalysis] = {}
        self.routing_decisions: Dict[str, RoutingDecision] = {}
        self.routing_history: List[Dict[str, Any]] = []
        
        # Component registry (would be populated from discovery service)
        self.component_registry: Dict[str, Dict[str, Any]] = {}
        
        # State
        self.is_async = True
        self.lock = asyncio.Lock()
        
        self.logger = logging.getLogger(f"{__name__}.IntentAwareRouter.{self.component_id[:8]}")
        self.logger.info(f"Intent-Aware Router initialized with ID {self.component_id}")
        
        # Add capabilities
        self.add_capability("intent_analysis", "Analyze message intent")
        self.add_capability("intelligent_routing", "Route messages based on intent")
        self.add_capability("adaptive_learning", "Learn from routing patterns")
        self.add_capability("context_awareness", "Consider context in routing decisions")

    async def initialize(self) -> bool:
        """Initialize the router service."""
        self.logger.info("Initializing Intent-Aware Router")
        
        # Load initial component registry if provided
        initial_registry = self.config.get("initial_registry", {})
        for component_id, component_info in initial_registry.items():
            self.component_registry[component_id] = component_info
        
        self.logger.info(f"Intent-Aware Router initialized with {len(self.component_registry)} registered components")
        return True

    # --- Intent Analysis ---

    async def analyze_intent(self, message: Dict[str, Any]) -> IntentAnalysis:
        """Analyze the intent of a message."""
        msg_obj = MessageFactory.create_from_dict(message)
        if not msg_obj:
            self.logger.error("Invalid message for intent analysis")
            return IntentAnalysis(
                message_id=message.get("message_id", str(uuid.uuid4())),
                primary_intent=IntentCategory.UNKNOWN,
                confidence=0.0
            )
        
        # Extract basic message properties
        message_id = msg_obj.message_id
        message_type = type(msg_obj).__name__
        
        # Determine primary intent based on message type
        primary_intent = IntentCategory.UNKNOWN
        confidence = 0.7  # Default confidence
        secondary_intents = {}
        extracted_entities = {}
        
        if isinstance(msg_obj, CommandMessage):
            primary_intent = IntentCategory.COMMAND
            confidence = 0.9
            extracted_entities["command"] = msg_obj.command
            extracted_entities["params"] = msg_obj.params
            
            # Add secondary intents based on command
            if msg_obj.command.startswith("get_"):
                secondary_intents[IntentCategory.QUERY] = 0.4
            elif msg_obj.command.startswith("monitor_"):
                secondary_intents[IntentCategory.MONITORING] = 0.5
            elif msg_obj.command.startswith("discover_"):
                secondary_intents[IntentCategory.DISCOVERY] = 0.6
        
        elif isinstance(msg_obj, QueryMessage):
            primary_intent = IntentCategory.QUERY
            confidence = 0.9
            extracted_entities["query"] = msg_obj.query
            extracted_entities["params"] = msg_obj.params
            
            # Add secondary intents based on query
            if msg_obj.query.startswith("find_"):
                secondary_intents[IntentCategory.DISCOVERY] = 0.6
            elif msg_obj.query.startswith("status_"):
                secondary_intents[IntentCategory.MONITORING] = 0.5
        
        elif isinstance(msg_obj, EventMessage):
            primary_intent = IntentCategory.NOTIFICATION
            confidence = 0.8
            extracted_entities["event_type"] = msg_obj.event_type
            extracted_entities["payload"] = msg_obj.payload
            
            # Add secondary intents based on event type
            if msg_obj.event_type.startswith("data_"):
                secondary_intents[IntentCategory.DATA_TRANSFER] = 0.6
            elif msg_obj.event_type.startswith("control_"):
                secondary_intents[IntentCategory.CONTROL] = 0.5
            elif msg_obj.event_type.startswith("auth_"):
                secondary_intents[IntentCategory.AUTHENTICATION] = 0.7
        
        elif isinstance(msg_obj, ResponseMessage):
            # Responses are typically data transfer
            primary_intent = IntentCategory.DATA_TRANSFER
            confidence = 0.8
            extracted_entities["correlation_id"] = msg_obj.correlation_id
            extracted_entities["status"] = msg_obj.status.value
            extracted_entities["payload"] = msg_obj.payload
        
        # Extract context factors
        context_factors = {
            "sender_id": msg_obj.sender_id,
            "receiver_id": getattr(msg_obj, "receiver_id", None),
            "timestamp": getattr(msg_obj, "timestamp", time.time()),
            "priority": getattr(msg_obj, "priority", MessagePriority.NORMAL).value,
            "security_level": getattr(msg_obj, "security_level", SecurityLevel.NORMAL).value
        }
        
        # Create intent analysis
        analysis = IntentAnalysis(
            message_id=message_id,
            primary_intent=primary_intent,
            confidence=confidence,
            secondary_intents=secondary_intents,
            extracted_entities=extracted_entities,
            context_factors=context_factors
        )
        
        # Store the analysis
        async with self.lock:
            self.intent_analyses[message_id] = analysis
        
        self.logger.debug(f"Analyzed intent for message {message_id}: {primary_intent.value} (confidence: {confidence:.2f})")
        return analysis

    async def get_intent_analysis(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get the intent analysis for a message."""
        async with self.lock:
            if message_id not in self.intent_analyses:
                self.logger.error(f"Intent analysis for message {message_id} not found")
                return None
            
            return self.intent_analyses[message_id].to_dict()

    # --- Routing Decision ---

    async def make_routing_decision(self, message: Dict[str, Any], intent_analysis: Optional[IntentAnalysis] = None) -> RoutingDecision:
        """Make a routing decision for a message."""
        msg_obj = MessageFactory.create_from_dict(message)
        if not msg_obj:
            self.logger.error("Invalid message for routing decision")
            return RoutingDecision(
                message_id=message.get("message_id", str(uuid.uuid4())),
                strategy=RoutingStrategy.DIRECT,
                target_components=[],
                priority=MessagePriority.NORMAL,
                reasoning="Invalid message"
            )
        
        message_id = msg_obj.message_id
        
        # Get intent analysis if not provided
        if not intent_analysis:
            intent_analysis = await self.analyze_intent(message)
        
        # Extract basic routing information
        receiver_id = getattr(msg_obj, "receiver_id", None)
        priority = getattr(msg_obj, "priority", MessagePriority.NORMAL)
        
        # Determine routing strategy and targets
        strategy = RoutingStrategy.DIRECT
        target_components = []
        reasoning = ""
        
        if receiver_id:
            # Direct routing to specified receiver
            strategy = RoutingStrategy.DIRECT
            target_components = [receiver_id]
            reasoning = f"Direct routing to specified receiver: {receiver_id}"
        
        else:
            # Intent-based routing
            primary_intent = intent_analysis.primary_intent
            
            if primary_intent == IntentCategory.QUERY:
                # Find components that can handle this query
                query_type = intent_analysis.extracted_entities.get("query", "")
                capable_components = self._find_components_with_capability(f"query_{query_type}")
                
                if capable_components:
                    strategy = RoutingStrategy.CAPABILITY_BASED
                    target_components = capable_components
                    reasoning = f"Routing query to components with capability: query_{query_type}"
                else:
                    # Fallback to discovery service
                    strategy = RoutingStrategy.DIRECT
                    target_components = ["discovery_service"]
                    reasoning = f"No components found for query {query_type}, routing to discovery service"
            
            elif primary_intent == IntentCategory.COMMAND:
                # Find components that can handle this command
                command_type = intent_analysis.extracted_entities.get("command", "")
                capable_components = self._find_components_with_capability(f"command_{command_type}")
                
                if capable_components:
                    strategy = RoutingStrategy.CAPABILITY_BASED
                    target_components = capable_components
                    reasoning = f"Routing command to components with capability: command_{command_type}"
                else:
                    # Fallback to command router
                    strategy = RoutingStrategy.DIRECT
                    target_components = ["command_router"]
                    reasoning = f"No components found for command {command_type}, routing to command router"
            
            elif primary_intent == IntentCategory.NOTIFICATION:
                # Broadcast to interested components
                event_type = intent_analysis.extracted_entities.get("event_type", "")
                interested_components = self._find_components_with_capability(f"handle_{event_type}")
                
                if interested_components:
                    strategy = RoutingStrategy.MULTICAST
                    target_components = interested_components
                    reasoning = f"Broadcasting event to components interested in: {event_type}"
                else:
                    # Fallback to event bus
                    strategy = RoutingStrategy.DIRECT
                    target_components = ["event_bus"]
                    reasoning = f"No components found for event {event_type}, routing to event bus"
            
            elif primary_intent == IntentCategory.DATA_TRANSFER:
                # Find data handlers
                data_type = intent_analysis.extracted_entities.get("data_type", "generic")
                data_handlers = self._find_components_with_capability(f"handle_data_{data_type}")
                
                if data_handlers:
                    strategy = RoutingStrategy.LOAD_BALANCED
                    target_components = data_handlers
                    reasoning = f"Load balancing data transfer to handlers for: {data_type}"
                else:
                    # Fallback to data service
                    strategy = RoutingStrategy.DIRECT
                    target_components = ["data_service"]
                    reasoning = f"No handlers found for data type {data_type}, routing to data service"
            
            else:
                # Default to discovery service for unknown intents
                strategy = RoutingStrategy.DIRECT
                target_components = ["discovery_service"]
                reasoning = f"Unknown intent {primary_intent.value}, routing to discovery service"
        
        # Create routing decision
        decision = RoutingDecision(
            message_id=message_id,
            strategy=strategy,
            target_components=target_components,
            priority=priority,
            intent_analysis_id=intent_analysis.message_id,
            reasoning=reasoning
        )
        
        # Store the decision
        async with self.lock:
            self.routing_decisions[message_id] = decision
            
            # Add to routing history
            self.routing_history.append({
                "message_id": message_id,
                "timestamp": time.time(),
                "strategy": strategy.value,
                "target_count": len(target_components),
                "intent": intent_analysis.primary_intent.value,
                "confidence": intent_analysis.confidence
            })
            
            # Keep history limited
            max_history = self.config.get("max_routing_history", 1000)
            if len(self.routing_history) > max_history:
                self.routing_history = self.routing_history[-max_history:]
        
        self.logger.debug(f"Made routing decision for message {message_id}: {strategy.value} to {len(target_components)} targets")
        return decision

    async def get_routing_decision(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get the routing decision for a message."""
        async with self.lock:
            if message_id not in self.routing_decisions:
                self.logger.error(f"Routing decision for message {message_id} not found")
                return None
            
            return self.routing_decisions[message_id].to_dict()

    # --- Component Registry Management ---

    def _find_components_with_capability(self, capability: str) -> List[str]:
        """Find components with a specific capability."""
        matching_components = []
        
        for component_id, component_info in self.component_registry.items():
            capabilities = component_info.get("capabilities", [])
            if capability in capabilities:
                matching_components.append(component_id)
        
        return matching_components

    async def register_component(self, component_data: Dict[str, Any]) -> bool:
        """Register a component in the registry."""
        component_id = component_data.get("component_id")
        if not component_id:
            self.logger.error("Missing component_id in registration data")
            return False
        
        async with self.lock:
            self.component_registry[component_id] = component_data
            self.logger.info(f"Registered component: {component_id}")
        
        return True

    async def unregister_component(self, component_id: str) -> bool:
        """Unregister a component from the registry."""
        async with self.lock:
            if component_id not in self.component_registry:
                self.logger.warning(f"Component {component_id} not found for unregistration")
                return False
            
            del self.component_registry[component_id]
            self.logger.info(f"Unregistered component: {component_id}")
        
        return True

    async def get_component(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Get a component from the registry."""
        async with self.lock:
            if component_id not in self.component_registry:
                self.logger.error(f"Component {component_id} not found")
                return None
            
            return self.component_registry[component_id]

    async def list_components(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """List components in the registry with optional filtering."""
        filters = filters or {}
        
        async with self.lock:
            components = list(self.component_registry.values())
        
        # Apply filters
        if "capability" in filters:
            capability = filters["capability"]
            components = [comp for comp in components if capability in comp.get("capabilities", [])]
        
        if "type" in filters:
            comp_type = filters["type"]
            components = [comp for comp in components if comp.get("type") == comp_type]
        
        return components

    # --- Analytics and Learning ---

    async def get_routing_statistics(self) -> Dict[str, Any]:
        """Get statistics about routing decisions."""
        async with self.lock:
            total_decisions = len(self.routing_history)
            if total_decisions == 0:
                return {
                    "total_decisions": 0,
                    "strategies": {},
                    "intents": {},
                    "targets": {}
                }
            
            # Count strategies
            strategies = {}
            for entry in self.routing_history:
                strategy = entry["strategy"]
                strategies[strategy] = strategies.get(strategy, 0) + 1
            
            # Count intents
            intents = {}
            for entry in self.routing_history:
                intent = entry["intent"]
                intents[intent] = intents.get(intent, 0) + 1
            
            # Count target components
            targets = {}
            for decision_id, decision in self.routing_decisions.items():
                for target in decision.target_components:
                    targets[target] = targets.get(target, 0) + 1
            
            # Calculate percentages
            strategies_pct = {k: (v / total_decisions) * 100 for k, v in strategies.items()}
            intents_pct = {k: (v / total_decisions) * 100 for k, v in intents.items()}
            
            return {
                "total_decisions": total_decisions,
                "strategies": strategies_pct,
                "intents": intents_pct,
                "targets": targets,
                "avg_targets_per_decision": sum(entry["target_count"] for entry in self.routing_history) / total_decisions,
                "avg_confidence": sum(entry["confidence"] for entry in self.routing_history) / total_decisions
            }

    # --- ProtocolService Methods ---

    async def process_message_async(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process an incoming message."""
        msg_obj = MessageFactory.create_from_dict(message)
        if not msg_obj:
            return MessageFactory.create_error("invalid_message", "Could not parse message").to_dict()

        response_payload = None
        status = MessageStatus.SUCCESS

        if isinstance(msg_obj, CommandMessage):
            if msg_obj.command == "analyze_intent":
                params = msg_obj.params
                if "message" in params:
                    analysis = await self.analyze_intent(params["message"])
                    response_payload = analysis.to_dict()
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing message parameter"}
            
            elif msg_obj.command == "make_routing_decision":
                params = msg_obj.params
                if "message" in params:
                    decision = await self.make_routing_decision(params["message"])
                    response_payload = decision.to_dict()
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing message parameter"}
            
            elif msg_obj.command == "register_component":
                success = await self.register_component(msg_obj.params)
                response_payload = {"success": success}
                if not success:
                    status = MessageStatus.FAILED
            
            elif msg_obj.command == "unregister_component":
                params = msg_obj.params
                if "component_id" in params:
                    success = await self.unregister_component(params["component_id"])
                    response_payload = {"success": success}
                    if not success:
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing component_id parameter"}
            
            else:
                status = MessageStatus.FAILED
                response_payload = {"error": f"Unsupported command: {msg_obj.command}"}
        
        elif isinstance(msg_obj, QueryMessage):
            if msg_obj.query == "get_intent_analysis":
                params = msg_obj.params
                if "message_id" in params:
                    analysis = await self.get_intent_analysis(params["message_id"])
                    if analysis:
                        response_payload = analysis
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Intent analysis not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing message_id parameter"}
            
            elif msg_obj.query == "get_routing_decision":
                params = msg_obj.params
                if "message_id" in params:
                    decision = await self.get_routing_decision(params["message_id"])
                    if decision:
                        response_payload = decision
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Routing decision not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing message_id parameter"}
            
            elif msg_obj.query == "get_component":
                params = msg_obj.params
                if "component_id" in params:
                    component = await self.get_component(params["component_id"])
                    if component:
                        response_payload = component
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Component not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing component_id parameter"}
            
            elif msg_obj.query == "list_components":
                components = await self.list_components(msg_obj.params.get("filters"))
                response_payload = {"components": components}
            
            elif msg_obj.query == "get_routing_statistics":
                stats = await self.get_routing_statistics()
                response_payload = stats
            
            else:
                status = MessageStatus.FAILED
                response_payload = {"error": f"Unsupported query: {msg_obj.query}"}
        
        else:
            # For other message types, just analyze and route
            analysis = await self.analyze_intent(message)
            decision = await self.make_routing_decision(message, analysis)
            
            # Return the routing decision
            response_payload = {
                "intent_analysis": analysis.to_dict(),
                "routing_decision": decision.to_dict()
            }

        # Create response
        response = MessageFactory.create_response(
            correlation_id=msg_obj.message_id,
            status=status,
            payload=response_payload,
            sender_id=self.component_id,
            receiver_id=msg_obj.sender_id
        )
        return response.to_dict()

    def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a message (synchronous wrapper)."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.process_message_async(message))
        finally:
            loop.close()

    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check."""
        async with self.lock:
            num_analyses = len(self.intent_analyses)
            num_decisions = len(self.routing_decisions)
            num_components = len(self.component_registry)
        
        return {
            "status": "healthy",
            "intent_analyses": num_analyses,
            "routing_decisions": num_decisions,
            "registered_components": num_components
        }

    async def get_manifest(self) -> Dict[str, Any]:
        """Get the component manifest."""
        manifest = await super().get_manifest()
        health = await self.health_check()
        manifest.update(health)
        return manifest
"""
