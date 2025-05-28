"""
Component Discovery Mechanisms for Industriverse Protocol Layer

This module implements the discovery mechanisms for protocol components in the
Industriverse Protocol Layer. It provides services for registering, discovering,
and managing components in the protocol mesh.

The discovery service ensures that:
1. Components can be dynamically discovered at runtime
2. Service capabilities are advertised and can be queried
3. Components can find other components with specific capabilities
4. The protocol mesh maintains an up-to-date view of available components
"""

import uuid
import json
import time
import asyncio
import logging
import datetime
from typing import Dict, List, Any, Optional, Union, Set, Callable

from protocols.protocol_base import ProtocolComponent, ProtocolAgent, ProtocolService, ProtocolRegistry
from protocols.agent_interface import AgentCard
from protocols.message_formats import MessageFactory, MessagePriority, SecurityLevel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DiscoveryService:
    """
    Service for discovering protocol components in the mesh.
    
    The DiscoveryService maintains a registry of available components and
    provides methods for querying and discovering components based on
    various criteria.
    """
    
    def __init__(self, service_id: str = None):
        """
        Initialize a discovery service.
        
        Args:
            service_id: Unique identifier for this service. If None, a UUID is generated.
        """
        self.service_id = service_id or str(uuid.uuid4())
        self.registry = ProtocolRegistry()
        self.agent_cards: Dict[str, AgentCard] = {}
        self.capabilities_index: Dict[str, Set[str]] = {}
        self.component_types_index: Dict[str, Set[str]] = {}
        self.industry_tags_index: Dict[str, Set[str]] = {}
        self.last_heartbeat: Dict[str, float] = {}
        self.heartbeat_interval = 30.0  # seconds
        self.logger = logging.getLogger(f"{__name__}.DiscoveryService.{self.service_id[:8]}")
        self.logger.info(f"Discovery Service initialized with ID {self.service_id}")
    
    def register_component(self, component: ProtocolComponent) -> None:
        """
        Register a component with the discovery service.
        
        Args:
            component: The component to register.
        """
        self.registry.register_component(component)
        self.last_heartbeat[component.component_id] = time.time()
        
        # Index the component by type
        component_type = component.component_type
        if component_type not in self.component_types_index:
            self.component_types_index[component_type] = set()
        self.component_types_index[component_type].add(component.component_id)
        
        # Index the component by capabilities
        for capability in component.capabilities:
            cap_id = capability["id"]
            if cap_id not in self.capabilities_index:
                self.capabilities_index[cap_id] = set()
            self.capabilities_index[cap_id].add(component.component_id)
        
        self.logger.info(f"Registered component {component.component_type} with ID {component.component_id}")
    
    def register_agent_card(self, card: AgentCard) -> None:
        """
        Register an agent card with the discovery service.
        
        Args:
            card: The agent card to register.
        """
        self.agent_cards[card.agent_id] = card
        
        # Index the agent by capabilities
        for capability in card.capabilities:
            cap_id = capability["id"]
            if cap_id not in self.capabilities_index:
                self.capabilities_index[cap_id] = set()
            self.capabilities_index[cap_id].add(card.agent_id)
        
        # Index the agent by industry tags
        for tag in card.industry_tags:
            if tag not in self.industry_tags_index:
                self.industry_tags_index[tag] = set()
            self.industry_tags_index[tag].add(card.agent_id)
        
        self.logger.info(f"Registered agent card for {card.agent_type} with ID {card.agent_id}")
    
    def unregister_component(self, component_id: str) -> None:
        """
        Unregister a component from the discovery service.
        
        Args:
            component_id: The ID of the component to unregister.
        """
        # Get the component before unregistering it
        component = self.registry.get_component(component_id)
        if not component:
            self.logger.warning(f"Attempted to unregister non-existent component with ID {component_id}")
            return
        
        # Remove from registry
        self.registry.unregister_component(component_id)
        
        # Remove from heartbeat tracking
        if component_id in self.last_heartbeat:
            del self.last_heartbeat[component_id]
        
        # Remove from component types index
        component_type = component.component_type
        if component_type in self.component_types_index and component_id in self.component_types_index[component_type]:
            self.component_types_index[component_type].remove(component_id)
            if not self.component_types_index[component_type]:
                del self.component_types_index[component_type]
        
        # Remove from capabilities index
        for capability in component.capabilities:
            cap_id = capability["id"]
            if cap_id in self.capabilities_index and component_id in self.capabilities_index[cap_id]:
                self.capabilities_index[cap_id].remove(component_id)
                if not self.capabilities_index[cap_id]:
                    del self.capabilities_index[cap_id]
        
        # Remove agent card if it exists
        if component_id in self.agent_cards:
            card = self.agent_cards[component_id]
            
            # Remove from industry tags index
            for tag in card.industry_tags:
                if tag in self.industry_tags_index and component_id in self.industry_tags_index[tag]:
                    self.industry_tags_index[tag].remove(component_id)
                    if not self.industry_tags_index[tag]:
                        del self.industry_tags_index[tag]
            
            del self.agent_cards[component_id]
        
        self.logger.info(f"Unregistered component with ID {component_id}")
    
    def heartbeat(self, component_id: str) -> None:
        """
        Record a heartbeat for a component.
        
        Args:
            component_id: The ID of the component sending the heartbeat.
        """
        if component_id not in self.last_heartbeat:
            self.logger.warning(f"Received heartbeat from unregistered component with ID {component_id}")
            return
        
        self.last_heartbeat[component_id] = time.time()
        self.logger.debug(f"Received heartbeat from component with ID {component_id}")
    
    def check_stale_components(self) -> List[str]:
        """
        Check for components that haven't sent a heartbeat recently.
        
        Returns:
            A list of component IDs that are considered stale.
        """
        now = time.time()
        stale_threshold = now - (self.heartbeat_interval * 3)  # 3 times the heartbeat interval
        stale_components = []
        
        for component_id, last_time in list(self.last_heartbeat.items()):
            if last_time < stale_threshold:
                stale_components.append(component_id)
                self.logger.warning(f"Component with ID {component_id} is stale")
        
        return stale_components
    
    def remove_stale_components(self) -> None:
        """Remove components that haven't sent a heartbeat recently."""
        stale_components = self.check_stale_components()
        for component_id in stale_components:
            self.unregister_component(component_id)
    
    def get_component(self, component_id: str) -> Optional[ProtocolComponent]:
        """
        Get a component by ID.
        
        Args:
            component_id: The ID of the component to retrieve.
            
        Returns:
            The component, or None if not found.
        """
        return self.registry.get_component(component_id)
    
    def get_agent_card(self, agent_id: str) -> Optional[AgentCard]:
        """
        Get an agent card by ID.
        
        Args:
            agent_id: The ID of the agent to retrieve.
            
        Returns:
            The agent card, or None if not found.
        """
        return self.agent_cards.get(agent_id)
    
    def find_components_by_type(self, component_type: str) -> List[ProtocolComponent]:
        """
        Find components by type.
        
        Args:
            component_type: The type of components to find.
            
        Returns:
            A list of matching components.
        """
        if component_type not in self.component_types_index:
            return []
        
        component_ids = self.component_types_index[component_type]
        return [self.registry.get_component(cid) for cid in component_ids if self.registry.get_component(cid)]
    
    def find_components_by_capability(self, capability: str) -> List[ProtocolComponent]:
        """
        Find components by capability.
        
        Args:
            capability: The capability to search for.
            
        Returns:
            A list of matching components.
        """
        if capability not in self.capabilities_index:
            return []
        
        component_ids = self.capabilities_index[capability]
        return [self.registry.get_component(cid) for cid in component_ids if self.registry.get_component(cid)]
    
    def find_agents_by_industry_tag(self, tag: str) -> List[AgentCard]:
        """
        Find agents by industry tag.
        
        Args:
            tag: The industry tag to search for.
            
        Returns:
            A list of matching agent cards.
        """
        if tag not in self.industry_tags_index:
            return []
        
        agent_ids = self.industry_tags_index[tag]
        return [self.agent_cards[aid] for aid in agent_ids if aid in self.agent_cards]
    
    def find_agents_by_priority(self, min_priority: int = 0, max_priority: int = 100) -> List[AgentCard]:
        """
        Find agents by priority range.
        
        Args:
            min_priority: Minimum priority level (inclusive).
            max_priority: Maximum priority level (inclusive).
            
        Returns:
            A list of matching agent cards.
        """
        return [
            card for card in self.agent_cards.values()
            if min_priority <= card.priority <= max_priority
        ]
    
    def get_all_components(self) -> List[ProtocolComponent]:
        """
        Get all registered components.
        
        Returns:
            A list of all components.
        """
        return self.registry.get_all_components()
    
    def get_all_agent_cards(self) -> List[AgentCard]:
        """
        Get all registered agent cards.
        
        Returns:
            A list of all agent cards.
        """
        return list(self.agent_cards.values())
    
    def get_component_count(self) -> int:
        """
        Get the number of registered components.
        
        Returns:
            The number of components.
        """
        return len(self.registry.components)
    
    def get_agent_card_count(self) -> int:
        """
        Get the number of registered agent cards.
        
        Returns:
            The number of agent cards.
        """
        return len(self.agent_cards)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this discovery service to a dictionary representation.
        
        Returns:
            A dictionary representing this discovery service.
        """
        return {
            "service_id": self.service_id,
            "component_count": self.get_component_count(),
            "agent_card_count": self.get_agent_card_count(),
            "heartbeat_interval": self.heartbeat_interval,
            "capabilities": list(self.capabilities_index.keys()),
            "component_types": list(self.component_types_index.keys()),
            "industry_tags": list(self.industry_tags_index.keys())
        }


class AsyncDiscoveryService:
    """
    Asynchronous service for discovering protocol components in the mesh.
    
    This class provides the same functionality as DiscoveryService but with
    asynchronous methods for high-performance protocol handling.
    """
    
    def __init__(self, service_id: str = None):
        """
        Initialize an asynchronous discovery service.
        
        Args:
            service_id: Unique identifier for this service. If None, a UUID is generated.
        """
        self.service_id = service_id or str(uuid.uuid4())
        self.registry = ProtocolRegistry()
        self.agent_cards: Dict[str, AgentCard] = {}
        self.capabilities_index: Dict[str, Set[str]] = {}
        self.component_types_index: Dict[str, Set[str]] = {}
        self.industry_tags_index: Dict[str, Set[str]] = {}
        self.last_heartbeat: Dict[str, float] = {}
        self.heartbeat_interval = 30.0  # seconds
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(f"{__name__}.AsyncDiscoveryService.{self.service_id[:8]}")
        self.logger.info(f"Async Discovery Service initialized with ID {self.service_id}")
    
    async def register_component(self, component: ProtocolComponent) -> None:
        """
        Register a component with the discovery service.
        
        Args:
            component: The component to register.
        """
        async with self.lock:
            self.registry.register_component(component)
            self.last_heartbeat[component.component_id] = time.time()
            
            # Index the component by type
            component_type = component.component_type
            if component_type not in self.component_types_index:
                self.component_types_index[component_type] = set()
            self.component_types_index[component_type].add(component.component_id)
            
            # Index the component by capabilities
            for capability in component.capabilities:
                cap_id = capability["id"]
                if cap_id not in self.capabilities_index:
                    self.capabilities_index[cap_id] = set()
                self.capabilities_index[cap_id].add(component.component_id)
        
        self.logger.info(f"Registered component {component.component_type} with ID {component.component_id}")
    
    async def register_agent_card(self, card: AgentCard) -> None:
        """
        Register an agent card with the discovery service.
        
        Args:
            card: The agent card to register.
        """
        async with self.lock:
            self.agent_cards[card.agent_id] = card
            
            # Index the agent by capabilities
            for capability in card.capabilities:
                cap_id = capability["id"]
                if cap_id not in self.capabilities_index:
                    self.capabilities_index[cap_id] = set()
                self.capabilities_index[cap_id].add(card.agent_id)
            
            # Index the agent by industry tags
            for tag in card.industry_tags:
                if tag not in self.industry_tags_index:
                    self.industry_tags_index[tag] = set()
                self.industry_tags_index[tag].add(card.agent_id)
        
        self.logger.info(f"Registered agent card for {card.agent_type} with ID {card.agent_id}")
    
    async def unregister_component(self, component_id: str) -> None:
        """
        Unregister a component from the discovery service.
        
        Args:
            component_id: The ID of the component to unregister.
        """
        async with self.lock:
            # Get the component before unregistering it
            component = self.registry.get_component(component_id)
            if not component:
                self.logger.warning(f"Attempted to unregister non-existent component with ID {component_id}")
                return
            
            # Remove from registry
            self.registry.unregister_component(component_id)
            
            # Remove from heartbeat tracking
            if component_id in self.last_heartbeat:
                del self.last_heartbeat[component_id]
            
            # Remove from component types index
            component_type = component.component_type
            if component_type in self.component_types_index and component_id in self.component_types_index[component_type]:
                self.component_types_index[component_type].remove(component_id)
                if not self.component_types_index[component_type]:
                    del self.component_types_index[component_type]
            
            # Remove from capabilities index
            for capability in component.capabilities:
                cap_id = capability["id"]
                if cap_id in self.capabilities_index and component_id in self.capabilities_index[cap_id]:
                    self.capabilities_index[cap_id].remove(component_id)
                    if not self.capabilities_index[cap_id]:
                        del self.capabilities_index[cap_id]
            
            # Remove agent card if it exists
            if component_id in self.agent_cards:
                card = self.agent_cards[component_id]
                
                # Remove from industry tags index
                for tag in card.industry_tags:
                    if tag in self.industry_tags_index and component_id in self.industry_tags_index[tag]:
                        self.industry_tags_index[tag].remove(component_id)
                        if not self.industry_tags_index[tag]:
                            del self.industry_tags_index[tag]
                
                del self.agent_cards[component_id]
        
        self.logger.info(f"Unregistered component with ID {component_id}")
    
    async def heartbeat(self, component_id: str) -> None:
        """
        Record a heartbeat for a component.
        
        Args:
            component_id: The ID of the component sending the heartbeat.
        """
        async with self.lock:
            if component_id not in self.last_heartbeat:
                self.logger.warning(f"Received heartbeat from unregistered component with ID {component_id}")
                return
            
            self.last_heartbeat[component_id] = time.time()
        
        self.logger.debug(f"Received heartbeat from component with ID {component_id}")
    
    async def check_stale_components(self) -> List[str]:
        """
        Check for components that haven't sent a heartbeat recently.
        
        Returns:
            A list of component IDs that are considered stale.
        """
        now = time.time()
        stale_threshold = now - (self.heartbeat_interval * 3)  # 3 times the heartbeat interval
        stale_components = []
        
        async with self.lock:
            for component_id, last_time in list(self.last_heartbeat.items()):
                if last_time < stale_threshold:
                    stale_components.append(component_id)
                    self.logger.warning(f"Component with ID {component_id} is stale")
        
        return stale_components
    
    async def remove_stale_components(self) -> None:
        """Remove components that haven't sent a heartbeat recently."""
        stale_components = await self.check_stale_components()
        for component_id in stale_components:
            await self.unregister_component(component_id)
    
    async def get_component(self, component_id: str) -> Optional[ProtocolComponent]:
        """
        Get a component by ID.
        
        Args:
            component_id: The ID of the component to retrieve.
            
        Returns:
            The component, or None if not found.
        """
        async with self.lock:
            return self.registry.get_component(component_id)
    
    async def get_agent_card(self, agent_id: str) -> Optional[AgentCard]:
        """
        Get an agent card by ID.
        
        Args:
            agent_id: The ID of the agent to retrieve.
            
        Returns:
            The agent card, or None if not found.
        """
        async with self.lock:
            return self.agent_cards.get(agent_id)
    
    async def find_components_by_type(self, component_type: str) -> List[ProtocolComponent]:
        """
        Find components by type.
        
        Args:
            component_type: The type of components to find.
            
        Returns:
            A list of matching components.
        """
        async with self.lock:
            if component_type not in self.component_types_index:
                return []
            
            component_ids = self.component_types_index[component_type]
            return [self.registry.get_component(cid) for cid in component_ids if self.registry.get_component(cid)]
    
    async def find_components_by_capability(self, capability: str) -> List[ProtocolComponent]:
        """
        Find components by capability.
        
        Args:
            capability: The capability to search for.
            
        Returns:
            A list of matching components.
        """
        async with self.lock:
            if capability not in self.capabilities_index:
                return []
            
            component_ids = self.capabilities_index[capability]
            return [self.registry.get_component(cid) for cid in component_ids if self.registry.get_component(cid)]
    
    async def find_agents_by_industry_tag(self, tag: str) -> List[AgentCard]:
        """
        Find agents by industry tag.
        
        Args:
            tag: The industry tag to search for.
            
        Returns:
            A list of matching agent cards.
        """
        async with self.lock:
            if tag not in self.industry_tags_index:
                return []
            
            agent_ids = self.industry_tags_index[tag]
            return [self.agent_cards[aid] for aid in agent_ids if aid in self.agent_cards]
    
    async def find_agents_by_priority(self, min_priority: int = 0, max_priority: int = 100) -> List[AgentCard]:
        """
        Find agents by priority range.
        
        Args:
            min_priority: Minimum priority level (inclusive).
            max_priority: Maximum priority level (inclusive).
            
        Returns:
            A list of matching agent cards.
        """
        async with self.lock:
            return [
                card for card in self.agent_cards.values()
                if min_priority <= card.priority <= max_priority
            ]
    
    async def get_all_components(self) -> List[ProtocolComponent]:
        """
        Get all registered components.
        
        Returns:
            A list of all components.
        """
        async with self.lock:
            return self.registry.get_all_components()
    
    async def get_all_agent_cards(self) -> List[AgentCard]:
        """
        Get all registered agent cards.
        
        Returns:
            A list of all agent cards.
        """
        async with self.lock:
            return list(self.agent_cards.values())
    
    async def get_component_count(self) -> int:
        """
        Get the number of registered components.
        
        Returns:
            The number of components.
        """
        async with self.lock:
            return len(self.registry.components)
    
    async def get_agent_card_count(self) -> int:
        """
        Get the number of registered agent cards.
        
        Returns:
            The number of agent cards.
        """
        async with self.lock:
            return len(self.agent_cards)
    
    async def to_dict(self) -> Dict[str, Any]:
        """
        Convert this discovery service to a dictionary representation.
        
        Returns:
            A dictionary representing this discovery service.
        """
        async with self.lock:
            return {
                "service_id": self.service_id,
                "component_count": len(self.registry.components),
                "agent_card_count": len(self.agent_cards),
                "heartbeat_interval": self.heartbeat_interval,
                "capabilities": list(self.capabilities_index.keys()),
                "component_types": list(self.component_types_index.keys()),
                "industry_tags": list(self.industry_tags_index.keys())
            }


