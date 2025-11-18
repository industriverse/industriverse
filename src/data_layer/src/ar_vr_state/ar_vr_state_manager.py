"""
AR/VR State Manager

Persists AR/VR state to Data Layer:
- Spatial anchors (position, rotation in 3D space)
- AR environment configurations
- User AR interaction history
- AR capsule placement and state

Part of Week 18-19: Architecture Unification - Day 6
"""

import logging
import asyncio
import time
from typing import Dict, Any, List, Optional, Tuple
import json

logger = logging.getLogger(__name__)


class ARVRStateManager:
    """
    Manages AR/VR state persistence in Data Layer.

    Database Tables:
    - ar_vr_state.spatial_anchors: 3D spatial anchors for AR objects
    - ar_vr_state.capsule_states: AR capsule rendering states
    - ar_vr_state.environments: AR/VR environment configurations
    - ar_vr_state.interaction_history: User interaction history in AR/VR

    Features:
    - Spatial anchor CRUD operations
    - AR capsule state persistence
    - Environment configuration management
    - Interaction history tracking
    - Async database operations with asyncpg
    """

    def __init__(self, database_pool=None):
        """
        Initialize AR/VR State Manager.

        Args:
            database_pool: AsyncPG database connection pool
        """
        self.db_pool = database_pool

        # In-memory cache for frequently accessed anchors
        self.anchor_cache: Dict[str, Dict[str, Any]] = {}

        # Statistics
        self.stats = {
            "anchors_created": 0,
            "capsule_states_saved": 0,
            "environments_registered": 0,
            "interactions_logged": 0
        }

        logger.info("AR/VR State Manager initialized")

    # ========================================================================
    # Spatial Anchors
    # ========================================================================

    async def save_spatial_anchor(
        self,
        anchor_id: str,
        position: Dict[str, float],
        rotation: Dict[str, float],
        environment_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Save spatial anchor to database.

        Args:
            anchor_id: Unique anchor identifier
            position: 3D position {x, y, z}
            rotation: Quaternion rotation {x, y, z, w}
            environment_id: AR/VR environment ID
            metadata: Additional metadata (e.g., capsule_id)

        Returns:
            Save result

        Table: ar_vr_state.spatial_anchors
        """
        if not self.db_pool:
            logger.warning("No database pool - caching anchor only")
            return self._cache_anchor_only(anchor_id, position, rotation, environment_id, metadata)

        try:
            logger.info(f"Saving spatial anchor: {anchor_id} in environment {environment_id}")

            metadata = metadata or {}

            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO ar_vr_state.spatial_anchors (
                        anchor_id,
                        environment_id,
                        position_x, position_y, position_z,
                        rotation_x, rotation_y, rotation_z, rotation_w,
                        created_at,
                        updated_at,
                        metadata
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW(), $10
                    )
                    ON CONFLICT (anchor_id) DO UPDATE SET
                        position_x = EXCLUDED.position_x,
                        position_y = EXCLUDED.position_y,
                        position_z = EXCLUDED.position_z,
                        rotation_x = EXCLUDED.rotation_x,
                        rotation_y = EXCLUDED.rotation_y,
                        rotation_z = EXCLUDED.rotation_z,
                        rotation_w = EXCLUDED.rotation_w,
                        updated_at = NOW(),
                        metadata = EXCLUDED.metadata
                """,
                    anchor_id,
                    environment_id,
                    position.get("x", 0.0),
                    position.get("y", 0.0),
                    position.get("z", 0.0),
                    rotation.get("x", 0.0),
                    rotation.get("y", 0.0),
                    rotation.get("z", 0.0),
                    rotation.get("w", 1.0),
                    json.dumps(metadata)
                )

            # Update cache
            self.anchor_cache[anchor_id] = {
                "anchor_id": anchor_id,
                "environment_id": environment_id,
                "position": position,
                "rotation": rotation,
                "metadata": metadata
            }

            self.stats["anchors_created"] += 1

            return {
                "status": "success",
                "anchor_id": anchor_id
            }

        except Exception as e:
            logger.error(f"Failed to save spatial anchor: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def get_spatial_anchor(self, anchor_id: str) -> Optional[Dict[str, Any]]:
        """Get spatial anchor by ID."""
        # Check cache first
        if anchor_id in self.anchor_cache:
            return self.anchor_cache[anchor_id]

        if not self.db_pool:
            return None

        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT
                        anchor_id,
                        environment_id,
                        position_x, position_y, position_z,
                        rotation_x, rotation_y, rotation_z, rotation_w,
                        created_at,
                        updated_at,
                        metadata
                    FROM ar_vr_state.spatial_anchors
                    WHERE anchor_id = $1
                """, anchor_id)

                if row:
                    anchor_data = {
                        "anchor_id": row["anchor_id"],
                        "environment_id": row["environment_id"],
                        "position": {
                            "x": float(row["position_x"]),
                            "y": float(row["position_y"]),
                            "z": float(row["position_z"])
                        },
                        "rotation": {
                            "x": float(row["rotation_x"]),
                            "y": float(row["rotation_y"]),
                            "z": float(row["rotation_z"]),
                            "w": float(row["rotation_w"])
                        },
                        "created_at": row["created_at"].timestamp(),
                        "updated_at": row["updated_at"].timestamp(),
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                    }

                    # Update cache
                    self.anchor_cache[anchor_id] = anchor_data

                    return anchor_data

                return None

        except Exception as e:
            logger.error(f"Failed to get spatial anchor: {e}")
            return None

    async def get_environment_anchors(
        self,
        environment_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get all spatial anchors for an environment."""
        if not self.db_pool:
            # Return cached anchors for this environment
            return [
                anchor for anchor in self.anchor_cache.values()
                if anchor.get("environment_id") == environment_id
            ]

        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT
                        anchor_id,
                        environment_id,
                        position_x, position_y, position_z,
                        rotation_x, rotation_y, rotation_z, rotation_w,
                        metadata
                    FROM ar_vr_state.spatial_anchors
                    WHERE environment_id = $1
                    ORDER BY created_at DESC
                    LIMIT $2
                """, environment_id, limit)

                return [
                    {
                        "anchor_id": row["anchor_id"],
                        "environment_id": row["environment_id"],
                        "position": {
                            "x": float(row["position_x"]),
                            "y": float(row["position_y"]),
                            "z": float(row["position_z"])
                        },
                        "rotation": {
                            "x": float(row["rotation_x"]),
                            "y": float(row["rotation_y"]),
                            "z": float(row["rotation_z"]),
                            "w": float(row["rotation_w"])
                        },
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                    }
                    for row in rows
                ]

        except Exception as e:
            logger.error(f"Failed to get environment anchors: {e}")
            return []

    async def delete_spatial_anchor(self, anchor_id: str) -> bool:
        """Delete spatial anchor."""
        if not self.db_pool:
            if anchor_id in self.anchor_cache:
                del self.anchor_cache[anchor_id]
            return True

        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    DELETE FROM ar_vr_state.spatial_anchors
                    WHERE anchor_id = $1
                """, anchor_id)

            # Remove from cache
            if anchor_id in self.anchor_cache:
                del self.anchor_cache[anchor_id]

            return True

        except Exception as e:
            logger.error(f"Failed to delete spatial anchor: {e}")
            return False

    # ========================================================================
    # AR Capsule States
    # ========================================================================

    async def save_ar_capsule_state(
        self,
        capsule_id: str,
        ar_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Save AR capsule state (position, scale, visibility, interaction state).

        Args:
            capsule_id: Capsule ID (references capsules.unified_registry)
            ar_state: AR state data
                {
                    "environment_id": str,
                    "anchor_id": str,
                    "scale_x": float,
                    "scale_y": float,
                    "scale_z": float,
                    "visible": bool,
                    "interaction_state": str,
                    "ar_metadata": dict
                }

        Returns:
            Save result

        Table: ar_vr_state.capsule_states
        """
        if not self.db_pool:
            logger.warning("No database pool - AR capsule state not persisted")
            return {"status": "skipped", "reason": "no_database"}

        try:
            logger.info(f"Saving AR capsule state: {capsule_id}")

            async with self.db_pool.acquire() as conn:
                # Build dynamic update based on provided fields
                if "environment_id" in ar_state and "anchor_id" in ar_state:
                    # Full insert/update
                    await conn.execute("""
                        INSERT INTO ar_vr_state.capsule_states (
                            capsule_id,
                            anchor_id,
                            scale_x, scale_y, scale_z,
                            visible,
                            interaction_state,
                            last_interaction_at,
                            ar_metadata
                        ) VALUES (
                            $1, $2, $3, $4, $5, $6, $7,
                            CASE WHEN $7 != 'idle' THEN NOW() ELSE NULL END,
                            $8
                        )
                        ON CONFLICT (capsule_id) DO UPDATE SET
                            anchor_id = EXCLUDED.anchor_id,
                            scale_x = EXCLUDED.scale_x,
                            scale_y = EXCLUDED.scale_y,
                            scale_z = EXCLUDED.scale_z,
                            visible = EXCLUDED.visible,
                            interaction_state = EXCLUDED.interaction_state,
                            last_interaction_at = CASE
                                WHEN EXCLUDED.interaction_state != 'idle'
                                THEN NOW()
                                ELSE capsule_states.last_interaction_at
                            END,
                            ar_metadata = EXCLUDED.ar_metadata
                    """,
                        capsule_id,
                        ar_state.get("anchor_id"),
                        ar_state.get("scale_x", 1.0),
                        ar_state.get("scale_y", 1.0),
                        ar_state.get("scale_z", 1.0),
                        ar_state.get("visible", True),
                        ar_state.get("interaction_state", "idle"),
                        json.dumps(ar_state.get("ar_metadata", {}))
                    )
                else:
                    # Partial update
                    await conn.execute("""
                        UPDATE ar_vr_state.capsule_states
                        SET
                            visible = COALESCE($2, visible),
                            interaction_state = COALESCE($3, interaction_state),
                            last_interaction_at = CASE
                                WHEN $3 IS NOT NULL AND $3 != 'idle'
                                THEN NOW()
                                ELSE last_interaction_at
                            END
                        WHERE capsule_id = $1
                    """,
                        capsule_id,
                        ar_state.get("visible"),
                        ar_state.get("interaction_state")
                    )

            self.stats["capsule_states_saved"] += 1

            return {
                "status": "success",
                "capsule_id": capsule_id
            }

        except Exception as e:
            logger.error(f"Failed to save AR capsule state: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def get_ar_capsule_state(self, capsule_id: str) -> Optional[Dict[str, Any]]:
        """Get AR capsule state by capsule ID."""
        if not self.db_pool:
            return None

        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT
                        capsule_id,
                        anchor_id,
                        scale_x, scale_y, scale_z,
                        visible,
                        interaction_state,
                        last_interaction_at,
                        ar_metadata
                    FROM ar_vr_state.capsule_states
                    WHERE capsule_id = $1
                """, capsule_id)

                if row:
                    return {
                        "capsule_id": row["capsule_id"],
                        "anchor_id": row["anchor_id"],
                        "scale": {
                            "x": float(row["scale_x"]),
                            "y": float(row["scale_y"]),
                            "z": float(row["scale_z"])
                        },
                        "visible": row["visible"],
                        "interaction_state": row["interaction_state"],
                        "last_interaction_at": row["last_interaction_at"].timestamp() if row["last_interaction_at"] else None,
                        "ar_metadata": json.loads(row["ar_metadata"]) if row["ar_metadata"] else {}
                    }

                return None

        except Exception as e:
            logger.error(f"Failed to get AR capsule state: {e}")
            return None

    # ========================================================================
    # Environment Management
    # ========================================================================

    async def register_environment(
        self,
        environment_id: str,
        environment_type: str,
        user_id: str,
        session_id: str,
        capabilities: List[str] = None,
        configuration: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Register AR/VR environment configuration.

        Args:
            environment_id: Environment ID
            environment_type: Type (mobile_ar, headset_ar, headset_vr, etc.)
            user_id: User ID
            session_id: Session ID
            capabilities: List of capabilities
            configuration: Environment configuration

        Returns:
            Registration result

        Table: ar_vr_state.environments
        """
        if not self.db_pool:
            logger.warning("No database pool - environment not persisted")
            return {"status": "skipped"}

        try:
            capabilities = capabilities or []
            configuration = configuration or {}

            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO ar_vr_state.environments (
                        environment_id,
                        environment_type,
                        user_id,
                        session_id,
                        capabilities,
                        configuration,
                        registered_at,
                        last_active_at,
                        active
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, NOW(), NOW(), TRUE
                    )
                    ON CONFLICT (environment_id) DO UPDATE SET
                        last_active_at = NOW(),
                        active = TRUE,
                        capabilities = EXCLUDED.capabilities,
                        configuration = EXCLUDED.configuration
                """,
                    environment_id,
                    environment_type,
                    user_id,
                    session_id,
                    json.dumps(capabilities),
                    json.dumps(configuration)
                )

            self.stats["environments_registered"] += 1

            return {
                "status": "success",
                "environment_id": environment_id
            }

        except Exception as e:
            logger.error(f"Failed to register environment: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def deactivate_environment(self, environment_id: str):
        """Mark environment as inactive."""
        if not self.db_pool:
            return

        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE ar_vr_state.environments
                    SET active = FALSE, last_active_at = NOW()
                    WHERE environment_id = $1
                """, environment_id)

        except Exception as e:
            logger.error(f"Failed to deactivate environment: {e}")

    async def get_active_environments(
        self,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all active environments, optionally filtered by user."""
        if not self.db_pool:
            return []

        try:
            async with self.db_pool.acquire() as conn:
                if user_id:
                    rows = await conn.fetch("""
                        SELECT
                            environment_id,
                            environment_type,
                            user_id,
                            session_id,
                            capabilities,
                            configuration,
                            registered_at,
                            last_active_at
                        FROM ar_vr_state.environments
                        WHERE active = TRUE AND user_id = $1
                        ORDER BY last_active_at DESC
                    """, user_id)
                else:
                    rows = await conn.fetch("""
                        SELECT
                            environment_id,
                            environment_type,
                            user_id,
                            session_id,
                            capabilities,
                            configuration,
                            registered_at,
                            last_active_at
                        FROM ar_vr_state.environments
                        WHERE active = TRUE
                        ORDER BY last_active_at DESC
                    """)

                return [
                    {
                        "environment_id": row["environment_id"],
                        "environment_type": row["environment_type"],
                        "user_id": row["user_id"],
                        "session_id": row["session_id"],
                        "capabilities": json.loads(row["capabilities"]) if row["capabilities"] else [],
                        "configuration": json.loads(row["configuration"]) if row["configuration"] else {},
                        "registered_at": row["registered_at"].timestamp(),
                        "last_active_at": row["last_active_at"].timestamp()
                    }
                    for row in rows
                ]

        except Exception as e:
            logger.error(f"Failed to get active environments: {e}")
            return []

    # ========================================================================
    # Interaction History
    # ========================================================================

    async def log_interaction(
        self,
        environment_id: str,
        user_id: str,
        capsule_id: Optional[str],
        interaction_type: str,
        interaction_data: Dict[str, Any]
    ) -> bool:
        """
        Log AR/VR interaction to history.

        Args:
            environment_id: Environment ID
            user_id: User ID
            capsule_id: Capsule ID (optional)
            interaction_type: Type of interaction
            interaction_data: Interaction data

        Returns:
            Success status

        Table: ar_vr_state.interaction_history
        """
        if not self.db_pool:
            return False

        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO ar_vr_state.interaction_history (
                        environment_id,
                        user_id,
                        capsule_id,
                        interaction_type,
                        interaction_data,
                        timestamp
                    ) VALUES (
                        $1, $2, $3, $4, $5, NOW()
                    )
                """,
                    environment_id,
                    user_id,
                    capsule_id,
                    interaction_type,
                    json.dumps(interaction_data)
                )

            self.stats["interactions_logged"] += 1

            return True

        except Exception as e:
            logger.error(f"Failed to log interaction: {e}")
            return False

    # ========================================================================
    # Helpers
    # ========================================================================

    def _cache_anchor_only(
        self,
        anchor_id: str,
        position: Dict[str, float],
        rotation: Dict[str, float],
        environment_id: str,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Cache anchor when database unavailable."""
        self.anchor_cache[anchor_id] = {
            "anchor_id": anchor_id,
            "environment_id": environment_id,
            "position": position,
            "rotation": rotation,
            "metadata": metadata or {}
        }

        self.stats["anchors_created"] += 1

        return {
            "status": "success",
            "anchor_id": anchor_id,
            "warning": "cached_only_no_database"
        }

    # ========================================================================
    # Statistics
    # ========================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """Get state manager statistics."""
        return {
            **self.stats,
            "anchor_cache_size": len(self.anchor_cache)
        }


# ============================================================================
# Singleton instance
# ============================================================================

_ar_state_manager_instance = None


def get_ar_vr_state_manager(database_pool=None) -> ARVRStateManager:
    """
    Get singleton AR/VR State Manager instance.

    Args:
        database_pool: Database connection pool

    Returns:
        ARVRStateManager instance
    """
    global _ar_state_manager_instance

    if _ar_state_manager_instance is None:
        _ar_state_manager_instance = ARVRStateManager(database_pool=database_pool)

    return _ar_state_manager_instance
