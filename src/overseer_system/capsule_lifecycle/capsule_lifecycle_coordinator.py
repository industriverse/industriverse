"""
Capsule Lifecycle Coordinator

Central orchestrator for capsule lifecycle management across all layers.
Coordinates between Application Layer (template-based creation) and
Deployment Operations Layer (infrastructure instantiation), ensuring
governance, evolution tracking, and unified registry management.

Part of Week 18-19: Architecture Unification
"""

import logging
import asyncio
import uuid
import time
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field

# Configure logging
logger = logging.getLogger(__name__)


class CapsuleLifecycleStage(Enum):
    """Capsule lifecycle stages."""
    REQUESTED = "requested"
    GOVERNANCE_REVIEW = "governance_review"
    GOVERNANCE_APPROVED = "governance_approved"
    GOVERNANCE_REJECTED = "governance_rejected"
    INFRASTRUCTURE_PROVISIONING = "infrastructure_provisioning"
    INFRASTRUCTURE_READY = "infrastructure_ready"
    ACTIVE = "active"
    EVOLVING = "evolving"
    DEPRECATED = "deprecated"
    DECOMMISSIONED = "decommissioned"


class CapsuleSource(Enum):
    """Source of capsule creation."""
    APPLICATION_LAYER = "application_layer"
    DEPLOYMENT_OPS_LAYER = "deployment_ops_layer"
    EXTERNAL_API = "external_api"
    EVOLUTION = "evolution"


@dataclass
class CapsuleLifecycleContext:
    """
    Context for capsule lifecycle management.
    """
    capsule_id: str
    source: CapsuleSource
    stage: CapsuleLifecycleStage
    template_id: Optional[str] = None
    blueprint_id: Optional[str] = None
    instance_config: Dict[str, Any] = field(default_factory=dict)
    deployment_context: Dict[str, Any] = field(default_factory=dict)
    governance_metadata: Dict[str, Any] = field(default_factory=dict)
    evolution_metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    parent_capsule_id: Optional[str] = None
    generation: int = 1
    errors: List[str] = field(default_factory=list)


