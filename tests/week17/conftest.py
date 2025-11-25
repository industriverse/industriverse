"""
Week 17 Test Configuration
Shared fixtures and configuration for all Week 17 tests
"""

import pytest
import sys
from pathlib import Path

# Add src to Python path for imports
src_path = Path(__file__).parent.parent.parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def project_root():
    """Get project root directory"""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def src_dir(project_root):
    """Get src directory"""
    return project_root / "src"


@pytest.fixture(scope="session")
def database_dir(project_root):
    """Get database directory"""
    return project_root / "database"


@pytest.fixture
def skip_if_no_database():
    """Skip test if database is not available"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="industriverse",
            user="industriverse",
            password="changeme",
            connect_timeout=3
        )
        conn.close()
    except (psycopg2.Error, Exception):
        pytest.skip("Database not available")


@pytest.fixture
def skip_if_no_redis():
    """Skip test if Redis is not available"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, socket_connect_timeout=3)
        r.ping()
    except (redis.ConnectionError, Exception):
        pytest.skip("Redis not available")
