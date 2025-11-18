"""
Unified Capsule Registry

Central registry for all capsules created across Application Layer and
Deployment Operations Layer, providing unified search, tracking, and
lifecycle management.

Part of Week 18-19: Architecture Unification - Day 4
"""

import logging
import asyncio
import time
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class RegistrySearchField(Enum):
    """Fields available for registry search."""
    CAPSULE_ID = "capsule_id"
    SOURCE = "source"
    TEMPLATE_ID = "template_id"
    BLUEPRINT_ID = "blueprint_id"
    STATUS = "status"
    GOVERNANCE_STATUS = "governance_status"
    GENERATION = "generation"
    PARENT_CAPSULE_ID = "parent_capsule_id"


class UnifiedCapsuleRegistry:
    """
    Unified registry for all capsules regardless of creation source.

    Features:
    - Unified search across all capsules
    - Lifecycle state tracking
    - Parent-child capsule relationships
    - Evolution lineage tracking
    - Governance status monitoring
    - PostgreSQL-backed persistence with JSONB
    - In-memory caching for performance

    Database Schema:
    - Table: capsules.unified_registry
    - Primary Key: capsule_id (UUID)
    - Indexed: source, template_id, blueprint_id, status
    - JSONB: capsule_data (with GIN index)
    """

    def __init__(self, database_pool=None, cache_ttl: int = 300):
        """
        Initialize the Unified Capsule Registry.

        Args:
            database_pool: AsyncPG database connection pool
            cache_ttl: Cache time-to-live in seconds (default: 300 = 5 minutes)
        """
        self.db_pool = database_pool
        self.cache_ttl = cache_ttl

        # In-memory cache: {capsule_id: (capsule_data, cached_at)}
        self.cache: Dict[str, tuple[Dict[str, Any], float]] = {}

        # Statistics
        self.stats = {
            "total_registered": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "searches_performed": 0
        }

        logger.info("Unified Capsule Registry initialized")

    # ========================================================================
    # Registration
    # ========================================================================

    async def register_capsule(
        self,
        capsule_id: str,
        capsule_data: Dict[str, Any],
        source: str
    ) -> Dict[str, Any]:
        """
        Register capsule in unified registry.

        Args:
            capsule_id: Capsule ID
            capsule_data: Complete capsule data including lifecycle context
            source: Source of creation ("application_layer" or "deployment_ops_layer")

        Returns:
            Registration result

        Stores in database schema: capsules.unified_registry
        """
        if not self.db_pool:
            logger.warning("No database pool - storing in cache only")
            return await self._register_in_cache_only(capsule_id, capsule_data, source)

        try:
            logger.info(f"Registering capsule in unified registry: {capsule_id} (source: {source})")

            # Extract key fields from capsule_data
            lifecycle_context = capsule_data.get("lifecycle_context", {})
            template_id = lifecycle_context.get("template_id")
            blueprint_id = lifecycle_context.get("blueprint_id")
            status = lifecycle_context.get("stage", "active")
            parent_capsule_id = lifecycle_context.get("parent_capsule_id")
            generation = lifecycle_context.get("generation", 1)

            # Extract governance status
            governance = capsule_data.get("governance", {})
            governance_status = "validated" if governance.get("validated_at") else "pending"

            async with self.db_pool.acquire() as conn:
                # Insert into database
                await conn.execute("""
                    INSERT INTO capsules.unified_registry (
                        capsule_id,
                        source,
                        template_id,
                        blueprint_id,
                        created_at,
                        updated_at,
                        status,
                        governance_status,
                        evolution_generation,
                        parent_capsule_id,
                        capsule_data,
                        metadata
                    ) VALUES (
                        $1, $2, $3, $4, NOW(), NOW(), $5, $6, $7, $8, $9, $10
                    )
                    ON CONFLICT (capsule_id) DO UPDATE SET
                        updated_at = NOW(),
                        status = EXCLUDED.status,
                        governance_status = EXCLUDED.governance_status,
                        capsule_data = EXCLUDED.capsule_data,
                        metadata = EXCLUDED.metadata
                """,
                    capsule_id,
                    source,
                    template_id,
                    blueprint_id,
                    status,
                    governance_status,
                    generation,
                    parent_capsule_id,
                    capsule_data,  # JSONB
                    {}  # metadata JSONB
                )

            # Update cache
            self.cache[capsule_id] = (capsule_data, time.time())

            # Update statistics
            self.stats["total_registered"] += 1

            logger.info(f"Capsule registered successfully: {capsule_id}")

            return {
                "status": "success",
                "capsule_id": capsule_id,
                "source": source
            }

        except Exception as e:
            logger.error(f"Failed to register capsule: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _register_in_cache_only(
        self,
        capsule_id: str,
        capsule_data: Dict[str, Any],
        source: str
    ) -> Dict[str, Any]:
        """Fallback registration when database is not available."""
        self.cache[capsule_id] = (capsule_data, time.time())
        self.stats["total_registered"] += 1

        logger.warning(f"Capsule registered in cache only (no database): {capsule_id}")

        return {
            "status": "success",
            "capsule_id": capsule_id,
            "source": source,
            "warning": "registered_in_cache_only"
        }

    # ========================================================================
    # Retrieval
    # ========================================================================

    async def get_capsule(self, capsule_id: str) -> Optional[Dict[str, Any]]:
        """
        Get capsule by ID.

        Args:
            capsule_id: Capsule ID

        Returns:
            Capsule data or None if not found
        """
        # Check cache first
        if capsule_id in self.cache:
            cached_data, cached_at = self.cache[capsule_id]
            # Check if cache is still valid
            if time.time() - cached_at < self.cache_ttl:
                self.stats["cache_hits"] += 1
                logger.debug(f"Cache hit for capsule: {capsule_id}")
                return cached_data

        self.stats["cache_misses"] += 1

        if not self.db_pool:
            logger.warning("No database pool - returning None")
            return None

        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT capsule_data
                    FROM capsules.unified_registry
                    WHERE capsule_id = $1
                """, capsule_id)

                if row:
                    capsule_data = row["capsule_data"]
                    # Update cache
                    self.cache[capsule_id] = (capsule_data, time.time())
                    return capsule_data

                return None

        except Exception as e:
            logger.error(f"Failed to get capsule: {e}")
            return None

    # ========================================================================
    # Search
    # ========================================================================

    async def search_capsules(
        self,
        filters: Dict[str, Any],
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search capsules across all sources.

        Args:
            filters: Search filters (e.g., {"source": "application_layer", "status": "active"})
            limit: Maximum number of results (default: 100)
            offset: Result offset for pagination (default: 0)

        Returns:
            List of matching capsules

        Supported filters:
        - source: "application_layer" or "deployment_ops_layer"
        - template_id: Template ID
        - blueprint_id: Blueprint ID
        - status: Lifecycle status
        - governance_status: "validated" or "pending"
        - generation: Generation number
        - parent_capsule_id: Parent capsule ID
        """
        if not self.db_pool:
            logger.warning("No database pool - searching cache only")
            return self._search_cache(filters, limit, offset)

        try:
            self.stats["searches_performed"] += 1

            # Build WHERE clause
            where_clauses = []
            params = []
            param_counter = 1

            for field, value in filters.items():
                if field in ["source", "template_id", "blueprint_id", "status",
                           "governance_status", "parent_capsule_id"]:
                    where_clauses.append(f"{field} = ${param_counter}")
                    params.append(value)
                    param_counter += 1
                elif field == "generation":
                    where_clauses.append(f"evolution_generation = ${param_counter}")
                    params.append(value)
                    param_counter += 1

            where_sql = " AND ".join(where_clauses) if where_clauses else "TRUE"

            # Add limit and offset
            params.append(limit)
            params.append(offset)

            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(f"""
                    SELECT capsule_data
                    FROM capsules.unified_registry
                    WHERE {where_sql}
                    ORDER BY created_at DESC
                    LIMIT ${param_counter} OFFSET ${param_counter + 1}
                """, *params)

                results = [row["capsule_data"] for row in rows]

                logger.info(f"Search completed: {len(results)} results (filters: {filters})")

                return results

        except Exception as e:
            logger.error(f"Failed to search capsules: {e}")
            return []

    def _search_cache(
        self,
        filters: Dict[str, Any],
        limit: int,
        offset: int
    ) -> List[Dict[str, Any]]:
        """Fallback search when database is not available."""
        results = []

        for capsule_data, cached_at in self.cache.values():
            # Check cache validity
            if time.time() - cached_at >= self.cache_ttl:
                continue

            # Apply filters
            lifecycle_context = capsule_data.get("lifecycle_context", {})
            governance = capsule_data.get("governance", {})

            match = True
            for field, value in filters.items():
                if field == "source" and lifecycle_context.get("source") != value:
                    match = False
                    break
                elif field == "template_id" and lifecycle_context.get("template_id") != value:
                    match = False
                    break
                elif field == "blueprint_id" and lifecycle_context.get("blueprint_id") != value:
                    match = False
                    break
                elif field == "status" and lifecycle_context.get("stage") != value:
                    match = False
                    break
                elif field == "generation" and lifecycle_context.get("generation") != value:
                    match = False
                    break

            if match:
                results.append(capsule_data)

        # Apply pagination
        return results[offset:offset + limit]

    # ========================================================================
    # Lineage Tracking
    # ========================================================================

    async def get_capsule_lineage(
        self,
        capsule_id: str,
        max_depth: int = 10
    ) -> Dict[str, Any]:
        """
        Get complete evolution lineage for a capsule.

        Traces parent-child relationships to build evolution tree.

        Args:
            capsule_id: Capsule ID
            max_depth: Maximum depth to traverse (default: 10)

        Returns:
            Lineage tree with parent and child capsules
        """
        if not self.db_pool:
            logger.warning("No database pool - lineage tracking not available")
            return {
                "capsule_id": capsule_id,
                "parents": [],
                "children": [],
                "generation": 0
            }

        try:
            # Get parents (ancestors)
            parents = await self._get_ancestors(capsule_id, max_depth)

            # Get children (descendants)
            children = await self._get_descendants(capsule_id, max_depth)

            # Get current capsule generation
            capsule = await self.get_capsule(capsule_id)
            generation = capsule.get("lifecycle_context", {}).get("generation", 0) if capsule else 0

            return {
                "capsule_id": capsule_id,
                "generation": generation,
                "parents": parents,
                "children": children,
                "total_ancestors": len(parents),
                "total_descendants": len(children)
            }

        except Exception as e:
            logger.error(f"Failed to get capsule lineage: {e}")
            return {
                "capsule_id": capsule_id,
                "error": str(e)
            }

    async def _get_ancestors(
        self,
        capsule_id: str,
        max_depth: int
    ) -> List[Dict[str, Any]]:
        """Get all ancestor capsules (parents)."""
        ancestors = []
        current_id = capsule_id
        depth = 0

        async with self.db_pool.acquire() as conn:
            while depth < max_depth:
                row = await conn.fetchrow("""
                    SELECT parent_capsule_id, capsule_data
                    FROM capsules.unified_registry
                    WHERE capsule_id = $1
                """, current_id)

                if not row or not row["parent_capsule_id"]:
                    break

                parent_id = row["parent_capsule_id"]
                ancestors.append({
                    "capsule_id": parent_id,
                    "depth": depth + 1
                })

                current_id = parent_id
                depth += 1

        return ancestors

    async def _get_descendants(
        self,
        capsule_id: str,
        max_depth: int
    ) -> List[Dict[str, Any]]:
        """Get all descendant capsules (children)."""
        descendants = []

        async with self.db_pool.acquire() as conn:
            # Find all children recursively
            # Note: This is a simplified version. For production, use WITH RECURSIVE query
            rows = await conn.fetch("""
                SELECT capsule_id, evolution_generation
                FROM capsules.unified_registry
                WHERE parent_capsule_id = $1
            """, capsule_id)

            for row in rows:
                descendants.append({
                    "capsule_id": row["capsule_id"],
                    "generation": row["evolution_generation"]
                })

        return descendants

    # ========================================================================
    # Statistics
    # ========================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        cache_hit_rate = (
            self.stats["cache_hits"] / (self.stats["cache_hits"] + self.stats["cache_misses"])
            if (self.stats["cache_hits"] + self.stats["cache_misses"]) > 0
            else 0
        )

        return {
            **self.stats,
            "cache_size": len(self.cache),
            "cache_hit_rate": round(cache_hit_rate * 100, 2)
        }

    async def get_registry_count(self) -> int:
        """Get total number of capsules in registry."""
        if not self.db_pool:
            return len(self.cache)

        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT COUNT(*) as count
                    FROM capsules.unified_registry
                """)
                return row["count"] if row else 0

        except Exception as e:
            logger.error(f"Failed to get registry count: {e}")
            return 0

    # ========================================================================
    # Cache Management
    # ========================================================================

    def clear_cache(self):
        """Clear the in-memory cache."""
        self.cache.clear()
        logger.info("Registry cache cleared")

    def invalidate_capsule(self, capsule_id: str):
        """Invalidate cache entry for specific capsule."""
        if capsule_id in self.cache:
            del self.cache[capsule_id]
            logger.debug(f"Cache invalidated for capsule: {capsule_id}")


# ============================================================================
# Singleton instance
# ============================================================================

_registry_instance = None


def get_unified_capsule_registry(database_pool=None) -> UnifiedCapsuleRegistry:
    """
    Get singleton Unified Capsule Registry instance.

    Args:
        database_pool: Database connection pool

    Returns:
        UnifiedCapsuleRegistry instance
    """
    global _registry_instance

    if _registry_instance is None:
        _registry_instance = UnifiedCapsuleRegistry(database_pool=database_pool)

    return _registry_instance
