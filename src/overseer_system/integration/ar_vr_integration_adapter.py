"""
AR/VR Integration Adapter

Connects Overseer System to UI/UX Layer AR/VR modules for:
- Capsule orchestration in AR/VR environments
- Spatial data synchronization
- AR/VR command processing (via A2A protocol)
- User interaction tracking (via behavioral tracking)
- MCP context integration for AR/VR state

Part of Week 18-19: Architecture Unification - Day 5
"""

import logging
import asyncio
import time
from typing import Dict, Any, List, Optional, Callable
from enum import Enum

logger = logging.getLogger(__name__)


class AREnvironmentType(Enum):
    """AR/VR environment types."""
    MOBILE_AR = "mobile_ar"  # ARKit, ARCore
    HEADSET_AR = "headset_ar"  # HoloLens, Magic Leap
    HEADSET_VR = "headset_vr"  # Oculus, Vive, Index
    WEBXR_AR = "webxr_ar"  # WebXR AR
    WEBXR_VR = "webxr_vr"  # WebXR VR


class SpatialInteractionType(Enum):
    """Types of spatial interactions."""
    HAND_TRACKING = "hand_tracking"
    CONTROLLER_INPUT = "controller_input"
    GAZE_INPUT = "gaze_input"
    VOICE_COMMAND = "voice_command"
    GESTURE_RECOGNITION = "gesture_recognition"


