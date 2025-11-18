"""
Week 17 Day 2: Behavioral Tracking API Bridge Tests
Integration tests for Python client, FastAPI endpoints, and TypeScript client
"""

import pytest
import asyncio
from datetime import datetime
import json


class TestBehavioralTrackingClient:
    """Test Python behavioral tracking client"""

    @pytest.fixture
    async def client(self):
        """Create behavioral tracking client"""
        try:
            from src.application_layer.behavioral_tracking.api_bridge.behavioral_tracking_client import (
                BehavioralTrackingClient
            )

            # Note: This would need actual database connection
            # For now, we're testing the structure
            pytest.skip("Requires database connection")

        except ImportError:
            pytest.skip("Behavioral tracking client not available")

    def test_client_module_imports(self):
        """Test that client module can be imported"""
        try:
            from src.application_layer.behavioral_tracking.api_bridge import (
                BehavioralTrackingClient,
                InteractionEventCreate,
                BehavioralVectorResponse
            )
            assert BehavioralTrackingClient is not None
            assert InteractionEventCreate is not None
            assert BehavioralVectorResponse is not None
        except ImportError as e:
            pytest.fail(f"Failed to import client module: {e}")

    def test_interaction_event_create_structure(self):
        """Test InteractionEventCreate Pydantic model structure"""
        try:
            from src.application_layer.behavioral_tracking.api_bridge.behavioral_tracking_client import (
                InteractionEventCreate
            )

            # Create test event
            event = InteractionEventCreate(
                event_type="click",
                user_id="test_user",
                session_id="test_session",
                capsule_id="test_capsule",
                device_type="web"
            )

            assert event.event_type == "click"
            assert event.user_id == "test_user"
            assert event.session_id == "test_session"

        except ImportError:
            pytest.skip("InteractionEventCreate not available")


class TestBehavioralTrackingAPI:
    """Test FastAPI REST endpoints"""

    @pytest.fixture
    def client(self):
        """Create FastAPI test client"""
        try:
            from fastapi.testclient import TestClient
            from src.application_layer.behavioral_tracking.api_bridge.behavioral_tracking_api import app

            return TestClient(app)
        except ImportError:
            pytest.skip("FastAPI or app not available")

    def test_api_module_imports(self):
        """Test that API module can be imported"""
        try:
            from src.application_layer.behavioral_tracking.api_bridge import behavioral_tracking_api
            assert behavioral_tracking_api is not None
        except ImportError as e:
            pytest.fail(f"Failed to import API module: {e}")

    def test_health_endpoint_structure(self, client):
        """Test health check endpoint structure"""
        response = client.get("/api/v1/behavioral/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "service" in data
        assert "version" in data
        assert data["service"] == "behavioral-tracking-api"


class TestTypeScriptClient:
    """Test TypeScript client structure and exports"""

    def test_typescript_client_exists(self):
        """Test that TypeScript client file exists"""
        from pathlib import Path

        ts_client = Path(
            "src/application_layer/behavioral_tracking/api_bridge/"
            "typescript_client/BehavioralTrackingClient.ts"
        )

        assert ts_client.exists(), "TypeScript client file not found"

    def test_typescript_client_exports(self):
        """Test that TypeScript client has required exports"""
        from pathlib import Path

        ts_client = Path(
            "src/application_layer/behavioral_tracking/api_bridge/"
            "typescript_client/BehavioralTrackingClient.ts"
        )

        if not ts_client.exists():
            pytest.skip("TypeScript client not found")

        content = ts_client.read_text()

        # Check for key exports
        assert "export class BehavioralTrackingClient" in content
        assert "export interface InteractionEvent" in content
        assert "export interface BehavioralVector" in content
        assert "export function useBehavioralTracking" in content

    def test_typescript_client_methods(self):
        """Test that TypeScript client has required methods"""
        from pathlib import Path

        ts_client = Path(
            "src/application_layer/behavioral_tracking/api_bridge/"
            "typescript_client/BehavioralTrackingClient.ts"
        )

        if not ts_client.exists():
            pytest.skip("TypeScript client not found")

        content = ts_client.read_text()

        # Check for required methods
        required_methods = [
            "healthCheck",
            "trackInteraction",
            "getBehavioralVector",
            "computeBehavioralVector",
            "getEngagementScore",
            "getSession",
            "getUserInteractions"
        ]

        for method in required_methods:
            assert f"async {method}" in content, f"Method '{method}' not found"


class TestAPIDocumentation:
    """Test API documentation"""

    def test_readme_exists(self):
        """Test that API bridge README exists"""
        from pathlib import Path

        readme = Path(
            "src/application_layer/behavioral_tracking/api_bridge/README.md"
        )

        assert readme.exists(), "API bridge README not found"

    def test_readme_content(self):
        """Test README has required sections"""
        from pathlib import Path

        readme = Path(
            "src/application_layer/behavioral_tracking/api_bridge/README.md"
        )

        if not readme.exists():
            pytest.skip("README not found")

        content = readme.read_text()

        required_sections = [
            "Overview",
            "Architecture",
            "Quick Start",
            "API Endpoints",
            "Configuration",
            "Testing",
            "Troubleshooting"
        ]

        for section in required_sections:
            assert section in content, f"Section '{section}' not found in README"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
