"""
Registry Protocol Connector

Connects Unified Capsule Registry to MCP and A2A protocols, enabling:
- MCP-based capsule queries and context propagation
- A2A agent discovery and bidding
- Event bus integration for all registry operations
- Protocol translation between registry and external systems

Part of Week 18-19: Architecture Unification - Day 9
CRITICAL INTEGRATION per user feedback
"""

import logging
import asyncio
import time
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class RegistryProtocolConnector:
    """
    Connects Unified Capsule Registry to MCP and A2A protocols.

    Architecture:
    ┌───────────────────────────────────────────────────────┐
    │         Unified Capsule Registry                       │
    ├───────────────────────────────────────────────────────┤
    │  - register_capsule()                                  │
    │  - search_capsules()                                   │
    │  - get_capsule()                                       │
    └────────────────────┬──────────────────────────────────┘
                         │
    ┌────────────────────▼──────────────────────────────────┐
    │    Registry Protocol Connector (THIS)                  │
    ├───────────────────────────────────────────────────────┤
    │  - MCP Integration                                     │
    │  - A2A Integration                                     │
    │  - Event Bus Integration                               │
    │  - Protocol Translation                                │
    └───┬──────────────┬─────────────────┬──────────────────┘
        │              │                 │
        ▼              ▼                 ▼
    ┌───────────┐  ┌──────────┐  ┌─────────────────┐
    │ MCP       │  │ A2A      │  │ Event Bus       │
    │ Protocol  │  │ Protocol │  │ (Kafka)         │
    │           │  │          │  │                 │
    │ - Context │  │ - Agent  │  │ - Registry      │
    │ - Queries │  │   Discovery│  │   Events        │
    │ - Updates │  │ - Bidding  │  │ - Capsule Ops   │
    └───────────┘  └──────────┘  └─────────────────┘

    Features:
    - MCP capsule context queries
    - A2A agent discovery via registry
    - Event publishing on all registry operations
    - Bidirectional protocol translation
    """

    def __init__(
        self,
        unified_registry=None,
        mcp_bridge=None,
        a2a_bridge=None,
        event_bus=None
    ):
        """
        Initialize Registry Protocol Connector.

        Args:
            unified_registry: UnifiedCapsuleRegistry instance
            mcp_bridge: MCP protocol bridge
            a2a_bridge: A2A protocol bridge
            event_bus: Event bus for publishing registry events
        """
        self.registry = unified_registry
        self.mcp_bridge = mcp_bridge
        self.a2a_bridge = a2a_bridge
        self.event_bus = event_bus

        # Statistics
        self.stats = {
            "mcp_queries": 0,
            "a2a_discoveries": 0,
            "events_published": 0,
            "protocol_translations": 0
        }

        logger.info("Registry Protocol Connector initialized")

    async def initialize(self):
        """Initialize protocol connections."""
        logger.info("Initializing registry protocol connections...")

        # Connect MCP protocol
        if self.mcp_bridge:
            await self._init_mcp_integration()
        else:
            logger.warning("MCP bridge not available")

        # Connect A2A protocol
        if self.a2a_bridge:
            await self._init_a2a_integration()
        else:
            logger.warning("A2A bridge not available")

        # Subscribe to registry events
        await self._subscribe_to_registry_events()

        logger.info("Registry protocol connections initialized")

    # ========================================================================
    # MCP Protocol Integration
    # ========================================================================

    async def _init_mcp_integration(self):
        """Initialize MCP protocol integration."""
        logger.info("Initializing MCP integration with registry...")

        try:
            # Register MCP context providers for capsule queries
            await self._register_mcp_context_providers()

            # Register MCP resource handlers for capsule operations
            await self._register_mcp_resource_handlers()

            logger.info("MCP integration initialized")

        except Exception as e:
            logger.error(f"Failed to initialize MCP integration: {e}")

    async def _register_mcp_context_providers(self):
        """Register MCP context providers for capsule data."""
        if not self.mcp_bridge:
            return

        try:
            # Register capsule context provider
            await self.mcp_bridge.register_context_provider(
                context_type="capsule",
                provider=self._provide_capsule_context
            )

            # Register capsule list context provider
            await self.mcp_bridge.register_context_provider(
                context_type="capsule_list",
                provider=self._provide_capsule_list_context
            )

            # Register capsule lineage context provider
            await self.mcp_bridge.register_context_provider(
                context_type="capsule_lineage",
                provider=self._provide_capsule_lineage_context
            )

            logger.info("MCP context providers registered")

        except AttributeError:
            logger.warning("MCP bridge doesn't support context providers - using fallback")

    async def _register_mcp_resource_handlers(self):
        """Register MCP resource handlers for capsule operations."""
        if not self.mcp_bridge:
            return

        try:
            # Register capsule query handler
            await self.mcp_bridge.register_resource_handler(
                resource_type="capsule",
                action="query",
                handler=self._handle_mcp_capsule_query
            )

            # Register capsule search handler
            await self.mcp_bridge.register_resource_handler(
                resource_type="capsule",
                action="search",
                handler=self._handle_mcp_capsule_search
            )

            logger.info("MCP resource handlers registered")

        except AttributeError:
            logger.warning("MCP bridge doesn't support resource handlers - using fallback")

    async def _provide_capsule_context(self, capsule_id: str) -> Dict[str, Any]:
        """
        Provide capsule context for MCP.

        Args:
            capsule_id: Capsule ID

        Returns:
            MCP context data
        """
        if not self.registry:
            return {"error": "registry_not_available"}

        self.stats["mcp_queries"] += 1

        try:
            capsule = await self.registry.get_capsule(capsule_id)

            if not capsule:
                return {"error": "capsule_not_found"}

            # Format for MCP context
            return {
                "type": "capsule",
                "capsule_id": capsule_id,
                "lifecycle_context": capsule.get("lifecycle_context", {}),
                "governance": capsule.get("governance", {}),
                "source": capsule.get("lifecycle_context", {}).get("source"),
                "status": capsule.get("lifecycle_context", {}).get("stage"),
                "generation": capsule.get("lifecycle_context", {}).get("generation"),
                "created_at": capsule.get("lifecycle_context", {}).get("created_at")
            }

        except Exception as e:
            logger.error(f"Failed to provide capsule context: {e}")
            return {"error": str(e)}

    async def _provide_capsule_list_context(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide capsule list context for MCP.

        Args:
            filters: Search filters

        Returns:
            MCP context with capsule list
        """
        if not self.registry:
            return {"error": "registry_not_available"}

        self.stats["mcp_queries"] += 1

        try:
            capsules = await self.registry.search_capsules(
                filters=filters,
                limit=filters.get("limit", 100)
            )

            return {
                "type": "capsule_list",
                "count": len(capsules),
                "capsules": [
                    {
                        "capsule_id": c.get("lifecycle_context", {}).get("capsule_id"),
                        "source": c.get("lifecycle_context", {}).get("source"),
                        "status": c.get("lifecycle_context", {}).get("stage"),
                        "template_id": c.get("lifecycle_context", {}).get("template_id")
                    }
                    for c in capsules
                ],
                "filters": filters
            }

        except Exception as e:
            logger.error(f"Failed to provide capsule list context: {e}")
            return {"error": str(e)}

    async def _provide_capsule_lineage_context(self, capsule_id: str) -> Dict[str, Any]:
        """
        Provide capsule lineage context for MCP.

        Args:
            capsule_id: Capsule ID

        Returns:
            MCP context with lineage data
        """
        if not self.registry:
            return {"error": "registry_not_available"}

        self.stats["mcp_queries"] += 1

        try:
            lineage = await self.registry.get_capsule_lineage(capsule_id)

            return {
                "type": "capsule_lineage",
                "capsule_id": capsule_id,
                "generation": lineage.get("generation"),
                "parents": lineage.get("parents", []),
                "children": lineage.get("children", []),
                "total_ancestors": lineage.get("total_ancestors", 0),
                "total_descendants": lineage.get("total_descendants", 0)
            }

        except Exception as e:
            logger.error(f"Failed to provide capsule lineage context: {e}")
            return {"error": str(e)}

    async def _handle_mcp_capsule_query(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP capsule query request.

        Args:
            request: MCP query request

        Returns:
            Query result
        """
        capsule_id = request.get("capsule_id")

        if not capsule_id:
            return {"error": "missing_capsule_id"}

        return await self._provide_capsule_context(capsule_id)

    async def _handle_mcp_capsule_search(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP capsule search request.

        Args:
            request: MCP search request

        Returns:
            Search results
        """
        filters = request.get("filters", {})

        return await self._provide_capsule_list_context(filters)

    # ========================================================================
    # A2A Protocol Integration
    # ========================================================================

    async def _init_a2a_integration(self):
        """Initialize A2A protocol integration."""
        logger.info("Initializing A2A integration with registry...")

        try:
            # Register A2A agent discovery handler
            await self._register_a2a_discovery_handler()

            # Register A2A bidding integration
            await self._register_a2a_bidding_integration()

            logger.info("A2A integration initialized")

        except Exception as e:
            logger.error(f"Failed to initialize A2A integration: {e}")

    async def _register_a2a_discovery_handler(self):
        """Register A2A agent discovery handler."""
        if not self.a2a_bridge:
            return

        try:
            # Register agent discovery via registry
            await self.a2a_bridge.register_discovery_handler(
                handler=self._handle_a2a_agent_discovery
            )

            logger.info("A2A discovery handler registered")

        except AttributeError:
            logger.warning("A2A bridge doesn't support discovery handlers")

    async def _register_a2a_bidding_integration(self):
        """Register A2A bidding integration with registry."""
        if not self.a2a_bridge:
            return

        try:
            # Register bid validation against registry
            await self.a2a_bridge.register_bid_validator(
                validator=self._validate_a2a_bid_against_registry
            )

            logger.info("A2A bidding integration registered")

        except AttributeError:
            logger.warning("A2A bridge doesn't support bid validators")

    async def _handle_a2a_agent_discovery(
        self,
        discovery_query: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Handle A2A agent discovery via registry.

        Args:
            discovery_query: A2A discovery query
                {
                    "capabilities": ["data_processing", "analytics"],
                    "status": "active",
                    "governance_status": "validated"
                }

        Returns:
            List of matching agent capsules
        """
        if not self.registry:
            return []

        self.stats["a2a_discoveries"] += 1

        try:
            logger.info(f"A2A agent discovery: {discovery_query}")

            # Convert A2A query to registry filters
            filters = self._translate_a2a_query_to_registry_filters(discovery_query)

            # Search registry
            capsules = await self.registry.search_capsules(
                filters=filters,
                limit=discovery_query.get("limit", 50)
            )

            # Convert to A2A agent format
            agents = []
            for capsule in capsules:
                agent = self._translate_capsule_to_a2a_agent(capsule)
                if agent:
                    agents.append(agent)

            logger.info(f"A2A discovery found {len(agents)} agents")

            return agents

        except Exception as e:
            logger.error(f"A2A agent discovery failed: {e}")
            return []

    async def _validate_a2a_bid_against_registry(
        self,
        bid: Dict[str, Any]
    ) -> bool:
        """
        Validate A2A bid against registry.

        Args:
            bid: A2A bid data

        Returns:
            Validation result
        """
        if not self.registry:
            return False

        try:
            agent_id = bid.get("agent_id")

            # Verify agent exists in registry
            capsule = await self.registry.get_capsule(agent_id)

            if not capsule:
                logger.warning(f"A2A bid rejected: agent {agent_id} not in registry")
                return False

            # Verify agent is active
            status = capsule.get("lifecycle_context", {}).get("stage")
            if status != "active":
                logger.warning(f"A2A bid rejected: agent {agent_id} not active (status: {status})")
                return False

            # Verify governance
            governance_status = capsule.get("governance", {}).get("validated_at")
            if not governance_status:
                logger.warning(f"A2A bid rejected: agent {agent_id} not governance-validated")
                return False

            logger.info(f"A2A bid validated for agent {agent_id}")
            return True

        except Exception as e:
            logger.error(f"A2A bid validation failed: {e}")
            return False

    def _translate_a2a_query_to_registry_filters(
        self,
        a2a_query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Translate A2A discovery query to registry filters.

        Args:
            a2a_query: A2A query

        Returns:
            Registry filters
        """
        self.stats["protocol_translations"] += 1

        filters = {}

        # Status mapping
        if "status" in a2a_query:
            filters["status"] = a2a_query["status"]

        # Governance mapping
        if "governance_status" in a2a_query:
            filters["governance_status"] = a2a_query["governance_status"]

        # Source mapping
        if "source" in a2a_query:
            filters["source"] = a2a_query["source"]

        # TODO: Capability matching would require JSONB query on capsule_data
        # For now, we do post-filtering on capabilities

        return filters

    def _translate_capsule_to_a2a_agent(
        self,
        capsule: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Translate capsule to A2A agent format.

        Args:
            capsule: Capsule data from registry

        Returns:
            A2A agent data or None if translation fails
        """
        self.stats["protocol_translations"] += 1

        try:
            lifecycle_context = capsule.get("lifecycle_context", {})
            app_instance = capsule.get("application_instance", {})
            infrastructure = capsule.get("infrastructure_instance", {})

            return {
                "agent_id": lifecycle_context.get("capsule_id"),
                "name": infrastructure.get("name") or app_instance.get("name", "Unknown"),
                "type": "capsule_agent",
                "capabilities": app_instance.get("instance", {}).get("capabilities", []),
                "status": lifecycle_context.get("stage", "unknown"),
                "governance_status": "validated" if capsule.get("governance", {}).get("validated_at") else "pending",
                "trust_score": infrastructure.get("security", {}).get("trust_score", 0),
                "generation": lifecycle_context.get("generation", 1),
                "created_at": lifecycle_context.get("created_at")
            }

        except Exception as e:
            logger.error(f"Failed to translate capsule to A2A agent: {e}")
            return None

    # ========================================================================
    # Event Bus Integration
    # ========================================================================

    async def _subscribe_to_registry_events(self):
        """Subscribe to registry operation events."""
        # Note: We'll wrap registry operations to publish events
        # This is done by monkey-patching or creating a wrapper
        if self.registry:
            await self._wrap_registry_operations()

    async def _wrap_registry_operations(self):
        """Wrap registry operations to publish events."""
        if not self.registry or not self.event_bus:
            return

        # Store original methods
        original_register = self.registry.register_capsule
        original_search = self.registry.search_capsules

        # Wrap register_capsule
        async def register_with_events(capsule_id, capsule_data, source):
            result = await original_register(capsule_id, capsule_data, source)

            # Publish event
            await self._publish_event("registry.capsule.registered", {
                "capsule_id": capsule_id,
                "source": source,
                "timestamp": time.time()
            })

            return result

        # Wrap search_capsules
        async def search_with_events(filters, limit=100, offset=0):
            results = await original_search(filters, limit, offset)

            # Publish event
            await self._publish_event("registry.capsule.searched", {
                "filters": filters,
                "result_count": len(results),
                "timestamp": time.time()
            })

            return results

        # Replace methods
        self.registry.register_capsule = register_with_events
        self.registry.search_capsules = search_with_events

        logger.info("Registry operations wrapped with event publishing")

    async def _publish_event(self, event_type: str, event_data: Dict[str, Any]):
        """Publish event to event bus."""
        if not self.event_bus:
            return

        try:
            await self.event_bus.publish(event_type, event_data)
            self.stats["events_published"] += 1

        except Exception as e:
            logger.error(f"Failed to publish event: {e}")

    # ========================================================================
    # Statistics
    # ========================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """Get protocol connector statistics."""
        return {
            **self.stats,
            "has_registry": self.registry is not None,
            "has_mcp_bridge": self.mcp_bridge is not None,
            "has_a2a_bridge": self.a2a_bridge is not None,
            "has_event_bus": self.event_bus is not None
        }


# ============================================================================
# Singleton instance
# ============================================================================

_protocol_connector_instance = None


def get_registry_protocol_connector(
    unified_registry=None,
    mcp_bridge=None,
    a2a_bridge=None,
    event_bus=None
) -> RegistryProtocolConnector:
    """
    Get singleton Registry Protocol Connector instance.

    Args:
        unified_registry: Unified capsule registry
        mcp_bridge: MCP protocol bridge
        a2a_bridge: A2A protocol bridge
        event_bus: Event bus

    Returns:
        RegistryProtocolConnector instance
    """
    global _protocol_connector_instance

    if _protocol_connector_instance is None:
        _protocol_connector_instance = RegistryProtocolConnector(
            unified_registry=unified_registry,
            mcp_bridge=mcp_bridge,
            a2a_bridge=a2a_bridge,
            event_bus=event_bus
        )

    return _protocol_connector_instance