class DiscoveryServiceClient:
    """
    Client for interacting with a discovery service.
    
    This class provides methods for registering with and querying a
    discovery service from a component's perspective.
    """
    
    def __init__(self, discovery_service: DiscoveryService, component_id: str, component_type: str):
        """
        Initialize a discovery service client.
        
        Args:
            discovery_service: The discovery service to interact with.
            component_id: The ID of the component using this client.
            component_type: The type of the component using this client.
        """
        self.discovery_service = discovery_service
        self.component_id = component_id
        self.component_type = component_type
        self.heartbeat_task = None
        self.logger = logging.getLogger(f"{__name__}.DiscoveryServiceClient.{component_id[:8]}")
        self.logger.info(f"Discovery Service Client initialized for component {component_type} with ID {component_id}")
    
    def register(self, component: ProtocolComponent = None) -> None:
        """
        Register with the discovery service.
        
        Args:
            component: The component to register. If None, a minimal component is created.
        """
        if not component:
            from protocols.protocol_base import ProtocolComponent
            
            class MinimalComponent(ProtocolComponent):
                def process_message(self, message):
                    return {"status": "ok"}
                
                def get_manifest(self):
                    return {"component_id": self.component_id, "component_type": self.component_type}
                
                def health_check(self):
                    return {"status": "healthy"}
            
            component = MinimalComponent(self.component_id, self.component_type)
        
        self.discovery_service.register_component(component)
        self.logger.info(f"Registered component {self.component_type} with ID {self.component_id}")
    
    def register_agent_card(self, card: AgentCard) -> None:
        """
        Register an agent card with the discovery service.
        
        Args:
            card: The agent card to register.
        """
        self.discovery_service.register_agent_card(card)
        self.logger.info(f"Registered agent card for {card.agent_type} with ID {card.agent_id}")
    
    def unregister(self) -> None:
        """Unregister from the discovery service."""
        self.discovery_service.unregister_component(self.component_id)
        self.logger.info(f"Unregistered component with ID {self.component_id}")
    
    def send_heartbeat(self) -> None:
        """Send a heartbeat to the discovery service."""
        self.discovery_service.heartbeat(self.component_id)
        self.logger.debug(f"Sent heartbeat for component with ID {self.component_id}")
    
    def start_heartbeat(self, interval: float = None) -> None:
        """
        Start sending periodic heartbeats to the discovery service.
        
        Args:
            interval: The heartbeat interval in seconds. If None, the discovery service's
                      default interval is used.
        """
        if self.heartbeat_task:
            self.logger.warning("Heartbeat task already running")
            return
        
        interval = interval or self.discovery_service.heartbeat_interval
        
        import threading
        
        def heartbeat_loop():
            while True:
                try:
                    self.send_heartbeat()
                    time.sleep(interval)
                except Exception as e:
                    self.logger.error(f"Error in heartbeat loop: {e}")
                    time.sleep(interval)
        
        self.heartbeat_task = threading.Thread(target=heartbeat_loop, daemon=True)
        self.heartbeat_task.start()
        self.logger.info(f"Started heartbeat task with interval {interval} seconds")
    
    def stop_heartbeat(self) -> None:
        """Stop sending periodic heartbeats."""
        if not self.heartbeat_task:
            self.logger.warning("No heartbeat task running")
            return
        
        # There's no clean way to stop a thread in Python, so we just
        # let the daemon thread die when the program exits
        self.heartbeat_task = None
        self.logger.info("Stopped heartbeat task")
    
    def find_components_by_type(self, component_type: str) -> List[ProtocolComponent]:
        """
        Find components by type.
        
        Args:
            component_type: The type of components to find.
            
        Returns:
            A list of matching components.
        """
        return self.discovery_service.find_components_by_type(component_type)
    
    def find_components_by_capability(self, capability: str) -> List[ProtocolComponent]:
        """
        Find components by capability.
        
        Args:
            capability: The capability to search for.
            
        Returns:
            A list of matching components.
        """
        return self.discovery_service.find_components_by_capability(capability)
    
    def find_agents_by_industry_tag(self, tag: str) -> List[AgentCard]:
        """
        Find agents by industry tag.
        
        Args:
            tag: The industry tag to search for.
            
        Returns:
            A list of matching agent cards.
        """
        return self.discovery_service.find_agents_by_industry_tag(tag)
    
    def find_agents_by_priority(self, min_priority: int = 0, max_priority: int = 100) -> List[AgentCard]:
        """
        Find agents by priority range.
        
        Args:
            min_priority: Minimum priority level (inclusive).
            max_priority: Maximum priority level (inclusive).
            
        Returns:
            A list of matching agent cards.
        """
        return self.discovery_service.find_agents_by_priority(min_priority, max_priority)
    
    def get_component(self, component_id: str) -> Optional[ProtocolComponent]:
        """
        Get a component by ID.
        
        Args:
            component_id: The ID of the component to retrieve.
            
        Returns:
            The component, or None if not found.
        """
        return self.discovery_service.get_component(component_id)
    
    def get_agent_card(self, agent_id: str) -> Optional[AgentCard]:
        """
        Get an agent card by ID.
        
        Args:
            agent_id: The ID of the agent to retrieve.
            
        Returns:
            The agent card, or None if not found.
        """
        return self.discovery_service.get_agent_card(agent_id)


