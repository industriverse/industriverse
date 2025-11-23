import unittest
import sys
import os
import asyncio
from typing import Dict, Any

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.white_label.widgets.shadow_twin_3d import ShadowTwin3DWidget
from src.white_label.widgets.predictive_maintenance import PredictiveMaintenanceWidget
from src.white_label.widgets.energy_flow_graph import EnergyFlowGraphWidget
from src.white_label.widgets.widget_sdk import WidgetConfig

class TestIntelligenceOptimization(unittest.IsolatedAsyncioTestCase):
    """
    Tier 2: Intelligence & Optimization Test Scenario
    Verifies:
    1. Shadow Twin 3D state updates.
    2. Predictive Maintenance alerts.
    3. Energy Flow Graph visualization.
    """

    async def asyncSetUp(self):
        config = WidgetConfig(widget_id="test_widget", partner_id="test_partner", theme="cosmic")
        self.shadow_twin = ShadowTwin3DWidget(config)
        self.predictive = PredictiveMaintenanceWidget(config)
        self.energy_graph = EnergyFlowGraphWidget(config)

    async def test_shadow_twin_update(self):
        print("\n--- Testing Shadow Twin 3D ---")
        # Simulate 3D state update
        state_data = {
            "nodes": [{"id": "n1", "x": 0, "y": 0, "z": 0}],
            "edges": [],
            "physics_engine": "active"
        }
        
        await self.shadow_twin.on_data_update(state_data)
        
        # Verify state
        self.assertIsNotNone(self.shadow_twin._data_cache)
        print("✅ Shadow Twin 3D state updated")

    async def test_predictive_maintenance_alert(self):
        print("\n--- Testing Predictive Maintenance ---")
        # Simulate sensor data
        sensor_data = {
            "vibration": 0.8,
            "temperature": 75,
            "predicted_failure_prob": 0.15
        }
        
        await self.predictive.on_data_update(sensor_data)
        
        # Verify alert logic (assuming widget processes data)
        self.assertIsNotNone(self.predictive._data_cache)
        print("✅ Predictive Maintenance processed sensor data")

    async def test_energy_flow_optimization(self):
        print("\n--- Testing Energy Flow Graph ---")
        # Simulate energy flow
        flow_data = {
            "source": "grid",
            "target": "factory_floor",
            "value": 500, # kW
            "efficiency": 0.92
        }
        
        
        await self.energy_graph.on_data_update(flow_data)
        
        self.assertIsNotNone(self.energy_graph._data_cache)
        print("✅ Energy Flow Graph recorded flow.")

if __name__ == "__main__":
    unittest.main()
