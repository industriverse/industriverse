import unittest
import sys
import os
import asyncio
from typing import Dict, Any

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.white_label.widgets.ai_shield_dashboard import AIShieldDashboardWidget
from src.white_label.widgets.compliance_score import ComplianceScoreWidget
from src.white_label.widgets.widget_sdk import WidgetConfig
from src.white_label.dac.registry import DACRegistry
from src.white_label.dac.manifest_schema import DACManifest
from src.core.dynamic_loader.loader_service import DynamicLoaderService

class TestSecurityCompliance(unittest.IsolatedAsyncioTestCase):
    """
    Tier 1: Security & Compliance Test Scenario
    Verifies:
    1. AI Shield Dashboard initialization and threat detection.
    2. Compliance Score calculation (NIST/ISO).
    3. Security DAC deployment via Registry.
    """

    async def asyncSetUp(self):
        config = WidgetConfig(widget_id="test_widget", partner_id="test_partner", theme="cosmic")
        self.dashboard = AIShieldDashboardWidget(config)
        self.compliance = ComplianceScoreWidget(config)
        self.registry = DACRegistry()
        self.loader = DynamicLoaderService()
        await self.loader.start()

    async def asyncTearDown(self):
        await self.loader.stop()

    async def test_ai_shield_dashboard_threats(self):
        print("\n--- Testing AI Shield Dashboard ---")
        # Simulate threat data
        threat_data = {
            "threat_count": 5,
            "security_score": 85,
            "active_alerts": ["SQL Injection Attempt", "Unauthorized Access"],
            "recent_events": [{"message": "Login failed", "time": "10:00"}]
        }
        
        # Update widget state
        await self.dashboard.on_data_update(threat_data)
        
        # Verify state
        self.assertEqual(self.dashboard.threat_count, 5)
        self.assertEqual(self.dashboard.security_score, 85)
        self.assertEqual(len(self.dashboard.active_alerts), 2)
        print("✅ AI Shield Dashboard correctly updated with threats")

    async def test_compliance_score_calculation(self):
        print("\n--- Testing Compliance Score ---")
        # Simulate compliance data update
        compliance_data = {
            "overall_score": 92,
            "frameworks": {
                "NIST": {"score": 95, "status": "compliant"},
                "ISO27001": {"score": 88, "status": "compliant"}
            },
            "recommendations": ["Enable MFA"]
        }
        
        await self.compliance.on_data_update(compliance_data)
        
        self.assertEqual(self.compliance.overall_score, 92)
        self.assertEqual(self.compliance.frameworks["NIST"]["score"], 95)
        print("✅ Compliance Score correctly updated")

    async def test_security_dac_deployment(self):
        print("\n--- Testing Security DAC Deployment ---")
        
        from src.white_label.dac.manifest_schema import ResourceRequirements, NetworkConfig, SecurityConfig, WidgetConfig
        
        # Create a mock manifest
        manifest = DACManifest(
            name="security-monitor",
            version="1.0.0",
            partner_id="test_partner",
            tier="security-essentials",
            description="Security Monitoring DAC",
            target_environments=["kubernetes"],
            resources=ResourceRequirements(cpu_cores=1.0, memory_gb=1.0),
            network=NetworkConfig(ingress_ports=[8080]),
            security=SecurityConfig(requires_tls=True),
            widgets=[WidgetConfig(widget_type="ai-shield-dashboard")]
        )
        
        # Register DAC
        package = self.registry.register(manifest)
        
        # Verify registration
        self.assertIsNotNone(package)
        self.assertEqual(package.dac_id, "test_partner:security-monitor")
        print("✅ Security DAC successfully registered")

        # Now deploy the registered DAC
        dac_id = package.dac_id # Use the ID from the registered package
        
        # Mock the registry client response for this DAC
        async def mock_get_model_info(model_id):
            if model_id == dac_id:
                return {
                    "id": model_id,
                    "path": "/tmp/mock_path",
                    "hash": "mock_hash_123",
                    "config": {"type": "security_dac"}
                }
            return None
            
        self.loader.registry_client.get_model_info = mock_get_model_info

        success = await self.loader.load_model(dac_id, context={"type": "security_dac"})
        self.assertTrue(success)
        print("✅ Security DAC successfully deployed via Dynamic Loader")
        active_models = self.loader.get_active_models()
        self.assertIn(dac_id, active_models)
        print(f"✅ Security DAC '{dac_id}' deployed successfully.")

if __name__ == "__main__":
    unittest.main()