class AsyncDiscoveryServiceClient:
    """
    Asynchronous client for interacting with a discovery service.
    
    This class provides asynchronous methods for registering with and querying a
    discovery service from a component's perspective.
    """
    
    def __init__(self, discovery_service: AsyncDiscoveryService, component_id: str, component_type: str):
        """
        Initialize an asynchronous discovery service client.
        
        Args:
            discovery_service: The asynchronous discovery service to interact with.
            component_id: The ID of the component using this client.
            component_type: The type of the component using this client.
        """
        self.discovery_service = discovery_service
        self.component_id = component_id
        self.component_type = component_type
        self.heartbeat_task = None
        self.logger = logging.getLogger(f"{__name__}.AsyncDiscoveryServiceClient.{component_id[:8]}")
        self.logger.info(f"Async Discovery Service Client initialized for component {component_type} with ID {component_id}")
    
    async def register(self, component: ProtocolComponent = None) -> None:
        """
        Register with the discovery service.
        
        Args:
            component: The component to register. If None, a minimal component is created.
        """
        if not component:
            from protocols.protocol_base import ProtocolComponent
            
            class MinimalComponent(ProtocolComponent):
                def process_message(self, message):
                    return {"status": "ok"}
                
                def get_manifest(self):
                    return {"component_id": self.component_id, "component_type": self.component_type}
                
                def health_check(self):
                    return {"status": "healthy"}
            
            component = MinimalComponent(self.component_id, self.component_type)
        
        await self.discovery_service.register_component(component)
        self.logger.info(f"Registered component {self.component_type} with ID {self.component_id}")
    
    async def register_agent_card(self, card: AgentCard) -> None:
        """
        Register an agent card with the discovery service.
        
        Args:
            card: The agent card to register.
        """
        await self.discovery_service.register_agent_card(card)
        self.logger.info(f"Registered agent card for {card.agent_type} with ID {card.agent_id}")
    
    async def unregister(self) -> None:
        """Unregister from the discovery service."""
        await self.discovery_service.unregister_component(self.component_id)
        self.logger.info(f"Unregistered component with ID {self.component_id}")
    
    async def send_heartbeat(self) -> None:
        """Send a heartbeat to the discovery service."""
        await self.discovery_service.heartbeat(self.component_id)
        self.logger.debug(f"Sent heartbeat for component with ID {self.component_id}")
    
    async def start_heartbeat(self, interval: float = None) -> None:
        """
        Start sending periodic heartbeats to the discovery service.
        
        Args:
            interval: The heartbeat interval in seconds. If None, the discovery service's
                      default interval is used.
        """
        if self.heartbeat_task:
            self.logger.warning("Heartbeat task already running")
            return
        
        interval = interval or self.discovery_service.heartbeat_interval
        
        async def heartbeat_loop():
            while True:
                try:
                    await self.send_heartbeat()
                    await asyncio.sleep(interval)
                except Exception as e:
                    self.logger.error(f"Error in heartbeat loop: {e}")
                    await asyncio.sleep(interval)
        
        self.heartbeat_task = asyncio.create_task(heartbeat_loop())
        self.logger.info(f"Started heartbeat task with interval {interval} seconds")
    
    def stop_heartbeat(self) -> None:
        """Stop sending periodic heartbeats."""
        if not self.heartbeat_task:
            self.logger.warning("No heartbeat task running")
            return
        
        self.heartbeat_task.cancel()
        self.heartbeat_task = None
        self.logger.info("Stopped heartbeat task")
    
    async def find_components_by_type(self, component_type: str) -> List[ProtocolComponent]:
        """
        Find components by type.
        
        Args:
            component_type: The type of components to find.
            
        Returns:
            A list of matching components.
        """
        return await self.discovery_service.find_components_by_type(component_type)
    
    async def find_components_by_capability(self, capability: str) -> List[ProtocolComponent]:
        """
        Find components by capability.
        
        Args:
            capability: The capability to search for.
            
        Returns:
            A list of matching components.
        """
        return await self.discovery_service.find_components_by_capability(capability)
    
    async def find_agents_by_industry_tag(self, tag: str) -> List[AgentCard]:
        """
        Find agents by industry tag.
        
        Args:
            tag: The industry tag to search for.
            
        Returns:
            A list of matching agent cards.
        """
        return await self.discovery_service.find_agents_by_industry_tag(tag)
    
    async def find_agents_by_priority(self, min_priority: int = 0, max_priority: int = 100) -> List[AgentCard]:
        """
        Find agents by priority range.
        
        Args:
            min_priority: Minimum priority level (inclusive).
            max_priority: Maximum priority level (inclusive).
            
        Returns:
            A list of matching agent cards.
        """
        return await self.discovery_service.find_agents_by_priority(min_priority, max_priority)
    
    async def get_component(self, component_id: str) -> Optional[ProtocolComponent]:
        """
        Get a component by ID.
        
        Args:
            component_id: The ID of the component to retrieve.
            
        Returns:
            The component, or None if not found.
        """
        return await self.discovery_service.get_component(component_id)
    
    async def get_agent_card(self, agent_id: str) -> Optional[AgentCard]:
        """
        Get an agent card by ID.
        
        Args:
            agent_id: The ID of the agent to retrieve.
            
        Returns:
            The agent card, or None if not found.
        """
        return await self.discovery_service.get_agent_card(agent_id)
"""
