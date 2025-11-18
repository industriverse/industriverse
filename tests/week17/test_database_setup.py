"""
Week 17 Day 1: Database Setup Integration Tests
Tests for unified database schema, migrations, and initialization
"""

import pytest
import psycopg2
from pathlib import Path
import subprocess


class TestDatabaseSetup:
    """Test database setup and schema validation"""

    @pytest.fixture
    def db_connection(self):
        """Create database connection for testing"""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="industriverse",
                user="industriverse",
                password="changeme"
            )
            yield conn
            conn.close()
        except psycopg2.Error as e:
            pytest.skip(f"Database not available: {e}")

    def test_database_exists(self, db_connection):
        """Test that industriverse database exists"""
        cursor = db_connection.cursor()
        cursor.execute("SELECT current_database()")
        result = cursor.fetchone()
        assert result[0] == "industriverse"

    def test_schemas_exist(self, db_connection):
        """Test that all required schemas exist"""
        cursor = db_connection.cursor()

        required_schemas = [
            'behavioral',
            'capsules',
            'overseer',
            'security',
            'analytics'
        ]

        for schema in required_schemas:
            cursor.execute(
                "SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s",
                (schema,)
            )
            result = cursor.fetchone()
            assert result is not None, f"Schema '{schema}' does not exist"
            assert result[0] == schema

    def test_behavioral_tables_exist(self, db_connection):
        """Test that behavioral schema tables exist"""
        cursor = db_connection.cursor()

        required_tables = [
            'interaction_events',
            'user_sessions',
            'behavioral_vectors',
            'engagement_scores'
        ]

        for table in required_tables:
            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'behavioral'
                AND table_name = %s
                """,
                (table,)
            )
            result = cursor.fetchone()
            assert result is not None, f"Table 'behavioral.{table}' does not exist"

    def test_capsules_tables_exist(self, db_connection):
        """Test that capsules schema tables exist"""
        cursor = db_connection.cursor()

        required_tables = [
            'capsules',
            'capsule_metadata',
            'capsule_relationships',
            'shadow_twin_consensus'
        ]

        for table in required_tables:
            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'capsules'
                AND table_name = %s
                """,
                (table,)
            )
            result = cursor.fetchone()
            assert result is not None, f"Table 'capsules.{table}' does not exist"

    def test_interaction_events_columns(self, db_connection):
        """Test interaction_events table has required columns"""
        cursor = db_connection.cursor()

        required_columns = [
            'event_id',
            'timestamp',
            'event_type',
            'user_id',
            'session_id',
            'capsule_id',
            'interaction_data'
        ]

        cursor.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'behavioral'
            AND table_name = 'interaction_events'
            """
        )

        existing_columns = [row[0] for row in cursor.fetchall()]

        for col in required_columns:
            assert col in existing_columns, f"Column '{col}' missing from interaction_events"

    def test_indexes_exist(self, db_connection):
        """Test that required indexes exist"""
        cursor = db_connection.cursor()

        # Check for GIN index on interaction_data JSONB column
        cursor.execute(
            """
            SELECT indexname
            FROM pg_indexes
            WHERE schemaname = 'behavioral'
            AND tablename = 'interaction_events'
            AND indexdef LIKE '%gin%'
            """
        )

        result = cursor.fetchone()
        assert result is not None, "GIN index on interaction_data not found"

    def test_partitions_exist(self, db_connection):
        """Test that sensor_readings partitions are created"""
        cursor = db_connection.cursor()

        # Check if sensor_readings table exists (should be partitioned)
        cursor.execute(
            """
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'analytics'
            AND tablename LIKE 'sensor_readings%'
            """
        )

        tables = cursor.fetchall()
        # Should have at least the parent table
        assert len(tables) >= 1, "sensor_readings table not found"

    def test_uuid_extension_exists(self, db_connection):
        """Test that uuid-ossp extension is installed"""
        cursor = db_connection.cursor()

        cursor.execute(
            """
            SELECT extname
            FROM pg_extension
            WHERE extname = 'uuid-ossp'
            """
        )

        result = cursor.fetchone()
        assert result is not None, "uuid-ossp extension not installed"
        assert result[0] == "uuid-ossp"

    def test_database_config_file_exists(self):
        """Test that database configuration file exists"""
        config_file = Path("database/config/database.yaml")
        assert config_file.exists(), "database.yaml config file not found"

    def test_init_script_exists(self):
        """Test that initialization script exists"""
        init_script = Path("database/scripts/init_db.sh")
        assert init_script.exists(), "init_db.sh script not found"
        assert init_script.stat().st_mode & 0o111, "init_db.sh is not executable"

    def test_makefile_exists(self):
        """Test that Makefile exists"""
        makefile = Path("database/Makefile")
        assert makefile.exists(), "Database Makefile not found"

    def test_docker_compose_exists(self):
        """Test that docker-compose file exists"""
        docker_compose = Path("database/docker-compose.yml")
        assert docker_compose.exists(), "docker-compose.yml not found"


class TestDatabasePerformance:
    """Test database performance and query optimization"""

    @pytest.fixture
    def db_connection(self):
        """Create database connection for testing"""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="industriverse",
                user="industriverse",
                password="changeme"
            )
            yield conn
            conn.close()
        except psycopg2.Error as e:
            pytest.skip(f"Database not available: {e}")

    def test_interaction_events_insert_performance(self, db_connection):
        """Test interaction events insert performance"""
        import time

        cursor = db_connection.cursor()

        # Insert test event and measure time
        start_time = time.time()

        cursor.execute(
            """
            INSERT INTO behavioral.interaction_events
            (event_type, user_id, session_id, interaction_data)
            VALUES (%s, %s, %s, %s)
            """,
            ('test', 'test_user', 'test_session', '{}')
        )

        db_connection.commit()
        elapsed = time.time() - start_time

        # Should insert in less than 100ms
        assert elapsed < 0.1, f"Insert took {elapsed}s (> 100ms)"

        # Cleanup
        cursor.execute(
            "DELETE FROM behavioral.interaction_events WHERE user_id = 'test_user'"
        )
        db_connection.commit()

    def test_jsonb_query_performance(self, db_connection):
        """Test JSONB query performance with GIN index"""
        import time

        cursor = db_connection.cursor()

        # Query should use GIN index
        start_time = time.time()

        cursor.execute(
            """
            SELECT event_id
            FROM behavioral.interaction_events
            WHERE interaction_data @> '{"test": "value"}'::jsonb
            LIMIT 10
            """
        )

        elapsed = time.time() - start_time

        # Should query in less than 50ms
        assert elapsed < 0.05, f"JSONB query took {elapsed}s (> 50ms)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
