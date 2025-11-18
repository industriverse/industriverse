"""
Integration Orchestrator

Central orchestrator for all layer integration managers in Overseer System.
Initializes, connects, and coordinates all 8 layer integration managers with
event bus, protocol bridges, and Week 17-19 components.

Part of Week 18-19: Architecture Unification - Day 8
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class IntegrationOrchestrator:
    """
    Central orchestrator for all Overseer System integrations.

    Manages:
    - 8 Layer Integration Managers
    - Event Bus coordination
    - Protocol Bridges (MCP, A2A)
    - Week 17-19 Component Integration (Behavioral, Task Execution, DTSL, Registry)
    - AR/VR Integration Adapter

    Architecture:
    ┌───────────────────────────────────────────────────────┐
    │         Integration Orchestrator                       │
    ├───────────────────────────────────────────────────────┤
    │  - Initializes all integration managers                │
    │  - Connects to event bus                               │
    │  - Registers protocol bridges                          │
    │  - Coordinates cross-layer communication               │
    └───────────────────────────────────────────────────────┘
              │                    │                    │
              ▼                    ▼                    ▼
    ┌──────────────────┐  ┌─────────────────┐  ┌────────────────┐
    │ Layer Integration│  │ Event Bus       │  │ Protocol       │
    │ Managers (8)     │  │ (Kafka)         │  │ Bridges        │
    │                  │  │                 │  │ (MCP, A2A)     │
    └──────────────────┘  └─────────────────┘  └────────────────┘
    """

    def __init__(
        self,
        event_bus=None,
        database_pool=None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Integration Orchestrator.

        Args:
            event_bus: Overseer event bus (Kafka)
            database_pool: Database connection pool
            config: Optional configuration
        """
        self.event_bus = event_bus
        self.db_pool = database_pool
        self.config = config or {}

        # Integration Managers
        self.integration_managers: Dict[str, Any] = {}

        # Protocol Bridges
        self.mcp_bridge = None
        self.a2a_bridge = None

        # Week 17-19 Components
        self.capsule_coordinator = None
        self.unified_registry = None
        self.behavioral_client = None
        self.task_execution_engine = None
        self.dtsl_validator = None
        self.ar_vr_adapter = None

        # Initialization state
        self.initialized = False

        logger.info("Integration Orchestrator created")

    async def initialize(self) -> bool:
        """
        Initialize all integration managers and components.

        Steps:
        1. Initialize all 8 layer integration managers
        2. Connect managers to event bus
        3. Initialize protocol bridges
        4. Connect Week 17-19 components
        5. Register AR/VR adapter
        6. Subscribe to key events

        Returns:
            Success status
        """
        if self.initialized:
            logger.warning("Integration Orchestrator already initialized")
            return True

        try:
            logger.info("Initializing Integration Orchestrator...")

            # Step 1: Initialize layer integration managers
            await self._initialize_layer_managers()

            # Step 2: Initialize protocol bridges
            await self._initialize_protocol_bridges()

            # Step 3: Connect Week 17-19 components
            await self._connect_week17_19_components()

            # Step 4: Subscribe to cross-layer events
            await self._subscribe_to_events()

            self.initialized = True

            logger.info("Integration Orchestrator initialization complete")
            logger.info(f"Active integration managers: {list(self.integration_managers.keys())}")

            return True

        except Exception as e:
            logger.error(f"Failed to initialize Integration Orchestrator: {e}")
            return False

    async def _initialize_layer_managers(self):
        """Initialize all 8 layer integration managers."""
        logger.info("Initializing layer integration managers...")

        # Import all integration managers
        from .application_layer_integration_manager import ApplicationLayerIntegrationManager
        from .core_ai_layer_integration_manager import CoreAILayerIntegrationManager
        from .data_layer_integration_manager import DataLayerIntegrationManager
        from .generative_layer_integration_manager import GenerativeLayerIntegrationManager
        from .protocol_layer_integration_manager import ProtocolLayerIntegrationManager
        from .security_compliance_layer_integration_manager import SecurityComplianceLayerIntegrationManager
        from .ui_ux_layer_integration_manager import UIUXLayerIntegrationManager
        from .workflow_automation_layer_integration_manager import WorkflowAutomationLayerIntegrationManager

        # Initialize each manager
        managers_config = [
            ("application_layer", ApplicationLayerIntegrationManager),
            ("core_ai_layer", CoreAILayerIntegrationManager),
            ("data_layer", DataLayerIntegrationManager),
            ("generative_layer", GenerativeLayerIntegrationManager),
            ("protocol_layer", ProtocolLayerIntegrationManager),
            ("security_compliance_layer", SecurityComplianceLayerIntegrationManager),
            ("ui_ux_layer", UIUXLayerIntegrationManager),
            ("workflow_automation_layer", WorkflowAutomationLayerIntegrationManager)
        ]

        for manager_name, ManagerClass in managers_config:
            try:
                manager = ManagerClass(
                    event_bus=self.event_bus,
                    config=self.config.get(manager_name, {})
                )

                # Initialize manager if it has initialize method
                if hasattr(manager, 'initialize'):
                    await manager.initialize()

                self.integration_managers[manager_name] = manager

                logger.info(f"Initialized {manager_name} integration manager")

            except Exception as e:
                logger.error(f"Failed to initialize {manager_name} manager: {e}")
                # Continue with other managers even if one fails
                continue

        logger.info(f"Layer integration managers initialized: {len(self.integration_managers)}/8")

    async def _initialize_protocol_bridges(self):
        """Initialize MCP and A2A protocol bridges."""
        logger.info("Initializing protocol bridges...")

        try:
            # Import protocol bridge modules
            from ..mcp_integration import MCPIntegrationManager
            from ..a2a_integration import A2AIntegrationManager

            # Initialize MCP bridge
            self.mcp_bridge = MCPIntegrationManager(
                event_bus=self.event_bus,
                config=self.config.get("mcp", {})
            )
            if hasattr(self.mcp_bridge, 'initialize'):
                await self.mcp_bridge.initialize()

            logger.info("MCP protocol bridge initialized")

            # Initialize A2A bridge
            self.a2a_bridge = A2AIntegrationManager(
                event_bus=self.event_bus,
                config=self.config.get("a2a", {})
            )
            if hasattr(self.a2a_bridge, 'initialize'):
                await self.a2a_bridge.initialize()

            logger.info("A2A protocol bridge initialized")

        except ImportError as e:
            logger.warning(f"Protocol bridge modules not available: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize protocol bridges: {e}")

    async def _connect_week17_19_components(self):
        """Connect Week 17-19 unified architecture components."""
        logger.info("Connecting Week 17-19 components...")

        try:
            # Import Week 17-19 components
            from ..capsule_lifecycle import (
                get_capsule_lifecycle_coordinator,
                get_unified_capsule_registry
            )
            from .ar_vr_integration_adapter import get_ar_vr_integration_adapter

            # Get capsule coordinator and registry
            self.capsule_coordinator = get_capsule_lifecycle_coordinator(
                event_bus=self.event_bus,
                database_pool=self.db_pool
            )

            self.unified_registry = get_unified_capsule_registry(
                database_pool=self.db_pool
            )

            # Register registry with coordinator
            if self.capsule_coordinator:
                self.capsule_coordinator.register_unified_registry(self.unified_registry)

            logger.info("Capsule lifecycle coordinator and registry connected")

            # Get AR/VR adapter
            self.ar_vr_adapter = get_ar_vr_integration_adapter(
                event_bus=self.event_bus,
                capsule_coordinator=self.capsule_coordinator
            )

            logger.info("AR/VR integration adapter connected")

        except ImportError as e:
            logger.warning(f"Week 17-19 components not fully available: {e}")
        except Exception as e:
            logger.error(f"Failed to connect Week 17-19 components: {e}")

        try:
            # Import Week 17 components
            from ...application_layer.behavioral_tracking.api_bridge import (
                get_behavioral_tracking_client
            )
            from ...protocol_layer.protocols.a2a import get_a2a_task_execution_engine
            from ...protocol_layer.protocols.dtsl import get_dtsl_schema_validator

            # Get behavioral tracking client
            self.behavioral_client = get_behavioral_tracking_client(
                database_pool=self.db_pool
            )

            logger.info("Behavioral tracking client connected")

            # Get A2A task execution engine
            self.task_execution_engine = get_a2a_task_execution_engine()

            logger.info("A2A task execution engine connected")

            # Get DTSL validator
            self.dtsl_validator = get_dtsl_schema_validator()

            logger.info("DTSL schema validator connected")

        except ImportError as e:
            logger.warning(f"Week 17 components not fully available: {e}")
        except Exception as e:
            logger.error(f"Failed to connect Week 17 components: {e}")

    async def _subscribe_to_events(self):
        """Subscribe to key cross-layer events."""
        if not self.event_bus:
            logger.warning("No event bus - skipping event subscriptions")
            return

        logger.info("Subscribing to cross-layer events...")

        try:
            # Subscribe to capsule lifecycle events
            self.event_bus.subscribe("capsule.lifecycle.created", self._handle_capsule_created)
            self.event_bus.subscribe("capsule.lifecycle.failed", self._handle_capsule_failed)

            # Subscribe to AR/VR events
            self.event_bus.subscribe("ar_vr.capsule.spawned", self._handle_ar_capsule_spawned)
            self.event_bus.subscribe("ar_vr.interaction", self._handle_ar_interaction)

            # Subscribe to behavioral events
            self.event_bus.subscribe("behavioral.interaction", self._handle_behavioral_event)

            # Subscribe to task execution events
            self.event_bus.subscribe("task.submitted", self._handle_task_submitted)
            self.event_bus.subscribe("task.completed", self._handle_task_completed)

            logger.info("Cross-layer event subscriptions complete")

        except Exception as e:
            logger.error(f"Failed to subscribe to events: {e}")

    # ========================================================================
    # Event Handlers
    # ========================================================================

    async def _handle_capsule_created(self, event: Dict[str, Any]):
        """Handle capsule creation event."""
        logger.info(f"Capsule created: {event.get('capsule_id')}")

        # Notify all relevant layer managers
        if "application_layer" in self.integration_managers:
            await self.integration_managers["application_layer"].handle_capsule_created(event)

        if "ui_ux_layer" in self.integration_managers:
            await self.integration_managers["ui_ux_layer"].handle_capsule_created(event)

    async def _handle_capsule_failed(self, event: Dict[str, Any]):
        """Handle capsule creation failure event."""
        logger.warning(f"Capsule creation failed: {event.get('capsule_id')} - {event.get('error')}")

        # Notify security/compliance layer
        if "security_compliance_layer" in self.integration_managers:
            await self.integration_managers["security_compliance_layer"].handle_capsule_failed(event)

    async def _handle_ar_capsule_spawned(self, event: Dict[str, Any]):
        """Handle AR capsule spawn event."""
        logger.info(f"AR capsule spawned: {event.get('capsule_id')} in {event.get('environment_id')}")

        # Notify UI/UX layer
        if "ui_ux_layer" in self.integration_managers:
            await self.integration_managers["ui_ux_layer"].handle_ar_capsule_spawned(event)

    async def _handle_ar_interaction(self, event: Dict[str, Any]):
        """Handle AR interaction event."""
        logger.info(f"AR interaction: {event.get('interaction_type')}")

        # Route to behavioral tracking if available
        if self.behavioral_client:
            # Behavioral client will track the interaction
            pass

    async def _handle_behavioral_event(self, event: Dict[str, Any]):
        """Handle behavioral tracking event."""
        logger.debug(f"Behavioral event: {event.get('event_type')}")

        # Analytics processing could happen here
        pass

    async def _handle_task_submitted(self, event: Dict[str, Any]):
        """Handle task submission event."""
        logger.info(f"Task submitted: {event.get('task_id')}")

        # Notify workflow automation layer
        if "workflow_automation_layer" in self.integration_managers:
            await self.integration_managers["workflow_automation_layer"].handle_task_submitted(event)

    async def _handle_task_completed(self, event: Dict[str, Any]):
        """Handle task completion event."""
        logger.info(f"Task completed: {event.get('task_id')}")

        # Notify application layer
        if "application_layer" in self.integration_managers:
            await self.integration_managers["application_layer"].handle_task_completed(event)

    # ========================================================================
    # Public Methods
    # ========================================================================

    def get_integration_manager(self, layer_name: str) -> Optional[Any]:
        """Get integration manager for specific layer."""
        return self.integration_managers.get(layer_name)

    def get_all_integration_managers(self) -> Dict[str, Any]:
        """Get all integration managers."""
        return self.integration_managers.copy()

    def get_protocol_bridges(self) -> Dict[str, Any]:
        """Get protocol bridges."""
        return {
            "mcp": self.mcp_bridge,
            "a2a": self.a2a_bridge
        }

    def get_week17_19_components(self) -> Dict[str, Any]:
        """Get Week 17-19 unified components."""
        return {
            "capsule_coordinator": self.capsule_coordinator,
            "unified_registry": self.unified_registry,
            "behavioral_client": self.behavioral_client,
            "task_execution_engine": self.task_execution_engine,
            "dtsl_validator": self.dtsl_validator,
            "ar_vr_adapter": self.ar_vr_adapter
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        return {
            "initialized": self.initialized,
            "integration_managers_count": len(self.integration_managers),
            "integration_managers": list(self.integration_managers.keys()),
            "has_mcp_bridge": self.mcp_bridge is not None,
            "has_a2a_bridge": self.a2a_bridge is not None,
            "has_capsule_coordinator": self.capsule_coordinator is not None,
            "has_unified_registry": self.unified_registry is not None,
            "has_behavioral_client": self.behavioral_client is not None,
            "has_task_execution_engine": self.task_execution_engine is not None,
            "has_dtsl_validator": self.dtsl_validator is not None,
            "has_ar_vr_adapter": self.ar_vr_adapter is not None
        }


# ============================================================================
# Singleton instance
# ============================================================================

_orchestrator_instance = None


def get_integration_orchestrator(
    event_bus=None,
    database_pool=None,
    config: Optional[Dict[str, Any]] = None
) -> IntegrationOrchestrator:
    """
    Get singleton Integration Orchestrator instance.

    Args:
        event_bus: Event bus
        database_pool: Database connection pool
        config: Configuration

    Returns:
        IntegrationOrchestrator instance
    """
    global _orchestrator_instance

    if _orchestrator_instance is None:
        _orchestrator_instance = IntegrationOrchestrator(
            event_bus=event_bus,
            database_pool=database_pool,
            config=config
        )

    return _orchestrator_instance