class CapsuleLifecycleCoordinator:
    """
    Coordinates capsule lifecycle across all layers.

    Architecture:
    ┌─────────────────────────────────────────────────────┐
    │         CapsuleLifecycleCoordinator                  │
    ├─────────────────────────────────────────────────────┤
    │                                                      │
    │  Request → Governance → Blueprint → Infrastructure  │
    │            ↓            ↓           ↓               │
    │         Evolution   Registry    Monitoring          │
    │                                                      │
    └─────────────────────────────────────────────────────┘
              │                    │                    │
              ▼                    ▼                    ▼
    ┌──────────────────┐  ┌─────────────────┐  ┌────────────────┐
    │ Application      │  │ Deployment Ops  │  │ Overseer       │
    │ Layer Factory    │  │ Layer Factory   │  │ Services       │
    │ (Templates)      │  │ (Infrastructure)│  │ (Governance)   │
    └──────────────────┘  └─────────────────┘  └────────────────┘

    Flow:
    1. Receive capsule creation request (template-based or blueprint-based)
    2. Validate against governance policies
    3. Enrich with evolution metadata
    4. Create application-level instance (if template-based)
    5. Generate/validate blueprint
    6. Create infrastructure instance
    7. Register in unified registry
    8. Initialize monitoring and evolution tracking
    9. Publish lifecycle events to event bus
    """

    def __init__(
        self,
        event_bus=None,
        database_pool=None
    ):
        """
        Initialize the Capsule Lifecycle Coordinator.

        Args:
            event_bus: Event bus for publishing lifecycle events
            database_pool: Database connection pool for registry
        """
        self.event_bus = event_bus
        self.db_pool = database_pool

        # Factory references (registered by factories)
        self.app_factory = None  # Application Layer AgentCapsuleFactory
        self.deploy_factory = None  # Deployment Ops CapsuleFactory

        # Service references (registered by Overseer services)
        self.governance_service = None  # Capsule governance
        self.evolution_service = None  # Capsule evolution
        self.unified_registry = None  # Unified capsule registry

        # Lifecycle tracking
        self.active_lifecycles: Dict[str, CapsuleLifecycleContext] = {}
        self.lifecycle_callbacks: Dict[CapsuleLifecycleStage, List[Callable]] = {
            stage: [] for stage in CapsuleLifecycleStage
        }

        # Statistics
        self.stats = {
            "total_requests": 0,
            "governance_approved": 0,
            "governance_rejected": 0,
            "infrastructure_provisioned": 0,
            "active_capsules": 0,
            "failed_creations": 0
        }

        logger.info("Capsule Lifecycle Coordinator initialized")

    # ========================================================================
    # Factory and Service Registration
    # ========================================================================

    def register_app_factory(self, factory):
        """Register Application Layer factory."""
        self.app_factory = factory
        logger.info("Application Layer factory registered with coordinator")

    def register_deploy_factory(self, factory):
        """Register Deployment Operations Layer factory."""
        self.deploy_factory = factory
        logger.info("Deployment Operations Layer factory registered with coordinator")

    def register_governance_service(self, service):
        """Register governance service."""
        self.governance_service = service
        logger.info("Governance service registered with coordinator")

    def register_evolution_service(self, service):
        """Register evolution service."""
        self.evolution_service = service
        logger.info("Evolution service registered with coordinator")

    def register_unified_registry(self, registry):
        """Register unified capsule registry."""
        self.unified_registry = registry
        logger.info("Unified capsule registry registered with coordinator")

    def register_lifecycle_callback(
        self,
        stage: CapsuleLifecycleStage,
        callback: Callable
    ):
        """
        Register callback for specific lifecycle stage.

        Args:
            stage: Lifecycle stage
            callback: Callback function(capsule_context) -> None
        """
        self.lifecycle_callbacks[stage].append(callback)
        logger.info(f"Registered callback for stage: {stage.value}")

    # ========================================================================
    # Main Lifecycle Orchestration
    # ========================================================================

    async def create_capsule_full_lifecycle(
        self,
        template_id: Optional[str] = None,
        blueprint: Optional[Dict[str, Any]] = None,
        instance_config: Dict[str, Any] = None,
        deployment_context: Dict[str, Any] = None,
        source: CapsuleSource = CapsuleSource.APPLICATION_LAYER,
        parent_capsule_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete capsule creation with full lifecycle management.

        Supports two creation modes:
        1. Template-based (template_id): Application Layer → Blueprint → Infrastructure
        2. Blueprint-based (blueprint): Direct Infrastructure creation

        Args:
            template_id: Template ID for template-based creation
            blueprint: Blueprint dictionary for direct creation
            instance_config: Instance configuration
            deployment_context: Deployment context
            source: Source of creation
            parent_capsule_id: Parent capsule ID (for evolution)

        Returns:
            Dictionary with creation result and capsule details

        Steps:
        1. Create lifecycle context
        2. Validate governance policies
        3. Create application instance (if template-based)
        4. Generate/validate blueprint
        5. Create infrastructure instance
        6. Register in unified registry
        7. Initialize evolution tracking
        8. Publish lifecycle events
        """
        instance_config = instance_config or {}
        deployment_context = deployment_context or {}

        # Generate capsule ID
        capsule_id = f"capsule-{str(uuid.uuid4())}"

        # Create lifecycle context
        lifecycle_context = CapsuleLifecycleContext(
            capsule_id=capsule_id,
            source=source,
            stage=CapsuleLifecycleStage.REQUESTED,
            template_id=template_id,
            blueprint_id=blueprint.get("metadata", {}).get("id") if blueprint else None,
            instance_config=instance_config,
            deployment_context=deployment_context,
            parent_capsule_id=parent_capsule_id,
            generation=1 if not parent_capsule_id else await self._get_parent_generation(parent_capsule_id) + 1
        )

        # Track lifecycle
        self.active_lifecycles[capsule_id] = lifecycle_context
        self.stats["total_requests"] += 1

        try:
            # Step 1: Governance Review
            await self._transition_stage(lifecycle_context, CapsuleLifecycleStage.GOVERNANCE_REVIEW)
            governance_result = await self._validate_governance(lifecycle_context)

            if not governance_result["approved"]:
                await self._transition_stage(lifecycle_context, CapsuleLifecycleStage.GOVERNANCE_REJECTED)
                self.stats["governance_rejected"] += 1
                return {
                    "status": "rejected",
                    "capsule_id": capsule_id,
                    "reason": governance_result.get("reason", "governance_violation"),
                    "lifecycle_context": lifecycle_context
                }

            await self._transition_stage(lifecycle_context, CapsuleLifecycleStage.GOVERNANCE_APPROVED)
            self.stats["governance_approved"] += 1
            lifecycle_context.governance_metadata = governance_result.get("metadata", {})

            # Step 2: Template-based creation (if applicable)
            app_instance = None
            if template_id and self.app_factory:
                app_instance = await self._create_application_instance(
                    lifecycle_context,
                    template_id,
                    instance_config
                )

                if app_instance.get("error"):
                    raise RuntimeError(f"Application instance creation failed: {app_instance['error']}")

            # Step 3: Generate/validate blueprint
            if not blueprint:
                blueprint = await self._generate_blueprint_from_template(
                    lifecycle_context,
                    template_id,
                    app_instance
                )

            # Step 4: Infrastructure provisioning
            await self._transition_stage(lifecycle_context, CapsuleLifecycleStage.INFRASTRUCTURE_PROVISIONING)
            infrastructure_instance = await self._create_infrastructure_instance(
                lifecycle_context,
                blueprint,
                deployment_context
            )

            if infrastructure_instance.get("error"):
                raise RuntimeError(f"Infrastructure creation failed: {infrastructure_instance['error']}")

            await self._transition_stage(lifecycle_context, CapsuleLifecycleStage.INFRASTRUCTURE_READY)
            self.stats["infrastructure_provisioned"] += 1

            # Step 5: Register in unified registry
            await self._register_in_unified_registry(
                lifecycle_context,
                app_instance,
                infrastructure_instance
            )

            # Step 6: Initialize evolution tracking
            if self.evolution_service:
                evolution_metadata = await self._initialize_evolution_tracking(lifecycle_context)
                lifecycle_context.evolution_metadata = evolution_metadata

            # Step 7: Activate capsule
            await self._transition_stage(lifecycle_context, CapsuleLifecycleStage.ACTIVE)
            self.stats["active_capsules"] += 1

            # Step 8: Publish success event
            await self._publish_event("capsule.lifecycle.created", {
                "capsule_id": capsule_id,
                "source": source.value,
                "template_id": template_id,
                "blueprint_id": lifecycle_context.blueprint_id,
                "governance_status": "approved",
                "generation": lifecycle_context.generation,
                "timestamp": time.time()
            })

            logger.info(f"Capsule lifecycle completed successfully: {capsule_id}")

            return {
                "status": "success",
                "capsule_id": capsule_id,
                "lifecycle_context": lifecycle_context,
                "application_instance": app_instance,
                "infrastructure_instance": infrastructure_instance
            }

        except Exception as e:
            logger.error(f"Capsule lifecycle failed: {e}")
            lifecycle_context.errors.append(str(e))
            self.stats["failed_creations"] += 1

            # Publish failure event
            await self._publish_event("capsule.lifecycle.failed", {
                "capsule_id": capsule_id,
                "error": str(e),
                "stage": lifecycle_context.stage.value,
                "timestamp": time.time()
            })

            return {
                "status": "error",
                "capsule_id": capsule_id,
                "error": str(e),
                "lifecycle_context": lifecycle_context
            }

    # ========================================================================
    # Lifecycle Stage Management
    # ========================================================================

    async def _transition_stage(
        self,
        context: CapsuleLifecycleContext,
        new_stage: CapsuleLifecycleStage
    ):
        """
        Transition capsule to new lifecycle stage.

        Args:
            context: Lifecycle context
            new_stage: New stage
        """
        old_stage = context.stage
        context.stage = new_stage
        context.updated_at = time.time()

        logger.info(f"Capsule {context.capsule_id} transitioned: {old_stage.value} → {new_stage.value}")

        # Execute stage callbacks
        for callback in self.lifecycle_callbacks[new_stage]:
            try:
                await callback(context)
            except Exception as e:
                logger.error(f"Lifecycle callback error: {e}")

        # Publish stage transition event
        await self._publish_event("capsule.lifecycle.stage_transition", {
            "capsule_id": context.capsule_id,
            "old_stage": old_stage.value,
            "new_stage": new_stage.value,
            "timestamp": time.time()
        })

    # ========================================================================
    # Governance
    # ========================================================================

    async def _validate_governance(
        self,
        context: CapsuleLifecycleContext
    ) -> Dict[str, Any]:
        """
        Validate capsule against governance policies.

        Args:
            context: Lifecycle context

        Returns:
            Governance validation result
        """
        if not self.governance_service:
            # No governance service - auto-approve
            logger.warning("No governance service registered - auto-approving capsule")
            return {
                "approved": True,
                "reason": "no_governance_service"
            }

        try:
            # TODO: Integrate with actual governance service
            # For now, implement basic validation

            # Check for required metadata
            required_fields = ["name", "description"] if context.template_id else ["metadata"]

            missing_fields = []
            if context.template_id:
                for field in required_fields:
                    if field not in context.instance_config:
                        missing_fields.append(field)
            else:
                # Blueprint-based creation
                pass  # Blueprints have their own validation

            if missing_fields:
                return {
                    "approved": False,
                    "reason": f"missing_required_fields: {missing_fields}"
                }

            # All checks passed
            return {
                "approved": True,
                "metadata": {
                    "validated_at": time.time(),
                    "compliance_frameworks": context.deployment_context.get("compliance_frameworks", []),
                    "trust_zone": context.deployment_context.get("trust_zone", "default")
                }
            }

        except Exception as e:
            logger.error(f"Governance validation error: {e}")
            return {
                "approved": False,
                "reason": f"validation_error: {str(e)}"
            }

    # ========================================================================
    # Application Layer Integration
    # ========================================================================

    async def _create_application_instance(
        self,
        context: CapsuleLifecycleContext,
        template_id: str,
        instance_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create application-level capsule instance.

        Args:
            context: Lifecycle context
            template_id: Template ID
            instance_config: Instance configuration

        Returns:
            Application instance result
        """
        if not self.app_factory:
            raise RuntimeError("Application Layer factory not registered")

        try:
            logger.info(f"Creating application instance from template: {template_id}")

            # Call Application Layer factory directly (not through coordinator to avoid recursion)
            # The create_capsule_instance method is synchronous, so we call it directly
            result = self.app_factory.create_capsule_instance(
                template_id=template_id,
                instance_config=instance_config
            )

            return result

        except Exception as e:
            logger.error(f"Application instance creation error: {e}")
            return {
                "error": str(e)
            }

    # ========================================================================
    # Blueprint Generation
    # ========================================================================

    async def _generate_blueprint_from_template(
        self,
        context: CapsuleLifecycleContext,
        template_id: str,
        app_instance: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate blueprint from template and application instance.

        Args:
            context: Lifecycle context
            template_id: Template ID
            app_instance: Application instance (if created)

        Returns:
            Blueprint dictionary
        """
        try:
            logger.info(f"Generating blueprint from template: {template_id}")

            # Generate blueprint from template
            blueprint = {
                "metadata": {
                    "id": f"blueprint-{str(uuid.uuid4())}",
                    "name": context.instance_config.get("name", f"Capsule from {template_id}"),
                    "template_id": template_id,
                    "generated_at": time.time()
                },
                "type": template_id,
                "version": "1.0.0",
                "config": context.instance_config.copy(),
                "capabilities": app_instance.get("capabilities", []) if app_instance else [],
                "resources": {
                    "cpu": context.instance_config.get("cpu", "1"),
                    "memory": context.instance_config.get("memory", "512Mi"),
                    "storage": context.instance_config.get("storage", "1Gi")
                }
            }

            context.blueprint_id = blueprint["metadata"]["id"]

            return blueprint

        except Exception as e:
            logger.error(f"Blueprint generation error: {e}")
            raise RuntimeError(f"Blueprint generation failed: {e}")

    # ========================================================================
    # Infrastructure Layer Integration
    # ========================================================================

    async def _create_infrastructure_instance(
        self,
        context: CapsuleLifecycleContext,
        blueprint: Dict[str, Any],
        deployment_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create infrastructure-level capsule instance.

        Args:
            context: Lifecycle context
            blueprint: Blueprint dictionary
            deployment_context: Deployment context

        Returns:
            Infrastructure instance result
        """
        if not self.deploy_factory:
            raise RuntimeError("Deployment Operations Layer factory not registered")

        try:
            logger.info(f"Creating infrastructure instance for capsule: {context.capsule_id}")

            # Create deployment manifest from deployment_context
            manifest = {
                "id": f"manifest-{context.capsule_id}",
                "capsule_id": context.capsule_id,
                "scaling": deployment_context.get("scaling", {"min": 1, "max": 1}),
                "environment": deployment_context.get("environment", "default"),
                "permissions": deployment_context.get("permissions", [])
            }

            # Call Deployment Operations Layer factory with governance metadata (Week 18-19 Day 3)
            capsule = self.deploy_factory.create_capsule(
                blueprint=blueprint,
                manifest=manifest,
                context=deployment_context,
                governance_metadata=context.governance_metadata  # NEW: Pass governance metadata
            )

            return capsule

        except Exception as e:
            logger.error(f"Infrastructure instance creation error: {e}")
            return {
                "error": str(e)
            }

    # ========================================================================
    # Registry Integration
    # ========================================================================

    async def _register_in_unified_registry(
        self,
        context: CapsuleLifecycleContext,
        app_instance: Optional[Dict[str, Any]],
        infrastructure_instance: Dict[str, Any]
    ):
        """
        Register capsule in unified registry.

        Args:
            context: Lifecycle context
            app_instance: Application instance (if created)
            infrastructure_instance: Infrastructure instance
        """
        if not self.unified_registry:
            logger.warning("No unified registry - skipping registration")
            return

        try:
            await self.unified_registry.register_capsule(
                capsule_id=context.capsule_id,
                capsule_data={
                    "lifecycle_context": {
                        "source": context.source.value,
                        "stage": context.stage.value,
                        "template_id": context.template_id,
                        "blueprint_id": context.blueprint_id,
                        "parent_capsule_id": context.parent_capsule_id,
                        "generation": context.generation,
                        "created_at": context.created_at,
                        "updated_at": context.updated_at
                    },
                    "governance": context.governance_metadata,
                    "evolution": context.evolution_metadata,
                    "application_instance": app_instance,
                    "infrastructure_instance": infrastructure_instance
                },
                source=context.source.value
            )

            logger.info(f"Capsule registered in unified registry: {context.capsule_id}")

        except Exception as e:
            logger.error(f"Registry registration error: {e}")
            raise

    # ========================================================================
    # Evolution Tracking
    # ========================================================================

    async def _initialize_evolution_tracking(
        self,
        context: CapsuleLifecycleContext
    ) -> Dict[str, Any]:
        """
        Initialize evolution tracking for capsule.

        Args:
            context: Lifecycle context

        Returns:
            Evolution metadata
        """
        if not self.evolution_service:
            logger.warning("No evolution service - skipping evolution tracking")
            return {}

        try:
            # TODO: Integrate with actual evolution service
            evolution_metadata = {
                "generation": context.generation,
                "parent_capsule_id": context.parent_capsule_id,
                "mutation_rate": 0.1,
                "fitness_score": 100,
                "evolution_started_at": time.time()
            }

            logger.info(f"Evolution tracking initialized for capsule: {context.capsule_id}")

            return evolution_metadata

        except Exception as e:
            logger.error(f"Evolution tracking initialization error: {e}")
            return {}

    # ========================================================================
    # Helpers
    # ========================================================================

    async def _get_parent_generation(self, parent_capsule_id: str) -> int:
        """Get generation number of parent capsule."""
        if not self.unified_registry:
            return 0

        try:
            parent_data = await self.unified_registry.get_capsule(parent_capsule_id)
            return parent_data.get("lifecycle_context", {}).get("generation", 0)
        except Exception:
            return 0

    async def _publish_event(self, event_type: str, event_data: Dict[str, Any]):
        """Publish event to event bus."""
        if not self.event_bus:
            return

        try:
            await self.event_bus.publish(event_type, event_data)
        except Exception as e:
            logger.error(f"Event publishing error: {e}")

    # ========================================================================
    # Query Methods
    # ========================================================================

    def get_lifecycle_context(self, capsule_id: str) -> Optional[CapsuleLifecycleContext]:
        """Get lifecycle context for capsule."""
        return self.active_lifecycles.get(capsule_id)

    def get_statistics(self) -> Dict[str, Any]:
        """Get coordinator statistics."""
        return self.stats.copy()

    def get_active_lifecycles(self) -> List[CapsuleLifecycleContext]:
        """Get all active lifecycle contexts."""
        return list(self.active_lifecycles.values())


# ============================================================================
# Singleton instance
# ============================================================================

_coordinator_instance = None

def get_capsule_lifecycle_coordinator(
    event_bus=None,
    database_pool=None
) -> CapsuleLifecycleCoordinator:
    """
    Get singleton Capsule Lifecycle Coordinator instance.

    Args:
        event_bus: Event bus for publishing lifecycle events
        database_pool: Database connection pool

    Returns:
        CapsuleLifecycleCoordinator instance
    """
    global _coordinator_instance

    if _coordinator_instance is None:
        _coordinator_instance = CapsuleLifecycleCoordinator(
            event_bus=event_bus,
            database_pool=database_pool
        )

    return _coordinator_instance
