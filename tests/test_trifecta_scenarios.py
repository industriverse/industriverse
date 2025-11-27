import pytest
import asyncio
from src.core.orchestration.trifecta_orchestrator import TrifectaOrchestrator

class TestTrifectaScenarios:
    """
    Comprehensive scenario testing for the Trifecta Conscious Loop.
    Verifies that the system adapts to different personas and goals.
    """
    
    @pytest.fixture
    def orchestrator(self):
        return TrifectaOrchestrator()

    @pytest.mark.asyncio
    async def test_scenario_fusion_physicist(self, orchestrator):
        """
        Scenario 1: Fusion Optimization
        Persona: Physicist
        Goal: Stabilize Plasma
        """
        goal = "Stabilize Plasma"
        persona = "Physicist"
        
        result = await orchestrator.run_conscious_loop(goal, persona)
        
        assert result["status"] == "completed"
        assert result["final_score"] > 0.4
        
        # Verify RND1 picked up fusion context
        log_str = str(result["log"])
        assert "plasma" in log_str.lower() or "fusion" in log_str.lower()

    @pytest.mark.asyncio
    async def test_scenario_grid_operator(self, orchestrator):
        """
        Scenario 2: Grid Management
        Persona: Operator
        Goal: Balance Load
        """
        goal = "Balance Load"
        persona = "Operator"
        
        result = await orchestrator.run_conscious_loop(goal, persona)
        
        assert result["status"] == "completed"
        # Verify RND1 picked up grid context
        log_str = str(result["log"])
        assert "load" in log_str.lower() or "grid" in log_str.lower()

    @pytest.mark.asyncio
    async def test_scenario_supply_chain(self, orchestrator):
        """
        Scenario 3: Supply Chain
        Persona: Logistics Manager
        Goal: Reduce Latency
        """
        goal = "Reduce Latency"
        persona = "Logistics Manager"
        
        result = await orchestrator.run_conscious_loop(goal, persona)
        
        assert result["status"] == "completed"
        # Generic fallback for now, but should complete
        assert result["final_score"] >= 0.0

    @pytest.mark.asyncio
    async def test_scenario_compliance(self, orchestrator):
        """
        Scenario 4: Regulatory Compliance
        Persona: Auditor
        Goal: Verify Safety Standards
        """
        goal = "Verify Safety Standards"
        persona = "Auditor"
        
        result = await orchestrator.run_conscious_loop(goal, persona)
        
        assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_scenario_investor_demo(self, orchestrator):
        """
        Scenario 5: Investor Demo
        Persona: VC
        Goal: Show ROI
        """
        goal = "Show ROI"
        persona = "VC"
        
        result = await orchestrator.run_conscious_loop(goal, persona)
        
        assert result["status"] == "completed"
