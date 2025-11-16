"""
Database layer for Capsule Gateway Service
Production-ready PostgreSQL integration with asyncpg

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import asyncpg
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import os


class CapsuleDatabase:
    """
    Production PostgreSQL database for Capsule Gateway
    
    Uses asyncpg for high-performance async database operations
    """
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        database: str = None,
        user: str = None,
        password: str = None
    ):
        """
        Initialize database connection
        
        Args:
            host: PostgreSQL host (default: from env or localhost)
            port: PostgreSQL port (default: from env or 5432)
            database: Database name (default: from env or industriverse)
            user: Database user (default: from env or postgres)
            password: Database password (default: from env)
        """
        self.host = host or os.getenv('POSTGRES_HOST', 'localhost')
        self.port = port or int(os.getenv('POSTGRES_PORT', '5432'))
        self.database = database or os.getenv('POSTGRES_DB', 'industriverse')
        self.user = user or os.getenv('POSTGRES_USER', 'postgres')
        self.password = password or os.getenv('POSTGRES_PASSWORD', '')
        
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                min_size=10,
                max_size=100,
                command_timeout=60
            )
            print(f"✅ Connected to PostgreSQL: {self.host}:{self.port}/{self.database}")
            
            # Initialize schema
            await self._init_schema()
            
        except Exception as e:
            print(f"❌ Failed to connect to PostgreSQL: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            print("✅ Disconnected from PostgreSQL")
    
    async def _init_schema(self):
        """Initialize database schema"""
        async with self.pool.acquire() as conn:
            # Create capsule_activities table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS capsule_activities (
                    activity_id VARCHAR(255) PRIMARY KEY,
                    capsule_id VARCHAR(255) NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    state VARCHAR(50) NOT NULL DEFAULT 'active',
                    priority VARCHAR(50) NOT NULL DEFAULT 'medium',
                    utid VARCHAR(255),
                    metadata JSONB DEFAULT '{}',
                    device_tokens TEXT[],
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                )
            ''')
            
            # Create index on capsule_id
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_capsule_id 
                ON capsule_activities(capsule_id)
            ''')
            
            # Create index on state
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_state 
                ON capsule_activities(state)
            ''')
            
            # Create capsule_actions table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS capsule_actions (
                    action_id VARCHAR(255) PRIMARY KEY,
                    capsule_id VARCHAR(255) NOT NULL,
                    action_type VARCHAR(50) NOT NULL,
                    user_id VARCHAR(255),
                    metadata JSONB DEFAULT '{}',
                    result JSONB DEFAULT '{}',
                    timestamp TIMESTAMP NOT NULL DEFAULT NOW()
                )
            ''')
            
            # Create index on capsule_id for actions
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_action_capsule_id 
                ON capsule_actions(capsule_id)
            ''')
            
            # Create device_registry table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS device_registry (
                    device_token VARCHAR(255) PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    platform VARCHAR(50) NOT NULL,
                    app_version VARCHAR(50),
                    registered_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    last_seen TIMESTAMP NOT NULL DEFAULT NOW()
                )
            ''')
            
            # Create index on user_id
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_id 
                ON device_registry(user_id)
            ''')
            
            print("✅ Database schema initialized")
    
    # Activity operations
    
    async def create_activity(
        self,
        activity_id: str,
        capsule_id: str,
        title: str,
        message: str,
        priority: str = 'medium',
        utid: Optional[str] = None,
        metadata: Optional[Dict] = None,
        device_tokens: Optional[List[str]] = None
    ) -> Dict:
        """Create a new capsule activity"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO capsule_activities 
                (activity_id, capsule_id, title, message, priority, utid, metadata, device_tokens)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ''', activity_id, capsule_id, title, message, priority, utid,
                json.dumps(metadata or {}), device_tokens or [])
            
            return await self.get_activity_by_id(activity_id)
    
    async def get_activity_by_id(self, activity_id: str) -> Optional[Dict]:
        """Get activity by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT * FROM capsule_activities WHERE activity_id = $1
            ''', activity_id)
            
            if row:
                return dict(row)
            return None
    
    async def get_activity_by_capsule_id(self, capsule_id: str) -> Optional[Dict]:
        """Get activity by capsule ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT * FROM capsule_activities WHERE capsule_id = $1
                ORDER BY created_at DESC LIMIT 1
            ''', capsule_id)
            
            if row:
                return dict(row)
            return None
    
    async def update_activity(
        self,
        capsule_id: str,
        title: Optional[str] = None,
        message: Optional[str] = None,
        state: Optional[str] = None,
        priority: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Update activity"""
        async with self.pool.acquire() as conn:
            # Build update query dynamically
            updates = []
            params = []
            param_count = 1
            
            if title is not None:
                updates.append(f'title = ${param_count}')
                params.append(title)
                param_count += 1
            
            if message is not None:
                updates.append(f'message = ${param_count}')
                params.append(message)
                param_count += 1
            
            if state is not None:
                updates.append(f'state = ${param_count}')
                params.append(state)
                param_count += 1
            
            if priority is not None:
                updates.append(f'priority = ${param_count}')
                params.append(priority)
                param_count += 1
            
            if metadata is not None:
                updates.append(f'metadata = metadata || ${param_count}::jsonb')
                params.append(json.dumps(metadata))
                param_count += 1
            
            updates.append('updated_at = NOW()')
            params.append(capsule_id)
            
            if not updates:
                return await self.get_activity_by_capsule_id(capsule_id)
            
            query = f'''
                UPDATE capsule_activities 
                SET {', '.join(updates)}
                WHERE capsule_id = ${param_count}
                RETURNING *
            '''
            
            row = await conn.fetchrow(query, *params)
            if row:
                return dict(row)
            return None
    
    async def list_activities(
        self,
        state: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """List activities with optional filtering"""
        async with self.pool.acquire() as conn:
            query = 'SELECT * FROM capsule_activities WHERE 1=1'
            params = []
            param_count = 1
            
            if state:
                query += f' AND state = ${param_count}'
                params.append(state)
                param_count += 1
            
            if priority:
                query += f' AND priority = ${param_count}'
                params.append(priority)
                param_count += 1
            
            query += f' ORDER BY created_at DESC LIMIT ${param_count}'
            params.append(limit)
            
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]
    
    async def delete_activity(self, capsule_id: str) -> bool:
        """Delete activity"""
        async with self.pool.acquire() as conn:
            result = await conn.execute('''
                DELETE FROM capsule_activities WHERE capsule_id = $1
            ''', capsule_id)
            
            return result != 'DELETE 0'
    
    # Action operations
    
    async def create_action(
        self,
        action_id: str,
        capsule_id: str,
        action_type: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        result: Optional[Dict] = None
    ) -> Dict:
        """Create a new action"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO capsule_actions 
                (action_id, capsule_id, action_type, user_id, metadata, result)
                VALUES ($1, $2, $3, $4, $5, $6)
            ''', action_id, capsule_id, action_type, user_id,
                json.dumps(metadata or {}), json.dumps(result or {}))
            
            row = await conn.fetchrow('''
                SELECT * FROM capsule_actions WHERE action_id = $1
            ''', action_id)
            
            return dict(row)
    
    async def list_actions(self, capsule_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """List actions"""
        async with self.pool.acquire() as conn:
            if capsule_id:
                rows = await conn.fetch('''
                    SELECT * FROM capsule_actions 
                    WHERE capsule_id = $1
                    ORDER BY timestamp DESC LIMIT $2
                ''', capsule_id, limit)
            else:
                rows = await conn.fetch('''
                    SELECT * FROM capsule_actions 
                    ORDER BY timestamp DESC LIMIT $1
                ''', limit)
            
            return [dict(row) for row in rows]
    
    # Device registry operations
    
    async def register_device(
        self,
        device_token: str,
        user_id: str,
        platform: str,
        app_version: Optional[str] = None
    ):
        """Register a device"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO device_registry 
                (device_token, user_id, platform, app_version)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (device_token) 
                DO UPDATE SET last_seen = NOW()
            ''', device_token, user_id, platform, app_version)
    
    async def get_user_devices(self, user_id: str) -> List[str]:
        """Get all device tokens for a user"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT device_token FROM device_registry 
                WHERE user_id = $1
            ''', user_id)
            
            return [row['device_token'] for row in rows]
    
    async def unregister_device(self, device_token: str):
        """Unregister a device"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                DELETE FROM device_registry WHERE device_token = $1
            ''', device_token)
    
    # Statistics
    
    async def get_statistics(self) -> Dict:
        """Get database statistics"""
        async with self.pool.acquire() as conn:
            # Total activities
            total_activities = await conn.fetchval('''
                SELECT COUNT(*) FROM capsule_activities
            ''')
            
            # Active activities
            active_activities = await conn.fetchval('''
                SELECT COUNT(*) FROM capsule_activities WHERE state = 'active'
            ''')
            
            # Total actions
            total_actions = await conn.fetchval('''
                SELECT COUNT(*) FROM capsule_actions
            ''')
            
            # State counts
            state_rows = await conn.fetch('''
                SELECT state, COUNT(*) as count 
                FROM capsule_activities 
                GROUP BY state
            ''')
            state_counts = {row['state']: row['count'] for row in state_rows}
            
            # Priority counts
            priority_rows = await conn.fetch('''
                SELECT priority, COUNT(*) as count 
                FROM capsule_activities 
                GROUP BY priority
            ''')
            priority_counts = {row['priority']: row['count'] for row in priority_rows}
            
            return {
                'total_activities': total_activities,
                'active_activities': active_activities,
                'total_actions': total_actions,
                'state_counts': state_counts,
                'priority_counts': priority_counts
            }
