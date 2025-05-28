"""
Simulation Scenario Generator

This module is responsible for generating simulation scenarios for the Workflow Simulator Agent.
It creates realistic test scenarios that mimic various deployment conditions, edge cases,
and potential failure modes to thoroughly test deployments before they go live.
"""

import logging
import random
import uuid
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class SimulationScenarioGenerator:
    """
    Generates simulation scenarios for testing deployments in various conditions.
    
    This class creates comprehensive test scenarios that cover normal operations,
    edge cases, resource constraints, network issues, and other real-world conditions
    that might affect deployment success.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Simulation Scenario Generator.
        
        Args:
            config: Configuration dictionary for the generator
        """
        self.config = config or {}
        
        # Load scenario templates
        self.scenario_templates = self.config.get("scenario_templates", {
            "normal": {
                "description": "Normal operating conditions",
                "probability": 0.5,
                "network_conditions": "normal",
                "resource_availability": "normal",
                "load_profile": "normal"
            },
            "high_load": {
                "description": "High load conditions",
                "probability": 0.2,
                "network_conditions": "normal",
                "resource_availability": "constrained",
                "load_profile": "high"
            },
            "network_latency": {
                "description": "High network latency",
                "probability": 0.1,
                "network_conditions": "high_latency",
                "resource_availability": "normal",
                "load_profile": "normal"
            },
            "network_packet_loss": {
                "description": "Network packet loss",
                "probability": 0.1,
                "network_conditions": "packet_loss",
                "resource_availability": "normal",
                "load_profile": "normal"
            },
            "resource_constrained": {
                "description": "Resource constrained environment",
                "probability": 0.1,
                "network_conditions": "normal",
                "resource_availability": "severely_constrained",
                "load_profile": "normal"
            }
        })
        
        # Load network condition profiles
        self.network_profiles = self.config.get("network_profiles", {
            "normal": {
                "latency_ms": 5,
                "jitter_ms": 2,
                "packet_loss_percent": 0,
                "bandwidth_mbps": 1000
            },
            "high_latency": {
                "latency_ms": 100,
                "jitter_ms": 20,
                "packet_loss_percent": 0,
                "bandwidth_mbps": 1000
            },
            "packet_loss": {
                "latency_ms": 10,
                "jitter_ms": 5,
                "packet_loss_percent": 2,
                "bandwidth_mbps": 1000
            },
            "low_bandwidth": {
                "latency_ms": 20,
                "jitter_ms": 10,
                "packet_loss_percent": 0,
                "bandwidth_mbps": 10
            },
            "edge_connection": {
                "latency_ms": 50,
                "jitter_ms": 15,
                "packet_loss_percent": 1,
                "bandwidth_mbps": 5
            }
        })
        
        # Load resource availability profiles
        self.resource_profiles = self.config.get("resource_profiles", {
            "normal": {
                "cpu_available_percent": 80,
                "memory_available_percent": 80,
                "storage_available_percent": 80
            },
            "constrained": {
                "cpu_available_percent": 50,
                "memory_available_percent": 50,
                "storage_available_percent": 70
            },
            "severely_constrained": {
                "cpu_available_percent": 30,
                "memory_available_percent": 30,
                "storage_available_percent": 50
            }
        })
        
        # Load load profiles
        self.load_profiles = self.config.get("load_profiles", {
            "normal": {
                "requests_per_second": 100,
                "concurrent_users": 50,
                "data_transfer_mbps": 10
            },
            "high": {
                "requests_per_second": 500,
                "concurrent_users": 200,
                "data_transfer_mbps": 50
            },
            "peak": {
                "requests_per_second": 1000,
                "concurrent_users": 500,
                "data_transfer_mbps": 100
            }
        })
        
        logger.info("Simulation Scenario Generator initialized")
    
    def generate_scenarios(self, 
                          deployment_manifest: Dict[str, Any],
                          environment_config: Dict[str, Any],
                          simulation_params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Generate simulation scenarios based on deployment manifest and environment.
        
        Args:
            deployment_manifest: The deployment manifest to simulate
            environment_config: Configuration of the target environment
            simulation_params: Additional parameters for scenario generation
            
        Returns:
            List of simulation scenarios
        """
        simulation_params = simulation_params or {}
        
        # Determine number of scenarios to generate
        num_scenarios = simulation_params.get("num_scenarios", 5)
        
        # Extract deployment-specific information for customizing scenarios
        deployment_type = deployment_manifest.get("type", "standard")
        deployment_scale = deployment_manifest.get("scale", "medium")
        deployment_components = deployment_manifest.get("components", [])
        
        # Extract environment-specific information
        environment_type = environment_config.get("type", "kubernetes")
        is_edge = environment_config.get("is_edge", False)
        
        # Generate scenarios
        scenarios = []
        
        # Always include a normal scenario
        scenarios.append(self._create_scenario(
            "normal",
            deployment_manifest,
            environment_config,
            "normal"
        ))
        
        # Generate additional scenarios based on deployment and environment characteristics
        remaining_scenarios = num_scenarios - 1
        
        # Determine scenario types to include based on deployment and environment
        scenario_types = []
        
        # Add edge-specific scenarios if deploying to edge
        if is_edge:
            scenario_types.extend(["network_latency", "network_packet_loss", "resource_constrained"])
        
        # Add high load scenarios for larger deployments
        if deployment_scale in ["large", "xlarge"]:
            scenario_types.append("high_load")
        
        # Add specific scenarios based on deployment type
        if deployment_type == "data_intensive":
            scenario_types.append("network_latency")
        elif deployment_type == "compute_intensive":
            scenario_types.append("resource_constrained")
        
        # Fill remaining scenarios with weighted random selection
        weighted_templates = [(name, template["probability"]) 
                             for name, template in self.scenario_templates.items()]
        
        # Ensure we have enough scenario types
        while len(scenario_types) < remaining_scenarios:
            scenario_types.append(self._weighted_random_choice(weighted_templates))
        
        # Generate the scenarios
        for scenario_type in scenario_types[:remaining_scenarios]:
            scenarios.append(self._create_scenario(
                scenario_type,
                deployment_manifest,
                environment_config,
                f"{scenario_type}_{len(scenarios)}"
            ))
        
        logger.info(f"Generated {len(scenarios)} simulation scenarios")
        return scenarios
    
    def _create_scenario(self, 
                        scenario_type: str,
                        deployment_manifest: Dict[str, Any],
                        environment_config: Dict[str, Any],
                        scenario_id: str) -> Dict[str, Any]:
        """
        Create a single simulation scenario.
        
        Args:
            scenario_type: Type of scenario to create
            deployment_manifest: The deployment manifest
            environment_config: The environment configuration
            scenario_id: Unique identifier for the scenario
            
        Returns:
            Simulation scenario dictionary
        """
        # Get the scenario template
        template = self.scenario_templates.get(scenario_type, self.scenario_templates["normal"])
        
        # Get the network profile
        network_profile_name = template["network_conditions"]
        network_profile = self.network_profiles.get(network_profile_name, self.network_profiles["normal"])
        
        # Get the resource profile
        resource_profile_name = template["resource_availability"]
        resource_profile = self.resource_profiles.get(resource_profile_name, self.resource_profiles["normal"])
        
        # Get the load profile
        load_profile_name = template["load_profile"]
        load_profile = self.load_profiles.get(load_profile_name, self.load_profiles["normal"])
        
        # Create the scenario
        scenario = {
            "id": scenario_id,
            "type": scenario_type,
            "description": template["description"],
            "network_conditions": {
                "profile": network_profile_name,
                **network_profile
            },
            "resource_availability": {
                "profile": resource_profile_name,
                **resource_profile
            },
            "load_profile": {
                "profile": load_profile_name,
                **load_profile
            },
            "deployment_manifest": deployment_manifest,
            "environment_config": environment_config,
            "duration_seconds": 300,  # Default 5-minute simulation
            "created_at": self._get_timestamp()
        }
        
        return scenario
    
    def _weighted_random_choice(self, choices: List[tuple]) -> Any:
        """
        Make a weighted random choice from a list of (item, weight) tuples.
        
        Args:
            choices: List of (item, weight) tuples
            
        Returns:
            Randomly selected item based on weights
        """
        total_weight = sum(weight for _, weight in choices)
        r = random.uniform(0, total_weight)
        upto = 0
        
        for item, weight in choices:
            upto += weight
            if upto >= r:
                return item
                
        # Fallback to the last item if something goes wrong
        return choices[-1][0] if choices else None
    
    def _get_timestamp(self) -> int:
        """
        Get the current timestamp.
        
        Returns:
            Current timestamp in seconds
        """
        import time
        return int(time.time())
