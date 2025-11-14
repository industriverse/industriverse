"""
Pytest Configuration and Fixtures

Shared fixtures and configuration for all test modules.
"""

import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
import numpy as np

# Import application components
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.eil_gateway import app
from diffusion.core.energy_field import EnergyField, EnergyState
from diffusion.core.diffusion_dynamics import ForwardDiffusion, ReverseDiffusion, DiffusionConfig
from security.auth import AuthManager, User
from security.rbac import Permission, Role


# ============================================================================
# Event Loop
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# API Client
# ============================================================================

@pytest.fixture
def client() -> Generator:
    """FastAPI test client"""
    with TestClient(app) as test_client:
        yield test_client


# ============================================================================
# Energy Field Fixtures
# ============================================================================

@pytest.fixture
def energy_field():
    """Energy field instance"""
    return EnergyField(
        shape=(32, 32),
        temperature=1.0,
        energy_tolerance=0.01,
        device="cpu"
    )


@pytest.fixture
def sample_energy_map():
    """Sample 2D energy map for testing"""
    np.random.seed(42)
    return np.random.randn(32, 32).astype(np.float32)


@pytest.fixture
def small_energy_map():
    """Small energy map for quick tests"""
    return np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)


# ============================================================================
# Diffusion Model Fixtures
# ============================================================================

@pytest.fixture
def diffusion_config():
    """Standard diffusion configuration"""
    return DiffusionConfig(
        timesteps=100,  # Reduced for faster tests
        noise_schedule="linear",
        beta_start=0.0001,
        beta_end=0.02,
        energy_guidance_scale=1.0
    )


@pytest.fixture
def forward_diffusion(diffusion_config):
    """Forward diffusion process"""
    return ForwardDiffusion(diffusion_config)


@pytest.fixture
def reverse_diffusion(diffusion_config):
    """Reverse diffusion process"""
    return ReverseDiffusion(diffusion_config)


# ============================================================================
# Security Fixtures
# ============================================================================

@pytest.fixture
def auth_manager():
    """Authentication manager"""
    return AuthManager(
        secret_key="test-secret-key-for-testing-only",
        algorithm="HS256",
        access_token_expire_minutes=30
    )


@pytest.fixture
def test_user():
    """Test user with developer role"""
    return User(
        user_id="test_user_123",
        username="testuser",
        email="test@eil-platform.io",
        hashed_password="$2b$12$dummy_hash",  # Dummy hash
        roles=[Role.DEVELOPER.value],
        permissions=[
            Permission.EIL_PREDICT.value,
            Permission.EIL_DIFFUSE.value,
            Permission.DATA_READ.value
        ],
        disabled=False
    )


@pytest.fixture
def admin_user():
    """Test user with admin role"""
    return User(
        user_id="admin_user_456",
        username="admin",
        email="admin@eil-platform.io",
        hashed_password="$2b$12$dummy_hash",
        roles=[Role.ADMIN.value],
        permissions=[Permission.ALL.value],
        disabled=False
    )


@pytest.fixture
def test_access_token(auth_manager, test_user):
    """Valid access token for test user"""
    return auth_manager.create_access_token(test_user)


@pytest.fixture
def admin_access_token(auth_manager, admin_user):
    """Valid access token for admin user"""
    return auth_manager.create_access_token(admin_user)


# ============================================================================
# HTTP Headers
# ============================================================================

@pytest.fixture
def auth_headers(test_access_token):
    """Authentication headers with Bearer token"""
    return {"Authorization": f"Bearer {test_access_token}"}


@pytest.fixture
def admin_headers(admin_access_token):
    """Admin authentication headers"""
    return {"Authorization": f"Bearer {admin_access_token}"}


# ============================================================================
# Test Data
# ============================================================================

@pytest.fixture
def predict_request_data(sample_energy_map):
    """Sample predict request data"""
    return {
        "energy_map": sample_energy_map.tolist(),
        "domain": "plasma",
        "cluster": "cluster_001",
        "node": "node_001",
        "num_steps": 1
    }


@pytest.fixture
def diffuse_request_data():
    """Sample diffuse request data"""
    return {
        "shape": [16, 16],
        "num_inference_steps": 10,
        "energy_guidance_scale": 1.0,
        "temperature": 1.0,
        "seed": 42
    }


@pytest.fixture
def proof_request_data():
    """Sample proof request data"""
    return {
        "energy_map": np.random.randn(16, 16).astype(np.float32).tolist(),
        "claimed_regime": "equilibrium",
        "metadata": {
            "domain": "thermal",
            "timestamp": "2025-01-01T00:00:00Z"
        }
    }


# ============================================================================
# Mock Objects
# ============================================================================

@pytest.fixture
def mock_s3_config():
    """Mock S3 configuration"""
    return {
        "bucket_name": "test-bucket",
        "region": "us-east-1",
        "endpoint_url": "http://localhost:9000",  # MinIO
        "access_key_id": "test-key",
        "secret_access_key": "test-secret"
    }


@pytest.fixture
def mock_influxdb_config():
    """Mock InfluxDB configuration"""
    return {
        "url": "http://localhost:8086",
        "token": "test-token",
        "org": "test-org",
        "bucket": "test-bucket"
    }


# ============================================================================
# Cleanup
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup after each test"""
    yield
    # Add any cleanup logic here
    pass


# ============================================================================
# Markers
# ============================================================================

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "physics: Physics validation tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
