import asyncpg
import os
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.dsn = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/industriverse")

    async def connect(self):
        """Initialize the connection pool."""
        try:
            self.pool = await asyncpg.create_pool(dsn=self.dsn, min_size=5, max_size=20)
            logger.info("Connected to PostgreSQL database.")
            await self.init_schema()
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            # In a real scenario, we might want to retry or fail hard.
            # For now, we'll log it.

    async def disconnect(self):
        """Close the connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Disconnected from PostgreSQL database.")

    async def init_schema(self):
        """Initialize the database schema if it doesn't exist."""
        if not self.pool:
            return

        async with self.pool.acquire() as conn:
            # Activities table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS activities (
                    id SERIAL PRIMARY KEY,
                    capsule_id TEXT NOT NULL,
                    activity_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    payload JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            
            # Devices table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS devices (
                    id SERIAL PRIMARY KEY,
                    device_token TEXT UNIQUE NOT NULL,
                    platform TEXT NOT NULL,
                    user_id TEXT,
                    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            logger.info("Database schema initialized.")

    async def execute(self, query: str, *args) -> str:
        """Execute a query (INSERT, UPDATE, DELETE)."""
        if not self.pool:
            raise ConnectionError("Database not connected")
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args) -> List[asyncpg.Record]:
        """Fetch multiple rows."""
        if not self.pool:
            raise ConnectionError("Database not connected")
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """Fetch a single row."""
        if not self.pool:
            raise ConnectionError("Database not connected")
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

db_manager = DatabaseManager()
