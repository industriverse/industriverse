"""
Advanced Scenario Orchestrator for the Overseer System.

This module provides advanced scenario orchestration capabilities for strategic simulations,
enabling complex scenario planning, execution, and analysis.
"""

import os
import json
import logging
import asyncio
import datetime
import uuid
import random
from typing import Dict, Any, List, Optional, Union, Tuple, Set
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("advanced_scenario_orchestrator")

class ScenarioTemplate(BaseModel):
    """Scenario template model."""
    template_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    category: str
    industry_vertical: Optional[str] = None
    complexity_level: int = 1  # 1-5 scale
    estimated_duration: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    stages: List[Dict[str, Any]] = Field(default_factory=list)
    required_capabilities: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    version: str = "1.0.0"

class ScenarioInstance(BaseModel):
    """Scenario instance model."""
    instance_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    template_id: str
    name: str
    description: str
    status: str = "created"  # created, configured, running, paused, completed, failed
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    current_stage: int = 0
    stage_results: Dict[int, Dict[str, Any]] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

class ScenarioEvent(BaseModel):
    """Scenario event model."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    instance_id: str
    event_type: str
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    stage: Optional[int] = None
    description: str
    details: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AdvancedScenarioOrchestrator:
    """
    Advanced Scenario Orchestrator.
    
    This service provides advanced scenario orchestration capabilities for strategic simulations,
    enabling complex scenario planning, execution, and analysis.
    """
    
    def __init__(self, event_bus_client=None, mcp_client=None, a2a_client=None, 
                 simulation_service=None, cloning_deck=None):
        """
        Initialize the Advanced Scenario Orchestrator.
        
        Args:
            event_bus_client: Event bus client for publishing and subscribing to events
            mcp_client: MCP client for context-aware communication
            a2a_client: A2A client for agent-based communication
            simulation_service: Strategic Simulation Service instance
            cloning_deck: Sovereign Simulation Cloning Deck instance
        """
        self.event_bus_client = event_bus_client
        self.mcp_client = mcp_client
        self.a2a_client = a2a_client
        self.simulation_service = simulation_service
        self.cloning_deck = cloning_deck
        
        # In-memory storage (would be replaced with database in production)
        self.templates = {}  # template_id -> ScenarioTemplate
        self.instances = {}  # instance_id -> ScenarioInstance
        self.events = {}  # instance_id -> List[ScenarioEvent]
        
        # Active scenario tasks
        self.active_scenarios = {}  # instance_id -> asyncio.Task
        
        # Load built-in templates
        self._load_built_in_templates()
        
    async def initialize(self):
        """Initialize the Advanced Scenario Orchestrator."""
        logger.info("Initializing Advanced Scenario Orchestrator")
        
        # In a real implementation, we would initialize connections to external systems
        # For example:
        # await self.event_bus_client.connect()
        # await self.mcp_client.connect()
        # await self.a2a_client.connect()
        
        # Subscribe to events
        # await self.event_bus_client.subscribe("scenario.request", self._handle_scenario_request)
        
        logger.info("Advanced Scenario Orchestrator initialized")
        
    def _load_built_in_templates(self):
        """Load built-in scenario templates."""
        # Manufacturing vertical templates
        manufacturing_templates = [
            ScenarioTemplate(
                name="Supply Chain Disruption Response",
                description="Simulate response to major supply chain disruptions affecting production",
                category="Resilience Testing",
                industry_vertical="Manufacturing",
                complexity_level=4,
                estimated_duration="2-4 hours",
                parameters={
                    "disruption_severity": 0.8,
                    "affected_suppliers_percentage": 0.4,
                    "alternative_sourcing_availability": 0.6,
                    "inventory_buffer_days": 14
                },
                stages=[
                    {
                        "name": "Initial Disruption",
                        "description": "Simulate initial supply chain disruption event",
                        "duration_minutes": 30,
                        "actions": ["trigger_supplier_outage", "notify_stakeholders"]
                    },
                    {
                        "name": "Response Activation",
                        "description": "Activate emergency response protocols",
                        "duration_minutes": 45,
                        "actions": ["activate_crisis_team", "assess_inventory_levels"]
                    },
                    {
                        "name": "Alternative Sourcing",
                        "description": "Identify and activate alternative suppliers",
                        "duration_minutes": 60,
                        "actions": ["search_supplier_database", "negotiate_emergency_contracts"]
                    },
                    {
                        "name": "Production Adjustment",
                        "description": "Adjust production schedules based on available materials",
                        "duration_minutes": 45,
                        "actions": ["recalculate_production_schedule", "prioritize_critical_products"]
                    },
                    {
                        "name": "Recovery Planning",
                        "description": "Develop recovery plan to return to normal operations",
                        "duration_minutes": 60,
                        "actions": ["develop_recovery_timeline", "allocate_recovery_resources"]
                    }
                ],
                required_capabilities=["supply_chain_management", "crisis_response", "production_planning"],
                tags=["manufacturing", "supply_chain", "crisis", "resilience"]
            ),
            ScenarioTemplate(
                name="Smart Factory Optimization",
                description="Optimize smart factory operations through AI-driven process improvements",
                category="Optimization",
                industry_vertical="Manufacturing",
                complexity_level=3,
                estimated_duration="3-5 hours",
                parameters={
                    "optimization_target": "throughput",  # throughput, quality, energy_efficiency
                    "constraint_priority": "quality",  # quality, cost, time
                    "learning_rate": 0.05,
                    "exploration_factor": 0.2
                },
                stages=[
                    {
                        "name": "Baseline Assessment",
                        "description": "Establish baseline performance metrics",
                        "duration_minutes": 45,
                        "actions": ["collect_baseline_metrics", "identify_bottlenecks"]
                    },
                    {
                        "name": "Parameter Exploration",
                        "description": "Explore parameter space for optimization opportunities",
                        "duration_minutes": 90,
                        "actions": ["generate_parameter_variations", "simulate_variations"]
                    },
                    {
                        "name": "Process Refinement",
                        "description": "Refine processes based on simulation results",
                        "duration_minutes": 60,
                        "actions": ["select_optimal_parameters", "implement_process_changes"]
                    },
                    {
                        "name": "Validation Testing",
                        "description": "Validate optimized processes against requirements",
                        "duration_minutes": 45,
                        "actions": ["run_validation_tests", "compare_to_baseline"]
                    },
                    {
                        "name": "Implementation Planning",
                        "description": "Plan implementation of optimized processes",
                        "duration_minutes": 60,
                        "actions": ["develop_implementation_plan", "estimate_roi"]
                    }
                ],
                required_capabilities=["process_optimization", "machine_learning", "manufacturing_simulation"],
                tags=["manufacturing", "optimization", "smart_factory", "industry_4.0"]
            )
        ]
        
        # Healthcare vertical templates
        healthcare_templates = [
            ScenarioTemplate(
                name="Hospital Resource Allocation Crisis",
                description="Simulate optimal resource allocation during a healthcare crisis",
                category="Crisis Management",
                industry_vertical="Healthcare",
                complexity_level=5,
                estimated_duration="4-6 hours",
                parameters={
                    "crisis_severity": 0.9,
                    "initial_resource_availability": 0.6,
                    "patient_influx_rate": 3.5,
                    "staff_availability": 0.8
                },
                stages=[
                    {
                        "name": "Crisis Onset",
                        "description": "Simulate initial crisis conditions and patient surge",
                        "duration_minutes": 45,
                        "actions": ["trigger_patient_surge", "assess_initial_resources"]
                    },
                    {
                        "name": "Triage Protocol Activation",
                        "description": "Activate and implement triage protocols",
                        "duration_minutes": 60,
                        "actions": ["implement_triage_system", "prioritize_critical_cases"]
                    },
                    {
                        "name": "Resource Optimization",
                        "description": "Optimize allocation of limited resources",
                        "duration_minutes": 90,
                        "actions": ["reallocate_staff", "optimize_bed_utilization", "manage_equipment_usage"]
                    },
                    {
                        "name": "External Resource Acquisition",
                        "description": "Secure additional resources from external sources",
                        "duration_minutes": 60,
                        "actions": ["request_emergency_supplies", "coordinate_with_other_facilities"]
                    },
                    {
                        "name": "Stabilization Planning",
                        "description": "Develop plan for stabilizing operations",
                        "duration_minutes": 45,
                        "actions": ["forecast_resource_needs", "develop_staffing_plan"]
                    }
                ],
                required_capabilities=["healthcare_operations", "crisis_management", "resource_allocation"],
                tags=["healthcare", "crisis", "resource_management", "triage"]
            )
        ]
        
        # Energy vertical templates
        energy_templates = [
            ScenarioTemplate(
                name="Grid Resilience Under Extreme Conditions",
                description="Test energy grid resilience under extreme weather or demand conditions",
                category="Resilience Testing",
                industry_vertical="Energy",
                complexity_level=4,
                estimated_duration="3-5 hours",
                parameters={
                    "weather_severity": 0.85,
                    "demand_spike_factor": 1.7,
                    "renewable_availability_factor": 0.3,
                    "infrastructure_vulnerability": 0.6
                },
                stages=[
                    {
                        "name": "Condition Onset",
                        "description": "Simulate onset of extreme conditions",
                        "duration_minutes": 30,
                        "actions": ["simulate_weather_event", "trigger_demand_spike"]
                    },
                    {
                        "name": "Initial Response",
                        "description": "Implement initial response measures",
                        "duration_minutes": 45,
                        "actions": ["activate_emergency_protocols", "assess_grid_stability"]
                    },
                    {
                        "name": "Load Management",
                        "description": "Manage load to maintain grid stability",
                        "duration_minutes": 60,
                        "actions": ["implement_load_shedding", "activate_demand_response"]
                    },
                    {
                        "name": "Alternative Generation",
                        "description": "Activate alternative generation sources",
                        "duration_minutes": 45,
                        "actions": ["start_backup_generators", "optimize_available_renewables"]
                    },
                    {
                        "name": "Recovery Operations",
                        "description": "Restore normal grid operations",
                        "duration_minutes": 60,
                        "actions": ["repair_damaged_infrastructure", "normalize_generation_mix"]
                    }
                ],
                required_capabilities=["grid_management", "emergency_response", "load_forecasting"],
                tags=["energy", "grid", "resilience", "extreme_events"]
            )
        ]
        
        # Logistics vertical templates
        logistics_templates = [
            ScenarioTemplate(
                name="Last-Mile Delivery Optimization",
                description="Optimize last-mile delivery operations for efficiency and customer satisfaction",
                category="Optimization",
                industry_vertical="Logistics",
                complexity_level=3,
                estimated_duration="2-4 hours",
                parameters={
                    "delivery_volume": 500,
                    "geographic_density": 0.7,
                    "time_window_constraints": 0.6,
                    "vehicle_capacity_utilization_target": 0.85
                },
                stages=[
                    {
                        "name": "Demand Analysis",
                        "description": "Analyze delivery demand patterns",
                        "duration_minutes": 30,
                        "actions": ["analyze_order_data", "identify_delivery_clusters"]
                    },
                    {
                        "name": "Route Optimization",
                        "description": "Optimize delivery routes",
                        "duration_minutes": 60,
                        "actions": ["generate_route_alternatives", "evaluate_route_efficiency"]
                    },
                    {
                        "name": "Resource Allocation",
                        "description": "Allocate vehicles and personnel",
                        "duration_minutes": 45,
                        "actions": ["match_vehicles_to_routes", "assign_delivery_personnel"]
                    },
                    {
                        "name": "Schedule Optimization",
                        "description": "Optimize delivery schedules",
                        "duration_minutes": 45,
                        "actions": ["optimize_time_windows", "balance_workloads"]
                    },
                    {
                        "name": "Performance Evaluation",
                        "description": "Evaluate optimized delivery operations",
                        "duration_minutes": 30,
                        "actions": ["calculate_key_metrics", "identify_improvement_areas"]
                    }
                ],
                required_capabilities=["route_optimization", "logistics_planning", "demand_forecasting"],
                tags=["logistics", "delivery", "optimization", "routing"]
            )
        ]
        
        # Add all templates to the store
        for template in manufacturing_templates + healthcare_templates + energy_templates + logistics_templates:
            self.templates[template.template_id] = template
            
    async def create_template(self, name: str, description: str, category: str,
                             industry_vertical: Optional[str], complexity_level: int,
                             estimated_duration: str, parameters: Dict[str, Any],
                             stages: List[Dict[str, Any]], required_capabilities: List[str],
                             tags: List[str], metadata: Optional[Dict[str, Any]] = None) -> ScenarioTemplate:
        """
        Create a scenario template.
        
        Args:
            name: Name of the template
            description: Description of the template
            category: Category of the template
            industry_vertical: Optional industry vertical
            complexity_level: Complexity level (1-5)
            estimated_duration: Estimated duration (e.g., "2-4 hours")
            parameters: Template parameters
            stages: Template stages
            required_capabilities: Required capabilities
            tags: Template tags
            metadata: Optional metadata
            
        Returns:
            Created scenario template
        """
        logger.info(f"Creating scenario template: {name}")
        
        # Create template
        template = ScenarioTemplate(
            name=name,
            description=description,
            category=category,
            industry_vertical=industry_vertical,
            complexity_level=complexity_level,
            estimated_duration=estimated_duration,
            parameters=parameters,
            stages=stages,
            required_capabilities=required_capabilities,
            tags=tags,
            metadata=metadata or {}
        )
        
        # Store template
        self.templates[template.template_id] = template
        
        # In a real implementation, we would publish the creation
        # For example:
        # await self.event_bus_client.publish("scenario.template.created", template.dict())
        
        logger.info(f"Created scenario template {template.template_id}: {name}")
        
        return template
        
    async def get_template(self, template_id: str) -> Optional[ScenarioTemplate]:
        """
        Get a scenario template by ID.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Scenario template, or None if not found
        """
        return self.templates.get(template_id)
        
    async def list_templates(self, category: Optional[str] = None,
                            industry_vertical: Optional[str] = None,
                            tags: Optional[List[str]] = None,
                            complexity_level: Optional[int] = None) -> List[ScenarioTemplate]:
        """
        List scenario templates.
        
        Args:
            category: Optional category filter
            industry_vertical: Optional industry vertical filter
            tags: Optional tags filter
            complexity_level: Optional complexity level filter
            
        Returns:
            List of scenario templates
        """
        templates = list(self.templates.values())
        
        # Apply filters
        if category:
            templates = [t for t in templates if t.category == category]
            
        if industry_vertical:
            templates = [t for t in templates if t.industry_vertical == industry_vertical]
            
        if tags:
            templates = [t for t in templates if any(tag in t.tags for tag in tags)]
            
        if complexity_level:
            templates = [t for t in templates if t.complexity_level == complexity_level]
            
        return templates
        
    async def update_template(self, template_id: str, updates: Dict[str, Any]) -> Optional[ScenarioTemplate]:
        """
        Update a scenario template.
        
        Args:
            template_id: ID of the template
            updates: Updates to apply
            
        Returns:
            Updated scenario template, or None if not found
        """
        if template_id not in self.templates:
            logger.warning(f"Scenario template {template_id} not found")
            return None
            
        template = self.templates[template_id]
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(template, key):
                setattr(template, key, value)
                
        # Update timestamp
        template.updated_at = datetime.datetime.now()
        
        # In a real implementation, we would publish the update
        # For example:
        # await self.event_bus_client.publish("scenario.template.updated", template.dict())
        
        logger.info(f"Updated scenario template {template_id}")
        
        return template
        
    async def delete_template(self, template_id: str) -> bool:
        """
        Delete a scenario template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            True if deleted, False if not found
        """
        if template_id not in self.templates:
            logger.warning(f"Scenario template {template_id} not found")
            return False
            
        # Delete template
        del self.templates[template_id]
        
        # In a real implementation, we would publish the deletion
        # For example:
        # await self.event_bus_client.publish("scenario.template.deleted", {"template_id": template_id})
        
        logger.info(f"Deleted scenario template {template_id}")
        
        return True
        
    async def create_instance(self, template_id: str, name: str, description: str,
                             parameters: Optional[Dict[str, Any]] = None,
                             tags: Optional[List[str]] = None,
                             metadata: Optional[Dict[str, Any]] = None) -> Optional[ScenarioInstance]:
        """
        Create a scenario instance from a template.
        
        Args:
            template_id: ID of the template
            name: Name of the instance
            description: Description of the instance
            parameters: Optional parameters (overrides template defaults)
            tags: Optional tags
            metadata: Optional metadata
            
        Returns:
            Created scenario instance, or None if template not found
        """
        if template_id not in self.templates:
            logger.warning(f"Scenario template {template_id} not found")
            return None
            
        template = self.templates[template_id]
        
        logger.info(f"Creating scenario instance from template {template_id}: {name}")
        
        # Merge parameters with template defaults
        merged_parameters = template.parameters.copy()
        if parameters:
            merged_parameters.update(parameters)
            
        # Create instance
        instance = ScenarioInstance(
            template_id=template_id,
            name=name,
            description=description,
            parameters=merged_parameters,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # Store instance
        self.instances[instance.instance_id] = instance
        self.events[instance.instance_id] = []
        
        # Record creation event
        await self._record_event(
            instance_id=instance.instance_id,
            event_type="created",
            description=f"Created scenario instance: {name}",
            details={"template_id": template_id}
        )
        
        # In a real implementation, we would publish the creation
        # For example:
        # await self.event_bus_client.publish("scenario.instance.created", instance.dict())
        
        logger.info(f"Created scenario instance {instance.instance_id}: {name}")
        
        return instance
        
    async def get_instance(self, instance_id: str) -> Optional[ScenarioInstance]:
        """
        Get a scenario instance by ID.
        
        Args:
            instance_id: ID of the instance
            
        Returns:
            Scenario instance, or None if not found
        """
        return self.instances.get(instance_id)
        
    async def list_instances(self, template_id: Optional[str] = None,
                            status: Optional[str] = None,
                            tags: Optional[List[str]] = None) -> List[ScenarioInstance]:
        """
        List scenario instances.
        
        Args:
            template_id: Optional template ID filter
            status: Optional status filter
            tags: Optional tags filter
            
        Returns:
            List of scenario instances
        """
        instances = list(self.instances.values())
        
        # Apply filters
        if template_id:
            instances = [i for i in instances if i.template_id == template_id]
            
        if status:
            instances = [i for i in instances if i.status == status]
            
        if tags:
            instances = [i for i in instances if any(tag in i.tags for tag in tags)]
            
        return instances
        
    async def start_scenario(self, instance_id: str) -> bool:
        """
        Start a scenario instance.
        
        Args:
            instance_id: ID of the instance
            
        Returns:
            True if started, False if not found or already running
        """
        if instance_id not in self.instances:
            logger.warning(f"Scenario instance {instance_id} not found")
            return False
            
        instance = self.instances[instance_id]
        
        if instance.status not in ["created", "configured"]:
            logger.warning(f"Scenario instance {instance_id} is not in a startable state (status: {instance.status})")
            return False
            
        logger.info(f"Starting scenario instance {instance_id}: {instance.name}")
        
        # Update instance
        instance.status = "running"
        instance.start_time = datetime.datetime.now()
        instance.updated_at = datetime.datetime.now()
        
        # Record start event
        await self._record_event(
            instance_id=instance_id,
            event_type="started",
            description=f"Started scenario instance: {instance.name}"
        )
        
        # Start scenario task
        self.active_scenarios[instance_id] = asyncio.create_task(
            self._run_scenario_task(instance_id)
        )
        
        # In a real implementation, we would publish the start
        # For example:
        # await self.event_bus_client.publish("scenario.instance.started", {"instance_id": instance_id})
        
        logger.info(f"Started scenario instance {instance_id}")
        
        return True
        
    async def pause_scenario(self, instance_id: str) -> bool:
        """
        Pause a running scenario instance.
        
        Args:
            instance_id: ID of the instance
            
        Returns:
            True if paused, False if not found or not running
        """
        if instance_id not in self.instances:
            logger.warning(f"Scenario instance {instance_id} not found")
            return False
            
        instance = self.instances[instance_id]
        
        if instance.status != "running":
            logger.warning(f"Scenario instance {instance_id} is not running (status: {instance.status})")
            return False
            
        # Update instance
        instance.status = "paused"
        instance.updated_at = datetime.datetime.now()
        
        # Record pause event
        await self._record_event(
            instance_id=instance_id,
            event_type="paused",
            description=f"Paused scenario instance: {instance.name}"
        )
        
        # In a real implementation, we would publish the pause
        # For example:
        # await self.event_bus_client.publish("scenario.instance.paused", {"instance_id": instance_id})
        
        logger.info(f"Paused scenario instance {instance_id}")
        
        return True
        
    async def resume_scenario(self, instance_id: str) -> bool:
        """
        Resume a paused scenario instance.
        
        Args:
            instance_id: ID of the instance
            
        Returns:
            True if resumed, False if not found or not paused
        """
        if instance_id not in self.instances:
            logger.warning(f"Scenario instance {instance_id} not found")
            return False
            
        instance = self.instances[instance_id]
        
        if instance.status != "paused":
            logger.warning(f"Scenario instance {instance_id} is not paused (status: {instance.status})")
            return False
            
        # Update instance
        instance.status = "running"
        instance.updated_at = datetime.datetime.now()
        
        # Record resume event
        await self._record_event(
            instance_id=instance_id,
            event_type="resumed",
            description=f"Resumed scenario instance: {instance.name}"
        )
        
        # In a real implementation, we would publish the resume
        # For example:
        # await self.event_bus_client.publish("scenario.instance.resumed", {"instance_id": instance_id})
        
        logger.info(f"Resumed scenario instance {instance_id}")
        
        return True
        
    async def stop_scenario(self, instance_id: str, reason: str) -> bool:
        """
        Stop a scenario instance.
        
        Args:
            instance_id: ID of the instance
            reason: Reason for stopping
            
        Returns:
            True if stopped, False if not found
        """
        if instance_id not in self.instances:
            logger.warning(f"Scenario instance {instance_id} not found")
            return False
            
        instance = self.instances[instance_id]
        
        if instance.status not in ["running", "paused"]:
            logger.warning(f"Scenario instance {instance_id} is not running or paused (status: {instance.status})")
            return False
            
        # Update instance
        instance.status = "completed"
        instance.end_time = datetime.datetime.now()
        instance.updated_at = datetime.datetime.now()
        
        # Cancel task if active
        if instance_id in self.active_scenarios:
            task = self.active_scenarios[instance_id]
            task.cancel()
            del self.active_scenarios[instance_id]
            
        # Record stop event
        await self._record_event(
            instance_id=instance_id,
            event_type="stopped",
            description=f"Stopped scenario instance: {instance.name}",
            details={"reason": reason}
        )
        
        # In a real implementation, we would publish the stop
        # For example:
        # await self.event_bus_client.publish("scenario.instance.stopped", {
        #     "instance_id": instance_id,
        #     "reason": reason
        # })
        
        logger.info(f"Stopped scenario instance {instance_id}: {reason}")
        
        return True
        
    async def get_instance_events(self, instance_id: str) -> List[ScenarioEvent]:
        """
        Get all events for a scenario instance.
        
        Args:
            instance_id: ID of the instance
            
        Returns:
            List of scenario events
        """
        if instance_id not in self.events:
            return []
            
        return self.events[instance_id]
        
    async def get_instance_metrics(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metrics for a scenario instance.
        
        Args:
            instance_id: ID of the instance
            
        Returns:
            Metrics, or None if instance not found
        """
        if instance_id not in self.instances:
            logger.warning(f"Scenario instance {instance_id} not found")
            return None
            
        instance = self.instances[instance_id]
        
        return instance.metrics
        
    async def get_stage_results(self, instance_id: str, stage: int) -> Optional[Dict[str, Any]]:
        """
        Get results for a specific stage of a scenario instance.
        
        Args:
            instance_id: ID of the instance
            stage: Stage number
            
        Returns:
            Stage results, or None if instance not found or stage not completed
        """
        if instance_id not in self.instances:
            logger.warning(f"Scenario instance {instance_id} not found")
            return None
            
        instance = self.instances[instance_id]
        
        if stage not in instance.stage_results:
            logger.warning(f"Stage {stage} results not found for instance {instance_id}")
            return None
            
        return instance.stage_results[stage]
        
    async def create_parallel_scenarios(self, template_id: str, base_name: str,
                                      parameter_variations: List[Dict[str, Any]],
                                      common_parameters: Optional[Dict[str, Any]] = None,
                                      tags: Optional[List[str]] = None,
                                      metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a set of parallel scenario instances with parameter variations.
        
        Args:
            template_id: ID of the template
            base_name: Base name for the scenario set
            parameter_variations: List of parameter variation specifications
            common_parameters: Optional parameters common to all instances
            tags: Optional tags
            metadata: Optional metadata
            
        Returns:
            Parallel scenario set information
        """
        if template_id not in self.templates:
            logger.warning(f"Scenario template {template_id} not found")
            raise ValueError(f"Scenario template {template_id} not found")
            
        logger.info(f"Creating parallel scenario set: {base_name}")
        
        # Create instances for each variation
        instances = []
        for i, variation in enumerate(parameter_variations):
            variation_name = variation.get("name", f"Variation {i+1}")
            
            # Merge parameters
            merged_parameters = {}
            if common_parameters:
                merged_parameters.update(common_parameters)
            if "parameters" in variation:
                merged_parameters.update(variation["parameters"])
                
            # Create instance
            instance = await self.create_instance(
                template_id=template_id,
                name=f"{base_name}: {variation_name}",
                description=f"Parallel scenario instance with variation: {variation_name}",
                parameters=merged_parameters,
                tags=(tags or []) + ["parallel_set"],
                metadata={
                    "parallel_set_id": str(uuid.uuid4()),  # Same for all instances in the set
                    "variation_index": i,
                    "variation_name": variation_name,
                    **(metadata or {})
                }
            )
            instances.append(instance)
            
        # Create parallel set info
        parallel_set = {
            "id": instances[0].metadata["parallel_set_id"],
            "name": base_name,
            "template_id": template_id,
            "creation_time": datetime.datetime.now().isoformat(),
            "instance_count": len(instances),
            "instance_ids": [i.instance_id for i in instances],
            "parameter_variations": parameter_variations,
            "common_parameters": common_parameters or {},
            "tags": tags or [],
            "metadata": metadata or {}
        }
        
        # In a real implementation, we would publish the parallel set creation
        # For example:
        # await self.event_bus_client.publish("scenario.parallel_set.created", parallel_set)
        
        logger.info(f"Created parallel scenario set with {len(instances)} instances")
        
        return parallel_set
        
    async def compare_scenario_results(self, instance_ids: List[str]) -> Dict[str, Any]:
        """
        Compare results from multiple scenario instances.
        
        Args:
            instance_ids: List of instance IDs to compare
            
        Returns:
            Comparison results
        """
        # Validate instances
        instances = []
        for instance_id in instance_ids:
            if instance_id not in self.instances:
                logger.warning(f"Scenario instance {instance_id} not found")
                raise ValueError(f"Scenario instance {instance_id} not found")
                
            instance = self.instances[instance_id]
            if instance.status != "completed":
                logger.warning(f"Scenario instance {instance_id} is not completed (status: {instance.status})")
                raise ValueError(f"Scenario instance {instance_id} is not completed")
                
            instances.append(instance)
            
        logger.info(f"Comparing results from {len(instances)} scenario instances")
        
        # In a real implementation, we would perform the actual comparison
        # For example:
        # comparison = await self.mcp_client.compare_scenario_results(instance_ids)
        
        # For simulation, we'll create a dummy comparison result
        comparison = {
            "timestamp": datetime.datetime.now().isoformat(),
            "instance_count": len(instances),
            "instances": [
                {
                    "id": instance.instance_id,
                    "name": instance.name,
                    "template_id": instance.template_id
                }
                for instance in instances
            ],
            "metrics_comparison": {
                "performance": {
                    "throughput": {
                        "min": random.uniform(100, 500),
                        "max": random.uniform(500, 1000),
                        "avg": random.uniform(300, 800),
                        "std_dev": random.uniform(50, 150)
                    },
                    "latency": {
                        "min": random.uniform(1, 20),
                        "max": random.uniform(20, 100),
                        "avg": random.uniform(10, 50),
                        "std_dev": random.uniform(5, 15)
                    },
                    "error_rate": {
                        "min": random.uniform(0, 0.02),
                        "max": random.uniform(0.02, 0.05),
                        "avg": random.uniform(0.01, 0.03),
                        "std_dev": random.uniform(0.005, 0.01)
                    }
                },
                "business": {
                    "value_generated": {
                        "min": random.uniform(1000, 5000),
                        "max": random.uniform(5000, 10000),
                        "avg": random.uniform(3000, 7000),
                        "std_dev": random.uniform(500, 1500)
                    },
                    "cost_incurred": {
                        "min": random.uniform(500, 2000),
                        "max": random.uniform(2000, 5000),
                        "avg": random.uniform(1000, 3000),
                        "std_dev": random.uniform(300, 800)
                    },
                    "efficiency": {
                        "min": random.uniform(0.7, 0.8),
                        "max": random.uniform(0.8, 0.95),
                        "avg": random.uniform(0.75, 0.9),
                        "std_dev": random.uniform(0.05, 0.1)
                    }
                }
            },
            "parameter_impact": {
                "sensitivity": {
                    "param1": random.uniform(0.1, 0.9),
                    "param2": random.uniform(0.1, 0.9),
                    "param3": random.uniform(0.1, 0.9)
                },
                "correlations": {
                    "param1_vs_throughput": random.uniform(-1, 1),
                    "param2_vs_latency": random.uniform(-1, 1),
                    "param3_vs_efficiency": random.uniform(-1, 1)
                }
            },
            "optimal_configuration": {
                "instance_id": random.choice(instance_ids),
                "parameters": {
                    "param1": random.uniform(0, 1),
                    "param2": random.uniform(0, 1),
                    "param3": random.uniform(0, 1)
                },
                "confidence": random.uniform(0.7, 0.95)
            }
        }
        
        logger.info(f"Completed comparison of {len(instances)} scenario instances")
        
        return comparison
        
    async def export_scenario_results(self, instance_id: str, format: str = "json") -> Dict[str, Any]:
        """
        Export results from a scenario instance.
        
        Args:
            instance_id: ID of the instance
            format: Export format (json, csv, html)
            
        Returns:
            Export result
        """
        if instance_id not in self.instances:
            logger.warning(f"Scenario instance {instance_id} not found")
            raise ValueError(f"Scenario instance {instance_id} not found")
            
        instance = self.instances[instance_id]
        
        if instance.status != "completed":
            logger.warning(f"Scenario instance {instance_id} is not completed (status: {instance.status})")
            raise ValueError(f"Scenario instance {instance_id} is not completed")
            
        logger.info(f"Exporting results from scenario instance {instance_id} in {format} format")
        
        # In a real implementation, we would perform the actual export
        # For example:
        # export_result = await self.mcp_client.export_scenario_results(instance_id, format)
        
        # For simulation, we'll create a dummy export result
        export_result = {
            "instance_id": instance_id,
            "format": format,
            "timestamp": datetime.datetime.now().isoformat(),
            "file_size": random.randint(10000, 1000000),
            "content_type": {
                "json": "application/json",
                "csv": "text/csv",
                "html": "text/html"
            }.get(format, "application/octet-stream"),
            "download_url": f"https://example.com/exports/{instance_id}.{format}",
            "expiration": (datetime.datetime.now() + datetime.timedelta(days=7)).isoformat()
        }
        
        logger.info(f"Exported results from scenario instance {instance_id} in {format} format")
        
        return export_result
        
    async def _record_event(self, instance_id: str, event_type: str, 
                          description: str, stage: Optional[int] = None,
                          details: Optional[Dict[str, Any]] = None) -> ScenarioEvent:
        """
        Record a scenario event.
        
        Args:
            instance_id: ID of the instance
            event_type: Type of event
            description: Description of the event
            stage: Optional stage number
            details: Optional details
            
        Returns:
            Created scenario event
        """
        # Create event
        event = ScenarioEvent(
            instance_id=instance_id,
            event_type=event_type,
            stage=stage,
            description=description,
            details=details or {}
        )
        
        # Store event
        if instance_id not in self.events:
            self.events[instance_id] = []
        self.events[instance_id].append(event)
        
        return event
        
    async def _run_scenario_task(self, instance_id: str):
        """
        Background task for running a scenario instance.
        
        Args:
            instance_id: ID of the instance
        """
        try:
            if instance_id not in self.instances:
                logger.error(f"Scenario instance {instance_id} not found")
                return
                
            instance = self.instances[instance_id]
            template_id = instance.template_id
            
            if template_id not in self.templates:
                logger.error(f"Scenario template {template_id} not found")
                return
                
            template = self.templates[template_id]
            
            logger.info(f"Running scenario instance {instance_id}: {instance.name}")
            
            # Process each stage
            for stage_index, stage in enumerate(template.stages):
                # Check if instance is still running
                instance = self.instances[instance_id]
                if instance.status != "running":
                    logger.info(f"Scenario instance {instance_id} is not running (status: {instance.status})")
                    break
                    
                # Update current stage
                instance.current_stage = stage_index
                instance.updated_at = datetime.datetime.now()
                
                stage_name = stage["name"]
                stage_description = stage["description"]
                stage_duration = stage.get("duration_minutes", 30)
                stage_actions = stage.get("actions", [])
                
                logger.info(f"Starting stage {stage_index}: {stage_name}")
                
                # Record stage start event
                await self._record_event(
                    instance_id=instance_id,
                    event_type="stage_started",
                    stage=stage_index,
                    description=f"Started stage {stage_index}: {stage_name}",
                    details={"stage_description": stage_description}
                )
                
                # In a real implementation, we would execute the actual stage actions
                # For example:
                # for action in stage_actions:
                #     await self.mcp_client.execute_scenario_action(instance_id, action)
                
                # Simulate stage execution
                stage_start_time = datetime.datetime.now()
                
                # Simulate actions
                for action_index, action in enumerate(stage_actions):
                    # Check if instance is still running
                    instance = self.instances[instance_id]
                    if instance.status != "running":
                        logger.info(f"Scenario instance {instance_id} is not running (status: {instance.status})")
                        break
                        
                    logger.info(f"Executing action {action_index}: {action}")
                    
                    # Record action event
                    await self._record_event(
                        instance_id=instance_id,
                        event_type="action_executed",
                        stage=stage_index,
                        description=f"Executed action: {action}",
                        details={"stage_name": stage_name, "action_index": action_index}
                    )
                    
                    # Simulate action execution
                    await asyncio.sleep(random.uniform(1, 3))
                    
                # Simulate stage completion
                elapsed_seconds = (datetime.datetime.now() - stage_start_time).total_seconds()
                remaining_seconds = max(0, stage_duration * 60 - elapsed_seconds)
                
                if remaining_seconds > 0:
                    await asyncio.sleep(remaining_seconds)
                    
                # Generate stage results
                stage_results = {
                    "stage_index": stage_index,
                    "stage_name": stage_name,
                    "start_time": stage_start_time.isoformat(),
                    "end_time": datetime.datetime.now().isoformat(),
                    "duration_seconds": (datetime.datetime.now() - stage_start_time).total_seconds(),
                    "actions_executed": len(stage_actions),
                    "metrics": {
                        "performance": {
                            "throughput": random.uniform(100, 1000),
                            "latency": random.uniform(1, 100),
                            "error_rate": random.uniform(0, 0.05)
                        },
                        "resources": {
                            "cpu_usage": random.uniform(10, 90),
                            "memory_usage": random.uniform(20, 80),
                            "storage_usage": random.uniform(30, 70),
                            "network_bandwidth": random.uniform(5, 50)
                        },
                        "business": {
                            "value_generated": random.uniform(1000, 10000),
                            "cost_incurred": random.uniform(500, 5000),
                            "efficiency": random.uniform(0.7, 0.95)
                        }
                    },
                    "outcomes": {
                        "success": random.random() > 0.1,  # 90% success rate
                        "quality_score": random.uniform(0.7, 1.0),
                        "insights": [
                            f"Insight {i+1} for stage {stage_index}"
                            for i in range(random.randint(1, 3))
                        ]
                    }
                }
                
                # Store stage results
                instance.stage_results[stage_index] = stage_results
                
                # Record stage completion event
                await self._record_event(
                    instance_id=instance_id,
                    event_type="stage_completed",
                    stage=stage_index,
                    description=f"Completed stage {stage_index}: {stage_name}",
                    details={"results_summary": {
                        "duration_seconds": stage_results["duration_seconds"],
                        "success": stage_results["outcomes"]["success"],
                        "quality_score": stage_results["outcomes"]["quality_score"]
                    }}
                )
                
                logger.info(f"Completed stage {stage_index}: {stage_name}")
                
            # All stages completed
            instance = self.instances[instance_id]
            
            # Only update if still running
            if instance.status == "running":
                # Compile overall metrics
                overall_metrics = {
                    "performance": {
                        "avg_throughput": sum(s["metrics"]["performance"]["throughput"] for s in instance.stage_results.values()) / len(instance.stage_results),
                        "avg_latency": sum(s["metrics"]["performance"]["latency"] for s in instance.stage_results.values()) / len(instance.stage_results),
                        "avg_error_rate": sum(s["metrics"]["performance"]["error_rate"] for s in instance.stage_results.values()) / len(instance.stage_results)
                    },
                    "resources": {
                        "avg_cpu_usage": sum(s["metrics"]["resources"]["cpu_usage"] for s in instance.stage_results.values()) / len(instance.stage_results),
                        "avg_memory_usage": sum(s["metrics"]["resources"]["memory_usage"] for s in instance.stage_results.values()) / len(instance.stage_results),
                        "avg_storage_usage": sum(s["metrics"]["resources"]["storage_usage"] for s in instance.stage_results.values()) / len(instance.stage_results),
                        "avg_network_bandwidth": sum(s["metrics"]["resources"]["network_bandwidth"] for s in instance.stage_results.values()) / len(instance.stage_results)
                    },
                    "business": {
                        "total_value_generated": sum(s["metrics"]["business"]["value_generated"] for s in instance.stage_results.values()),
                        "total_cost_incurred": sum(s["metrics"]["business"]["cost_incurred"] for s in instance.stage_results.values()),
                        "overall_efficiency": sum(s["metrics"]["business"]["efficiency"] for s in instance.stage_results.values()) / len(instance.stage_results)
                    },
                    "outcomes": {
                        "success_rate": sum(1 if s["outcomes"]["success"] else 0 for s in instance.stage_results.values()) / len(instance.stage_results),
                        "avg_quality_score": sum(s["outcomes"]["quality_score"] for s in instance.stage_results.values()) / len(instance.stage_results),
                        "key_insights": [
                            insight
                            for s in instance.stage_results.values()
                            for insight in s["outcomes"]["insights"]
                        ][:5]  # Top 5 insights
                    }
                }
                
                # Update instance
                instance.status = "completed"
                instance.end_time = datetime.datetime.now()
                instance.updated_at = datetime.datetime.now()
                instance.metrics = overall_metrics
                
                # Record completion event
                await self._record_event(
                    instance_id=instance_id,
                    event_type="completed",
                    description=f"Completed scenario instance: {instance.name}",
                    details={"metrics_summary": {
                        "success_rate": overall_metrics["outcomes"]["success_rate"],
                        "avg_quality_score": overall_metrics["outcomes"]["avg_quality_score"],
                        "total_value_generated": overall_metrics["business"]["total_value_generated"],
                        "total_cost_incurred": overall_metrics["business"]["total_cost_incurred"],
                        "overall_efficiency": overall_metrics["business"]["overall_efficiency"]
                    }}
                )
                
                # In a real implementation, we would publish the completion
                # For example:
                # await self.event_bus_client.publish("scenario.instance.completed", {
                #     "instance_id": instance_id,
                #     "metrics_summary": overall_metrics
                # })
                
                logger.info(f"Completed scenario instance {instance_id}: {instance.name}")
                
        except asyncio.CancelledError:
            logger.info(f"Scenario task for {instance_id} was cancelled")
            raise
            
        except Exception as e:
            logger.error(f"Error in scenario task for {instance_id}: {e}")
            
            # Update instance status
            if instance_id in self.instances:
                instance = self.instances[instance_id]
                instance.status = "failed"
                instance.end_time = datetime.datetime.now()
                instance.updated_at = datetime.datetime.now()
                
                # Record error event
                await self._record_event(
                    instance_id=instance_id,
                    event_type="failed",
                    description=f"Scenario failed: {str(e)}"
                )
                
                # In a real implementation, we would publish the failure
                # For example:
                # await self.event_bus_client.publish("scenario.instance.failed", {
                #     "instance_id": instance_id,
                #     "error": str(e)
                # })
                
        finally:
            # Clean up
            if instance_id in self.active_scenarios:
                del self.active_scenarios[instance_id]
                
    async def _handle_scenario_request(self, event):
        """
        Handle scenario request event.
        
        Args:
            event: Scenario request event
        """
        request_type = event.get("request_type")
        
        if request_type == "create_instance":
            template_id = event.get("template_id")
            name = event.get("name")
            description = event.get("description")
            
            if template_id and name and description:
                try:
                    await self.create_instance(
                        template_id=template_id,
                        name=name,
                        description=description,
                        parameters=event.get("parameters"),
                        tags=event.get("tags"),
                        metadata=event.get("metadata")
                    )
                except Exception as e:
                    logger.error(f"Error handling scenario request: {e}")
            else:
                logger.warning("Scenario request missing required fields")
                
        elif request_type == "start":
            instance_id = event.get("instance_id")
            
            if instance_id:
                await self.start_scenario(instance_id)
            else:
                logger.warning("Start request missing instance_id")
                
        elif request_type == "stop":
            instance_id = event.get("instance_id")
            reason = event.get("reason", "Requested stop")
            
            if instance_id:
                await self.stop_scenario(instance_id, reason)
            else:
                logger.warning("Stop request missing instance_id")