class ARVRIntegrationAdapter:
    """
    Bidirectional bridge between Overseer System and AR/VR modules.

    Architecture:
    ┌─────────────────────────────────────────────────────┐
    │        ARVRIntegrationAdapter                        │
    ├─────────────────────────────────────────────────────┤
    │                                                      │
    │  Overseer ←→ AR/VR Manager ←→ Capsule Coordinator   │
    │      ↓              ↓                  ↓            │
    │  Event Bus   Spatial State      Behavioral          │
    │              Persistence         Tracking            │
    │                                                      │
    └─────────────────────────────────────────────────────┘
              │                    │                    │
              ▼                    ▼                    ▼
    ┌──────────────────┐  ┌─────────────────┐  ┌────────────────┐
    │ UI/UX Layer      │  │ Data Layer      │  │ Protocol Layer │
    │ AR/VR Manager    │  │ AR State Store  │  │ A2A/MCP        │
    └──────────────────┘  └─────────────────┘  └────────────────┘

    Responsibilities:
    1. Capsule spawning in AR/VR environments
    2. AR/VR interaction event processing
    3. Spatial anchor synchronization
    4. Behavioral tracking integration
    5. MCP context propagation
    6. A2A command routing to AR/VR
    """

    def __init__(
        self,
        event_bus=None,
        ar_vr_manager=None,
        capsule_coordinator=None,
        behavioral_client=None,
        ar_state_manager=None
    ):
        """
        Initialize AR/VR Integration Adapter.

        Args:
            event_bus: Overseer event bus for publishing AR/VR events
            ar_vr_manager: UI/UX Layer AR/VR integration manager
            capsule_coordinator: Capsule lifecycle coordinator
            behavioral_client: Behavioral tracking client
            ar_state_manager: AR/VR state persistence manager
        """
        self.event_bus = event_bus
        self.ar_vr_manager = ar_vr_manager
        self.capsule_coordinator = capsule_coordinator
        self.behavioral_client = behavioral_client
        self.ar_state_manager = ar_state_manager

        # Active AR/VR environments: {environment_id: environment_data}
        self.active_environments: Dict[str, Dict[str, Any]] = {}

        # AR capsule instances: {capsule_id: ar_instance_data}
        self.ar_capsule_instances: Dict[str, Dict[str, Any]] = {}

        # Interaction event handlers
        self.interaction_handlers: Dict[SpatialInteractionType, List[Callable]] = {
            interaction_type: [] for interaction_type in SpatialInteractionType
        }

        # Statistics
        self.stats = {
            "capsules_spawned": 0,
            "interactions_processed": 0,
            "spatial_anchors_synced": 0,
            "environments_active": 0
        }

        logger.info("AR/VR Integration Adapter initialized")

    # ========================================================================
    # Environment Management
    # ========================================================================

    async def register_ar_environment(
        self,
        environment_id: str,
        environment_type: AREnvironmentType,
        user_id: str,
        session_id: str,
        capabilities: List[str] = None
    ) -> Dict[str, Any]:
        """
        Register an active AR/VR environment.

        Args:
            environment_id: Unique environment identifier
            environment_type: Type of AR/VR environment
            user_id: User ID
            session_id: Session ID
            capabilities: List of environment capabilities

        Returns:
            Registration result
        """
        try:
            environment_data = {
                "environment_id": environment_id,
                "environment_type": environment_type.value,
                "user_id": user_id,
                "session_id": session_id,
                "capabilities": capabilities or [],
                "registered_at": time.time(),
                "active_capsules": [],
                "spatial_anchors": {}
            }

            self.active_environments[environment_id] = environment_data
            self.stats["environments_active"] = len(self.active_environments)

            # Publish to event bus
            await self._publish_event("ar_vr.environment.registered", {
                "environment_id": environment_id,
                "environment_type": environment_type.value,
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": time.time()
            })

            # Track in behavioral system
            if self.behavioral_client:
                await self._track_behavioral_event(
                    user_id=user_id,
                    session_id=session_id,
                    event_type="ar_environment_registered",
                    event_data={
                        "environment_id": environment_id,
                        "environment_type": environment_type.value
                    }
                )

            logger.info(f"AR/VR environment registered: {environment_id} (type: {environment_type.value})")

            return {
                "status": "success",
                "environment_id": environment_id
            }

        except Exception as e:
            logger.error(f"Failed to register AR/VR environment: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def unregister_ar_environment(self, environment_id: str):
        """Unregister AR/VR environment."""
        if environment_id in self.active_environments:
            environment_data = self.active_environments[environment_id]

            # Cleanup all capsules in this environment
            for capsule_id in environment_data.get("active_capsules", []):
                await self.despawn_ar_capsule(capsule_id, environment_id)

            del self.active_environments[environment_id]
            self.stats["environments_active"] = len(self.active_environments)

            await self._publish_event("ar_vr.environment.unregistered", {
                "environment_id": environment_id,
                "timestamp": time.time()
            })

            logger.info(f"AR/VR environment unregistered: {environment_id}")

    # ========================================================================
    # Capsule Orchestration in AR/VR
    # ========================================================================

    async def orchestrate_ar_capsule_spawn(
        self,
        capsule_id: str,
        environment_id: str,
        spatial_anchor: Dict[str, Any],
        spawn_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate capsule spawning in AR/VR environment.

        Flow:
        1. Validate environment exists and is active
        2. Request capsule from unified registry
        3. Adapt capsule data for AR rendering (morphology)
        4. Determine spatial placement using spatial_awareness_engine
        5. Create spatial anchor in AR environment
        6. Send spawn command to AR/VR manager
        7. Track spawn event in behavioral tracking
        8. Persist AR capsule state to data layer
        9. Publish spawn event to event bus

        Args:
            capsule_id: Capsule ID from unified registry
            environment_id: AR/VR environment ID
            spatial_anchor: Spatial anchor data (position, rotation, scale)
            spawn_config: Optional spawn configuration

        Returns:
            Spawn result with AR instance data
        """
        if environment_id not in self.active_environments:
            return {
                "status": "error",
                "error": f"Environment not found: {environment_id}"
            }

        try:
            logger.info(f"Orchestrating AR capsule spawn: {capsule_id} in {environment_id}")

            environment = self.active_environments[environment_id]
            spawn_config = spawn_config or {}

            # Step 1: Get capsule from unified registry (via coordinator)
            if not self.capsule_coordinator or not self.capsule_coordinator.unified_registry:
                return {
                    "status": "error",
                    "error": "Capsule coordinator or registry not available"
                }

            capsule = await self.capsule_coordinator.unified_registry.get_capsule(capsule_id)

            if not capsule:
                return {
                    "status": "error",
                    "error": f"Capsule not found in registry: {capsule_id}"
                }

            # Step 2: Adapt capsule for AR rendering
            ar_capsule = await self._adapt_capsule_for_ar(capsule, environment, spawn_config)

            # Step 3: Create spatial anchor
            anchor_id = await self._create_spatial_anchor(
                environment_id=environment_id,
                spatial_anchor=spatial_anchor,
                capsule_id=capsule_id
            )

            # Step 4: Send spawn command to AR/VR manager
            if self.ar_vr_manager:
                ar_spawn_result = await self._send_ar_spawn_command(
                    ar_vr_manager=self.ar_vr_manager,
                    environment_id=environment_id,
                    ar_capsule=ar_capsule,
                    anchor_id=anchor_id
                )
            else:
                logger.warning("AR/VR manager not available - simulating spawn")
                ar_spawn_result = {
                    "status": "simulated",
                    "ar_instance_id": f"ar-{capsule_id}"
                }

            # Step 5: Track AR capsule instance
            ar_instance_data = {
                "capsule_id": capsule_id,
                "environment_id": environment_id,
                "anchor_id": anchor_id,
                "ar_instance_id": ar_spawn_result.get("ar_instance_id"),
                "spawned_at": time.time(),
                "ar_capsule": ar_capsule,
                "spawn_config": spawn_config
            }

            self.ar_capsule_instances[capsule_id] = ar_instance_data
            environment["active_capsules"].append(capsule_id)

            # Step 6: Persist AR capsule state
            if self.ar_state_manager:
                await self.ar_state_manager.save_ar_capsule_state(
                    capsule_id=capsule_id,
                    ar_state={
                        "environment_id": environment_id,
                        "anchor_id": anchor_id,
                        "ar_instance_id": ar_spawn_result.get("ar_instance_id"),
                        "visible": True,
                        "interaction_state": "idle",
                        "spawned_at": time.time()
                    }
                )

            # Step 7: Track in behavioral system
            if self.behavioral_client:
                await self._track_behavioral_event(
                    user_id=environment["user_id"],
                    session_id=environment["session_id"],
                    event_type="ar_capsule_spawned",
                    event_data={
                        "capsule_id": capsule_id,
                        "environment_id": environment_id,
                        "anchor_id": anchor_id
                    }
                )

            # Step 8: Publish to event bus
            await self._publish_event("ar_vr.capsule.spawned", {
                "capsule_id": capsule_id,
                "environment_id": environment_id,
                "ar_instance_id": ar_spawn_result.get("ar_instance_id"),
                "timestamp": time.time()
            })

            self.stats["capsules_spawned"] += 1

            logger.info(f"AR capsule spawned successfully: {capsule_id} (ar_instance: {ar_spawn_result.get('ar_instance_id')})")

            return {
                "status": "success",
                "capsule_id": capsule_id,
                "ar_instance_id": ar_spawn_result.get("ar_instance_id"),
                "anchor_id": anchor_id,
                "ar_instance_data": ar_instance_data
            }

        except Exception as e:
            logger.error(f"Failed to spawn AR capsule: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def despawn_ar_capsule(
        self,
        capsule_id: str,
        environment_id: str
    ) -> Dict[str, Any]:
        """Despawn capsule from AR/VR environment."""
        try:
            if capsule_id not in self.ar_capsule_instances:
                return {
                    "status": "error",
                    "error": f"AR capsule instance not found: {capsule_id}"
                }

            ar_instance = self.ar_capsule_instances[capsule_id]

            # Send despawn command to AR/VR manager
            if self.ar_vr_manager:
                await self._send_ar_despawn_command(
                    ar_vr_manager=self.ar_vr_manager,
                    environment_id=environment_id,
                    ar_instance_id=ar_instance.get("ar_instance_id")
                )

            # Remove from tracking
            del self.ar_capsule_instances[capsule_id]

            if environment_id in self.active_environments:
                environment = self.active_environments[environment_id]
                if capsule_id in environment["active_capsules"]:
                    environment["active_capsules"].remove(capsule_id)

            # Update AR state
            if self.ar_state_manager:
                await self.ar_state_manager.save_ar_capsule_state(
                    capsule_id=capsule_id,
                    ar_state={
                        "visible": False,
                        "despawned_at": time.time()
                    }
                )

            await self._publish_event("ar_vr.capsule.despawned", {
                "capsule_id": capsule_id,
                "environment_id": environment_id,
                "timestamp": time.time()
            })

            logger.info(f"AR capsule despawned: {capsule_id}")

            return {"status": "success"}

        except Exception as e:
            logger.error(f"Failed to despawn AR capsule: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    # ========================================================================
    # AR/VR Interaction Handling
    # ========================================================================

    async def handle_ar_interaction_event(
        self,
        event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle AR/VR interaction events (gaze, hand tracking, voice, gestures).

        Flow:
        1. Validate interaction event
        2. Translate AR interaction to capsule command
        3. Route command to A2A task execution engine
        4. Track interaction in behavioral system
        5. Update AR visualization based on command result
        6. Publish interaction event to event bus

        Args:
            event: Interaction event data
                {
                    "environment_id": str,
                    "capsule_id": str (optional),
                    "interaction_type": SpatialInteractionType,
                    "interaction_data": dict,
                    "timestamp": float
                }

        Returns:
            Interaction processing result
        """
        try:
            environment_id = event.get("environment_id")
            capsule_id = event.get("capsule_id")
            interaction_type = event.get("interaction_type")
            interaction_data = event.get("interaction_data", {})

            if environment_id not in self.active_environments:
                return {
                    "status": "error",
                    "error": f"Environment not found: {environment_id}"
                }

            environment = self.active_environments[environment_id]

            logger.info(f"Handling AR interaction: {interaction_type} in {environment_id}")

            # Step 1: Execute registered interaction handlers
            if interaction_type in self.interaction_handlers:
                for handler in self.interaction_handlers[interaction_type]:
                    try:
                        await handler(event)
                    except Exception as e:
                        logger.error(f"Interaction handler error: {e}")

            # Step 2: Translate to capsule command (A2A integration point)
            if capsule_id:
                capsule_command = self._translate_interaction_to_command(
                    interaction_type=interaction_type,
                    interaction_data=interaction_data,
                    capsule_id=capsule_id
                )

                # Day 9 Complete: A2A routing now handled by RegistryProtocolConnector
                # The connector validates bids and enables A2A discovery via the registry
                logger.info(f"Capsule command generated: {capsule_command}")

            # Step 3: Track in behavioral system
            if self.behavioral_client:
                await self._track_behavioral_event(
                    user_id=environment["user_id"],
                    session_id=environment["session_id"],
                    event_type=f"ar_interaction_{interaction_type}",
                    event_data={
                        "environment_id": environment_id,
                        "capsule_id": capsule_id,
                        "interaction_type": interaction_type,
                        "interaction_data": interaction_data
                    }
                )

            # Step 4: Publish to event bus
            await self._publish_event("ar_vr.interaction", event)

            self.stats["interactions_processed"] += 1

            return {
                "status": "success",
                "interaction_type": interaction_type
            }

        except Exception as e:
            logger.error(f"Failed to handle AR interaction: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def register_interaction_handler(
        self,
        interaction_type: SpatialInteractionType,
        handler: Callable
    ):
        """Register handler for specific interaction type."""
        self.interaction_handlers[interaction_type].append(handler)
        logger.info(f"Registered interaction handler for: {interaction_type.value}")

    # ========================================================================
    # Helper Methods
    # ========================================================================

    async def _adapt_capsule_for_ar(
        self,
        capsule: Dict[str, Any],
        environment: Dict[str, Any],
        spawn_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adapt capsule data for AR rendering."""
        # Extract relevant capsule data
        lifecycle_context = capsule.get("lifecycle_context", {})
        infrastructure = capsule.get("infrastructure_instance", {})

        # Create AR-specific capsule representation
        ar_capsule = {
            "capsule_id": lifecycle_context.get("capsule_id"),
            "name": infrastructure.get("name", "Capsule"),
            "description": infrastructure.get("description", ""),
            "visual_config": {
                "model": spawn_config.get("model", "default_capsule"),
                "scale": spawn_config.get("scale", {"x": 1.0, "y": 1.0, "z": 1.0}),
                "color": spawn_config.get("color", "#4A90E2"),
                "opacity": spawn_config.get("opacity", 1.0)
            },
            "interaction_config": {
                "enabled": True,
                "interaction_types": environment.get("capabilities", [])
            },
            "metadata": {
                "source": lifecycle_context.get("source"),
                "generation": lifecycle_context.get("generation"),
                "governance_status": capsule.get("governance", {}).get("validated_at") is not None
            }
        }

        return ar_capsule

    async def _create_spatial_anchor(
        self,
        environment_id: str,
        spatial_anchor: Dict[str, Any],
        capsule_id: str
    ) -> str:
        """Create spatial anchor in AR environment."""
        anchor_id = f"anchor-{capsule_id}"

        # Persist spatial anchor
        if self.ar_state_manager:
            await self.ar_state_manager.save_spatial_anchor(
                anchor_id=anchor_id,
                position=spatial_anchor.get("position", {"x": 0, "y": 0, "z": 0}),
                rotation=spatial_anchor.get("rotation", {"x": 0, "y": 0, "z": 0, "w": 1}),
                environment_id=environment_id,
                metadata={"capsule_id": capsule_id}
            )

        # Track in environment
        environment = self.active_environments[environment_id]
        environment["spatial_anchors"][anchor_id] = spatial_anchor

        self.stats["spatial_anchors_synced"] += 1

        return anchor_id

    async def _send_ar_spawn_command(
        self,
        ar_vr_manager,
        environment_id: str,
        ar_capsule: Dict[str, Any],
        anchor_id: str
    ) -> Dict[str, Any]:
        """Send spawn command to AR/VR manager."""
        # TODO: Integrate with actual AR/VR manager from UI/UX Layer
        logger.info(f"Sending AR spawn command: {ar_capsule['capsule_id']} at {anchor_id}")
        return {
            "status": "spawned",
            "ar_instance_id": f"ar-instance-{ar_capsule['capsule_id']}"
        }

    async def _send_ar_despawn_command(
        self,
        ar_vr_manager,
        environment_id: str,
        ar_instance_id: str
    ):
        """Send despawn command to AR/VR manager."""
        # TODO: Integrate with actual AR/VR manager
        logger.info(f"Sending AR despawn command: {ar_instance_id}")

    def _translate_interaction_to_command(
        self,
        interaction_type: str,
        interaction_data: Dict[str, Any],
        capsule_id: str
    ) -> Dict[str, Any]:
        """Translate AR interaction to capsule command (A2A format)."""
        # Map interaction types to capsule commands
        command_mapping = {
            "hand_tracking": "capsule.interact.touch",
            "controller_input": "capsule.interact.select",
            "gaze_input": "capsule.interact.focus",
            "voice_command": "capsule.interact.voice",
            "gesture_recognition": "capsule.interact.gesture"
        }

        return {
            "command": command_mapping.get(interaction_type, "capsule.interact.generic"),
            "capsule_id": capsule_id,
            "parameters": interaction_data,
            "timestamp": time.time()
        }

    async def _track_behavioral_event(
        self,
        user_id: str,
        session_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ):
        """Track event in behavioral tracking system."""
        if not self.behavioral_client:
            return

        try:
            await self.behavioral_client.track_interaction({
                "user_id": user_id,
                "session_id": session_id,
                "event_type": event_type,
                "timestamp": time.time(),
                "interaction_data": event_data
            })
        except Exception as e:
            logger.error(f"Behavioral tracking error: {e}")

    async def _publish_event(self, event_type: str, event_data: Dict[str, Any]):
        """Publish event to event bus."""
        if not self.event_bus:
            return

        try:
            await self.event_bus.publish(event_type, event_data)
        except Exception as e:
            logger.error(f"Event publishing error: {e}")

    # ========================================================================
    # Statistics
    # ========================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """Get adapter statistics."""
        return {
            **self.stats,
            "active_environments": len(self.active_environments),
            "active_ar_capsules": len(self.ar_capsule_instances)
        }


# ============================================================================
# Singleton instance
# ============================================================================

_ar_vr_adapter_instance = None


def get_ar_vr_integration_adapter(
    event_bus=None,
    ar_vr_manager=None,
    capsule_coordinator=None,
    behavioral_client=None,
    ar_state_manager=None
) -> ARVRIntegrationAdapter:
    """
    Get singleton AR/VR Integration Adapter instance.

    Args:
        event_bus: Event bus
        ar_vr_manager: AR/VR manager from UI/UX Layer
        capsule_coordinator: Capsule lifecycle coordinator
        behavioral_client: Behavioral tracking client
        ar_state_manager: AR/VR state manager

    Returns:
        ARVRIntegrationAdapter instance
    """
    global _ar_vr_adapter_instance

    if _ar_vr_adapter_instance is None:
        _ar_vr_adapter_instance = ARVRIntegrationAdapter(
            event_bus=event_bus,
            ar_vr_manager=ar_vr_manager,
            capsule_coordinator=capsule_coordinator,
            behavioral_client=behavioral_client,
            ar_state_manager=ar_state_manager
        )

    return _ar_vr_adapter_instance
