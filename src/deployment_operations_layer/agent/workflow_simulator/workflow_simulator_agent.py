"""
Workflow Simulator Agent

This module implements the Workflow Simulator Agent, which runs synthetic edge simulations 
before approval to go live. It provides comprehensive simulation capabilities to test
deployments in various environments and conditions before actual deployment.

The agent coordinates with other components to create realistic simulation scenarios,
execute them, analyze results, and generate reports for deployment decision-making.
"""

import logging
import uuid
import json
import time
from typing import Dict, List, Any, Optional, Tuple

from ..agent_utils import AgentBase
from .simulation_scenario_generator import SimulationScenarioGenerator
from .simulation_executor import SimulationExecutor
from .simulation_analyzer import SimulationAnalyzer
from .simulation_reporter import SimulationReporter

logger = logging.getLogger(__name__)

class WorkflowSimulatorAgent(AgentBase):
    """
    Agent responsible for running synthetic edge simulations before approval to go live.
    
    This agent creates and executes simulation scenarios that mimic real-world conditions
    to validate deployments before they are approved for production environments.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Workflow Simulator Agent.
        
        Args:
            config: Configuration dictionary for the agent
        """
        super().__init__(name="WorkflowSimulatorAgent", config=config)
        
        # Initialize components
        self.scenario_generator = SimulationScenarioGenerator(config.get("scenario_generator", {}))
        self.simulation_executor = SimulationExecutor(config.get("simulation_executor", {}))
        self.simulation_analyzer = SimulationAnalyzer(config.get("simulation_analyzer", {}))
        self.simulation_reporter = SimulationReporter(config.get("simulation_reporter", {}))
        
        # Simulation history
        self.simulation_history = {}
        
        logger.info("Workflow Simulator Agent initialized")
    
    def simulate_deployment(self, deployment_manifest: Dict[str, Any], 
                           environment_config: Dict[str, Any],
                           simulation_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run a simulation for a deployment in a specified environment.
        
        Args:
            deployment_manifest: The deployment manifest to simulate
            environment_config: Configuration of the target environment
            simulation_params: Additional parameters for the simulation
            
        Returns:
            Dictionary containing simulation results and recommendations
        """
        simulation_id = str(uuid.uuid4())
        logger.info(f"Starting deployment simulation {simulation_id}")
        
        # Generate simulation scenarios
        scenarios = self.scenario_generator.generate_scenarios(
            deployment_manifest, 
            environment_config,
            simulation_params
        )
        
        # Execute simulation
        simulation_results = self.simulation_executor.execute_simulation(
            scenarios, 
            deployment_manifest,
            environment_config
        )
        
        # Analyze results
        analysis_results = self.simulation_analyzer.analyze_results(simulation_results)
        
        # Generate report
        report = self.simulation_reporter.generate_report(
            simulation_id,
            deployment_manifest,
            environment_config,
            scenarios,
            simulation_results,
            analysis_results
        )
        
        # Store in history
        self.simulation_history[simulation_id] = {
            "timestamp": time.time(),
            "deployment_manifest": deployment_manifest,
            "environment_config": environment_config,
            "simulation_params": simulation_params,
            "scenarios": scenarios,
            "results": simulation_results,
            "analysis": analysis_results,
            "report": report
        }
        
        logger.info(f"Completed deployment simulation {simulation_id}")
        
        return {
            "simulation_id": simulation_id,
            "status": "completed",
            "results": analysis_results,
            "report": report,
            "recommendation": self._generate_recommendation(analysis_results)
        }
    
    def get_simulation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the history of simulations.
        
        Args:
            limit: Maximum number of history items to return
            
        Returns:
            List of simulation history items
        """
        history_items = sorted(
            self.simulation_history.items(),
            key=lambda x: x[1]["timestamp"],
            reverse=True
        )
        
        return [
            {
                "simulation_id": sim_id,
                "timestamp": data["timestamp"],
                "deployment_manifest_id": data["deployment_manifest"].get("id", "unknown"),
                "environment": data["environment_config"].get("name", "unknown"),
                "status": "completed",
                "recommendation": self._generate_recommendation(data["analysis"])
            }
            for sim_id, data in history_items[:limit]
        ]
    
    def get_simulation_details(self, simulation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific simulation.
        
        Args:
            simulation_id: ID of the simulation to retrieve
            
        Returns:
            Dictionary with simulation details or None if not found
        """
        if simulation_id not in self.simulation_history:
            logger.warning(f"Simulation {simulation_id} not found")
            return None
        
        return self.simulation_history[simulation_id]
    
    def compare_simulations(self, simulation_ids: List[str]) -> Dict[str, Any]:
        """
        Compare multiple simulations.
        
        Args:
            simulation_ids: List of simulation IDs to compare
            
        Returns:
            Dictionary with comparison results
        """
        simulations = []
        for sim_id in simulation_ids:
            if sim_id in self.simulation_history:
                simulations.append(self.simulation_history[sim_id])
            else:
                logger.warning(f"Simulation {sim_id} not found for comparison")
        
        if not simulations:
            return {"error": "No valid simulations found for comparison"}
        
        return self.simulation_analyzer.compare_simulations(simulations)
    
    def _generate_recommendation(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a deployment recommendation based on analysis results.
        
        Args:
            analysis_results: Results from simulation analysis
            
        Returns:
            Recommendation dictionary
        """
        # Extract key metrics
        success_rate = analysis_results.get("success_rate", 0)
        performance_score = analysis_results.get("performance_score", 0)
        resource_utilization = analysis_results.get("resource_utilization", 0)
        error_count = analysis_results.get("error_count", 0)
        
        # Determine recommendation
        if success_rate >= 0.95 and performance_score >= 0.8 and error_count == 0:
            recommendation = "approve"
            confidence = "high"
        elif success_rate >= 0.9 and performance_score >= 0.7 and error_count <= 2:
            recommendation = "approve_with_caution"
            confidence = "medium"
        elif success_rate >= 0.8 and performance_score >= 0.6:
            recommendation = "needs_improvements"
            confidence = "medium"
        else:
            recommendation = "reject"
            confidence = "high"
        
        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "reasons": analysis_results.get("insights", []),
            "improvements": analysis_results.get("improvement_suggestions", [])
        }
    
    def cleanup_simulation_history(self, max_age_days: int = 30) -> int:
        """
        Clean up old simulation history entries.
        
        Args:
            max_age_days: Maximum age in days to keep simulations
            
        Returns:
            Number of entries removed
        """
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        to_remove = [
            sim_id for sim_id, data in self.simulation_history.items()
            if current_time - data["timestamp"] > max_age_seconds
        ]
        
        for sim_id in to_remove:
            del self.simulation_history[sim_id]
        
        logger.info(f"Cleaned up {len(to_remove)} old simulation history entries")
        return len(to_remove)
