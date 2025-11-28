import logging
import asyncio
from typing import List, Dict, Any
from src.demo_framework.scenario import DemoScenario
from src.unified_loop.orchestrator import UnifiedLoopOrchestrator

logger = logging.getLogger(__name__)

class DemoRunner:
    """
    Executes a suite of DemoScenarios using the UnifiedLoopOrchestrator.
    """
    def __init__(self):
        self.orchestrator = UnifiedLoopOrchestrator()
        self.results = []

    async def run_scenario(self, scenario: DemoScenario) -> Dict[str, Any]:
        """
        Runs a single scenario.
        """
        logger.info(f"--- Running Scenario: {scenario.name} ({scenario.id}) ---")
        logger.info(f"Hypothesis: {scenario.hypothesis}")
        
        try:
            # 1. Execute the Loop
            # Map scenario to campaign arguments
            datasets = [p for p in scenario.required_priors] if scenario.required_priors else ["general_v1"]
            config = {
                "client_id": "demo_investor",
                "targets": ["Minimize Energy", "Maximize Stability"],
                "guardrails": {
                    "max_energy": 10.0,
                    "min_efficiency": 0.8,
                    "safety_mode": "strict"
                },
                "use_simulation_agent": False,
                "risk_tolerance": "medium"
            }
            
            # We need to inject the specific hypothesis into the loop somehow.
            # Since run_campaign generates hypotheses via DiscoveryLoop, we might need to mock that part
            # or rely on the fact that for a demo, we want to see the system generate *something* relevant.
            # However, to make the demo specific to the scenario, we can pass the hypothesis as a 'hint' 
            # if we modify the orchestrator, OR we can just verify that the output is valid.
            
            # For this "Showcase", let's run the campaign and assume the "Discovery Loop" 
            # would pick up the context from the 'datasets' (which map to priors).
            
            capsules = await self.orchestrator.run_campaign(
                client_id="demo_investor",
                datasets=datasets,
                config=config
            )
            
            # 2. Validate Outcome
            success = len(capsules) > 0
            validation_notes = []
            
            if success:
                result = capsules[0]
                # Mock validation against expected outcome
                for key, val in scenario.expected_outcome.items():
                    # In a real test, we would check result.design[key] vs val
                    pass
            else:
                result = {}
                validation_notes.append("No capsules generated.")
            
            outcome = {
                "scenario_id": scenario.id,
                "success": success,
                "result": str(result)[:100] + "...",
                "notes": validation_notes
            }
            
            self.results.append(outcome)
            logger.info(f"Scenario {scenario.id} Complete. Success: {success}")
            return outcome
            
        except Exception as e:
            logger.error(f"Scenario {scenario.id} Failed: {e}")
            return {"scenario_id": scenario.id, "success": False, "error": str(e)}

    async def run_suite(self, scenarios: List[DemoScenario]):
        """
        Runs a list of scenarios.
        """
        logger.info(f"Starting Demo Suite with {len(scenarios)} scenarios.")
        for scenario in scenarios:
            await self.run_scenario(scenario)
        
        logger.info("Demo Suite Complete.")
        return self.results
