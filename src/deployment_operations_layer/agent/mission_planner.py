"""
Mission Planner for the Deployment Operations Layer.

This module provides mission planning capabilities for orchestrating deployments
across the Industriverse ecosystem.
"""

import os
import json
import logging
import requests
import time
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MissionPlanner:
    """
    Planner for deployment missions.
    
    This class provides methods for planning deployment missions, including
    resource allocation, dependency resolution, and execution sequencing.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Mission Planner.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.planner_id = config.get("planner_id", f"planner-{uuid.uuid4().hex[:8]}")
        self.endpoint = config.get("endpoint", "http://localhost:9001")
        self.auth_token = config.get("auth_token", "")
        self.timeout = config.get("timeout", 30)
        self.retry_attempts = config.get("retry_attempts", 3)
        
        # Initialize planning configuration
        self.planning_strategies = config.get("planning_strategies", ["sequential", "parallel", "hybrid"])
        self.default_strategy = config.get("default_strategy", "hybrid")
        self.simulation_enabled = config.get("simulation_enabled", True)
        self.optimization_enabled = config.get("optimization_enabled", True)
        
        # Initialize template manager
        from ..templates.template_manager import TemplateManager
        self.template_manager = TemplateManager(config.get("template_manager", {}))
        
        # Initialize simulation engine
        from ..simulation.simulation_engine import SimulationEngine
        self.simulation_engine = SimulationEngine(config.get("simulation_engine", {}))
        
        logger.info(f"Mission Planner {self.planner_id} initialized")
    
    def plan_mission(self, deployment_request: Dict) -> Dict:
        """
        Plan a deployment mission.
        
        Args:
            deployment_request: Deployment request
            
        Returns:
            Dict: Mission plan
        """
        try:
            # Validate request
            validation_result = self._validate_request(deployment_request)
            if validation_result.get("status") != "success":
                return validation_result
            
            # Extract mission parameters
            mission_name = deployment_request.get("name", f"mission-{int(time.time())}")
            mission_id = deployment_request.get("mission_id", f"mission-{int(time.time())}-{uuid.uuid4().hex[:8]}")
            strategy = deployment_request.get("strategy", self.default_strategy)
            
            # Resolve templates
            template_resolution = self._resolve_templates(deployment_request)
            if template_resolution.get("status") != "success":
                return template_resolution
            
            # Resolve dependencies
            dependency_resolution = self._resolve_dependencies(deployment_request, template_resolution)
            if dependency_resolution.get("status") != "success":
                return dependency_resolution
            
            # Generate execution plan
            execution_plan = self._generate_execution_plan(
                deployment_request,
                template_resolution,
                dependency_resolution,
                strategy
            )
            if execution_plan.get("status") != "success":
                return execution_plan
            
            # Run simulation if enabled
            simulation_result = None
            if self.simulation_enabled:
                simulation_result = self._run_simulation(execution_plan)
                if simulation_result.get("status") != "success":
                    return {
                        "status": "error",
                        "message": "Simulation failed",
                        "details": simulation_result
                    }
            
            # Optimize plan if enabled
            if self.optimization_enabled:
                execution_plan = self._optimize_plan(execution_plan, simulation_result)
            
            # Construct mission plan
            mission_plan = {
                "status": "success",
                "message": "Mission planning completed successfully",
                "mission_id": mission_id,
                "mission_name": mission_name,
                "strategy": strategy,
                "template_resolution": template_resolution,
                "dependency_resolution": dependency_resolution,
                "execution_plan": execution_plan,
                "simulation_result": simulation_result,
                "timestamp": datetime.now().isoformat(),
                "planner_id": self.planner_id
            }
            
            return mission_plan
        except Exception as e:
            logger.error(f"Error planning mission: {e}")
            return {"status": "error", "message": str(e)}
    
    def plan_rollback(self, deployment_id: str, deployment_status: Dict) -> Dict:
        """
        Plan a rollback mission for a deployment.
        
        Args:
            deployment_id: ID of the deployment to rollback
            deployment_status: Current status of the deployment
            
        Returns:
            Dict: Rollback mission plan
        """
        try:
            # Extract mission details from deployment status
            mission_details = deployment_status.get("mission_status", {})
            if not mission_details:
                return {
                    "status": "error",
                    "message": "No mission details found in deployment status"
                }
            
            # Generate rollback request
            rollback_request = {
                "name": f"rollback-{mission_details.get('mission_name', 'unknown')}",
                "mission_id": f"rollback-{deployment_id}",
                "strategy": "sequential",  # Rollbacks are always sequential for safety
                "type": "rollback",
                "original_deployment_id": deployment_id,
                "original_mission_id": mission_details.get("mission_id"),
                "components": self._generate_rollback_components(mission_details)
            }
            
            # Plan rollback mission
            return self.plan_mission(rollback_request)
        except Exception as e:
            logger.error(f"Error planning rollback: {e}")
            return {"status": "error", "message": str(e)}
    
    def _validate_request(self, deployment_request: Dict) -> Dict:
        """
        Validate a deployment request.
        
        Args:
            deployment_request: Deployment request
            
        Returns:
            Dict: Validation results
        """
        # Check for required fields
        if "components" not in deployment_request:
            return {
                "status": "error",
                "message": "No components specified in deployment request"
            }
        
        # Validate strategy
        strategy = deployment_request.get("strategy", self.default_strategy)
        if strategy not in self.planning_strategies:
            return {
                "status": "error",
                "message": f"Invalid planning strategy: {strategy}"
            }
        
        # Validate components
        components = deployment_request.get("components", [])
        if not components:
            return {
                "status": "error",
                "message": "Empty components list in deployment request"
            }
        
        for component in components:
            if "type" not in component:
                return {
                    "status": "error",
                    "message": f"Component missing required field: type"
                }
        
        return {"status": "success", "message": "Validation successful"}
    
    def _resolve_templates(self, deployment_request: Dict) -> Dict:
        """
        Resolve templates in a deployment request.
        
        Args:
            deployment_request: Deployment request
            
        Returns:
            Dict: Template resolution results
        """
        try:
            components = deployment_request.get("components", [])
            resolved_components = []
            
            for component in components:
                # Check if component uses a template
                if "template" in component:
                    template_name = component["template"]
                    template_params = component.get("template_params", {})
                    
                    # Resolve template
                    template_result = self.template_manager.resolve_template(template_name, template_params)
                    if template_result.get("status") != "success":
                        return template_result
                    
                    # Merge template with component
                    resolved_component = {**template_result.get("resolved_template", {}), **component}
                    resolved_components.append(resolved_component)
                else:
                    # No template, use component as is
                    resolved_components.append(component)
            
            return {
                "status": "success",
                "message": "Template resolution completed successfully",
                "resolved_components": resolved_components
            }
        except Exception as e:
            logger.error(f"Error resolving templates: {e}")
            return {"status": "error", "message": str(e)}
    
    def _resolve_dependencies(self, deployment_request: Dict, template_resolution: Dict) -> Dict:
        """
        Resolve dependencies in a deployment request.
        
        Args:
            deployment_request: Deployment request
            template_resolution: Template resolution results
            
        Returns:
            Dict: Dependency resolution results
        """
        try:
            resolved_components = template_resolution.get("resolved_components", [])
            dependency_graph = {}
            component_map = {}
            
            # Build component map
            for i, component in enumerate(resolved_components):
                component_id = component.get("id", f"component-{i}")
                component_map[component_id] = component
                dependency_graph[component_id] = {
                    "component": component,
                    "dependencies": component.get("dependencies", []),
                    "dependents": []
                }
            
            # Build dependency graph
            for component_id, node in dependency_graph.items():
                for dependency_id in node["dependencies"]:
                    if dependency_id in dependency_graph:
                        dependency_graph[dependency_id]["dependents"].append(component_id)
                    else:
                        return {
                            "status": "error",
                            "message": f"Dependency not found: {dependency_id} for component {component_id}"
                        }
            
            # Check for circular dependencies
            visited = set()
            temp_visited = set()
            
            def has_cycle(node_id):
                if node_id in temp_visited:
                    return True
                if node_id in visited:
                    return False
                
                temp_visited.add(node_id)
                
                for dependency_id in dependency_graph[node_id]["dependencies"]:
                    if has_cycle(dependency_id):
                        return True
                
                temp_visited.remove(node_id)
                visited.add(node_id)
                return False
            
            for component_id in dependency_graph:
                if component_id not in visited:
                    if has_cycle(component_id):
                        return {
                            "status": "error",
                            "message": f"Circular dependency detected in component {component_id}"
                        }
            
            return {
                "status": "success",
                "message": "Dependency resolution completed successfully",
                "dependency_graph": dependency_graph,
                "component_map": component_map
            }
        except Exception as e:
            logger.error(f"Error resolving dependencies: {e}")
            return {"status": "error", "message": str(e)}
    
    def _generate_execution_plan(self, deployment_request: Dict, template_resolution: Dict, dependency_resolution: Dict, strategy: str) -> Dict:
        """
        Generate an execution plan for a deployment.
        
        Args:
            deployment_request: Deployment request
            template_resolution: Template resolution results
            dependency_resolution: Dependency resolution results
            strategy: Planning strategy
            
        Returns:
            Dict: Execution plan
        """
        try:
            dependency_graph = dependency_resolution.get("dependency_graph", {})
            component_map = dependency_resolution.get("component_map", {})
            
            # Generate execution stages based on strategy
            if strategy == "sequential":
                execution_stages = self._generate_sequential_stages(dependency_graph)
            elif strategy == "parallel":
                execution_stages = self._generate_parallel_stages(dependency_graph)
            else:  # hybrid
                execution_stages = self._generate_hybrid_stages(dependency_graph)
            
            # Generate execution steps for each stage
            execution_steps = []
            for stage_index, stage in enumerate(execution_stages):
                stage_steps = []
                for component_id in stage:
                    component = component_map.get(component_id, {})
                    step = {
                        "step_id": f"step-{stage_index}-{component_id}",
                        "component_id": component_id,
                        "component_type": component.get("type"),
                        "component_name": component.get("name", component_id),
                        "stage": stage_index,
                        "action": component.get("action", "deploy"),
                        "parameters": component.get("parameters", {}),
                        "dependencies": component.get("dependencies", []),
                        "timeout": component.get("timeout", 300),  # seconds
                        "retry_policy": component.get("retry_policy", {"attempts": 3, "delay": 5})
                    }
                    stage_steps.append(step)
                execution_steps.extend(stage_steps)
            
            return {
                "status": "success",
                "message": "Execution plan generated successfully",
                "strategy": strategy,
                "stages": execution_stages,
                "steps": execution_steps
            }
        except Exception as e:
            logger.error(f"Error generating execution plan: {e}")
            return {"status": "error", "message": str(e)}
    
    def _generate_sequential_stages(self, dependency_graph: Dict) -> List[List[str]]:
        """
        Generate sequential execution stages.
        
        Args:
            dependency_graph: Dependency graph
            
        Returns:
            List[List[str]]: List of stages, each containing component IDs
        """
        # Topological sort
        visited = set()
        temp_visited = set()
        order = []
        
        def visit(node_id):
            if node_id in temp_visited:
                return
            if node_id in visited:
                return
            
            temp_visited.add(node_id)
            
            for dependency_id in dependency_graph[node_id]["dependencies"]:
                visit(dependency_id)
            
            temp_visited.remove(node_id)
            visited.add(node_id)
            order.append(node_id)
        
        for component_id in dependency_graph:
            if component_id not in visited:
                visit(component_id)
        
        # Reverse to get correct order
        order.reverse()
        
        # Each component gets its own stage in sequential execution
        return [[component_id] for component_id in order]
    
    def _generate_parallel_stages(self, dependency_graph: Dict) -> List[List[str]]:
        """
        Generate parallel execution stages.
        
        Args:
            dependency_graph: Dependency graph
            
        Returns:
            List[List[str]]: List of stages, each containing component IDs
        """
        # Calculate depths
        depths = {}
        
        def calculate_depth(node_id, current_depth=0):
            if node_id in depths:
                depths[node_id] = max(depths[node_id], current_depth)
            else:
                depths[node_id] = current_depth
            
            for dependent_id in dependency_graph[node_id]["dependents"]:
                calculate_depth(dependent_id, current_depth + 1)
        
        # Start with nodes that have no dependencies
        for component_id, node in dependency_graph.items():
            if not node["dependencies"]:
                calculate_depth(component_id)
        
        # Group by depth
        stages = {}
        for component_id, depth in depths.items():
            if depth not in stages:
                stages[depth] = []
            stages[depth].append(component_id)
        
        # Convert to list of stages
        return [stages[depth] for depth in sorted(stages.keys())]
    
    def _generate_hybrid_stages(self, dependency_graph: Dict) -> List[List[str]]:
        """
        Generate hybrid execution stages.
        
        Args:
            dependency_graph: Dependency graph
            
        Returns:
            List[List[str]]: List of stages, each containing component IDs
        """
        # Start with parallel stages
        stages = self._generate_parallel_stages(dependency_graph)
        
        # Optimize stages based on component types and dependencies
        optimized_stages = []
        
        for stage in stages:
            # Group components by type
            type_groups = {}
            for component_id in stage:
                component_type = dependency_graph[component_id]["component"].get("type")
                if component_type not in type_groups:
                    type_groups[component_type] = []
                type_groups[component_type].append(component_id)
            
            # Add each type group as a separate stage
            for component_type, components in type_groups.items():
                optimized_stages.append(components)
        
        return optimized_stages
    
    def _run_simulation(self, execution_plan: Dict) -> Dict:
        """
        Run a simulation of an execution plan.
        
        Args:
            execution_plan: Execution plan
            
        Returns:
            Dict: Simulation results
        """
        try:
            # Prepare simulation request
            simulation_request = {
                "execution_plan": execution_plan,
                "simulation_type": "full",
                "timeout": 60  # seconds
            }
            
            # Run simulation
            simulation_result = self.simulation_engine.run_simulation(simulation_request)
            return simulation_result
        except Exception as e:
            logger.error(f"Error running simulation: {e}")
            return {"status": "error", "message": str(e)}
    
    def _optimize_plan(self, execution_plan: Dict, simulation_result: Optional[Dict] = None) -> Dict:
        """
        Optimize an execution plan.
        
        Args:
            execution_plan: Execution plan
            simulation_result: Simulation results
            
        Returns:
            Dict: Optimized execution plan
        """
        # If simulation failed or no optimization needed, return original plan
        if not simulation_result or simulation_result.get("status") != "success":
            return execution_plan
        
        # Extract optimization suggestions from simulation
        optimization_suggestions = simulation_result.get("optimization_suggestions", [])
        if not optimization_suggestions:
            return execution_plan
        
        # Apply optimization suggestions
        optimized_steps = execution_plan.get("steps", [])
        
        for suggestion in optimization_suggestions:
            suggestion_type = suggestion.get("type")
            target_step = suggestion.get("target_step")
            
            if suggestion_type == "timeout_adjustment":
                # Find and adjust step timeout
                for i, step in enumerate(optimized_steps):
                    if step["step_id"] == target_step:
                        optimized_steps[i]["timeout"] = suggestion.get("timeout", step["timeout"])
            
            elif suggestion_type == "retry_policy_adjustment":
                # Find and adjust step retry policy
                for i, step in enumerate(optimized_steps):
                    if step["step_id"] == target_step:
                        optimized_steps[i]["retry_policy"] = suggestion.get("retry_policy", step["retry_policy"])
            
            elif suggestion_type == "parameter_adjustment":
                # Find and adjust step parameters
                for i, step in enumerate(optimized_steps):
                    if step["step_id"] == target_step:
                        parameters = step["parameters"].copy()
                        parameters.update(suggestion.get("parameters", {}))
                        optimized_steps[i]["parameters"] = parameters
        
        # Update execution plan with optimized steps
        execution_plan["steps"] = optimized_steps
        execution_plan["optimized"] = True
        
        return execution_plan
    
    def _generate_rollback_components(self, mission_details: Dict) -> List[Dict]:
        """
        Generate rollback components from mission details.
        
        Args:
            mission_details: Mission details
            
        Returns:
            List[Dict]: Rollback components
        """
        rollback_components = []
        
        # Extract steps from mission details
        steps = mission_details.get("execution_plan", {}).get("steps", [])
        
        # Generate rollback components in reverse order
        for step in reversed(steps):
            component_id = step.get("component_id")
            component_type = step.get("component_type")
            
            # Create rollback component
            rollback_component = {
                "id": f"rollback-{component_id}",
                "type": component_type,
                "action": "rollback",
                "original_component_id": component_id,
                "parameters": step.get("parameters", {})
            }
            
            rollback_components.append(rollback_component)
        
        return rollback_components
    
    def configure(self, config: Dict) -> Dict:
        """
        Configure the Mission Planner.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dict: Configuration results
        """
        try:
            # Update local configuration
            if "planning_strategies" in config:
                self.planning_strategies = config["planning_strategies"]
            
            if "default_strategy" in config:
                self.default_strategy = config["default_strategy"]
            
            if "simulation_enabled" in config:
                self.simulation_enabled = config["simulation_enabled"]
            
            if "optimization_enabled" in config:
                self.optimization_enabled = config["optimization_enabled"]
            
            # Configure template manager
            template_result = None
            if "template_manager" in config:
                template_result = self.template_manager.configure(config["template_manager"])
            
            # Configure simulation engine
            simulation_result = None
            if "simulation_engine" in config:
                simulation_result = self.simulation_engine.configure(config["simulation_engine"])
            
            return {
                "status": "success",
                "message": "Mission Planner configured successfully",
                "planner_id": self.planner_id,
                "template_result": template_result,
                "simulation_result": simulation_result
            }
        except Exception as e:
            logger.error(f"Error configuring Mission Planner: {e}")
            return {"status": "error", "message": str(e)}
