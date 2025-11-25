"""
Security Event Registry

Extension of Unified Capsule Registry for security events and threat intelligence.

Integrates with Week 18-19 architecture:
- Extends UnifiedCapsuleRegistry for security-specific operations
- Stores threat signatures, PUF data, baselines, events
- Provides threat correlation and pattern matching
- Publishes security events via MCP/A2A protocols

Use Cases:
- Register security events with thermodynamic fingerprints
- Correlate threats across devices
- Track device authentication history
- Store forensic evidence
- Generate compliance reports
"""

import logging
import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SecurityEventRegistry:
    """
    Security-focused extension of Unified Capsule Registry.

    Manages:
    - Threat signatures
    - Security events
    - Device PUFs
    - Thermodynamic baselines
    - Forensic evidence
    - Mitigation actions
    """

    def __init__(
        self,
        database_pool=None,
        unified_registry=None,
        protocol_connector=None,
        event_bus=None
    ):
        """
        Initialize Security Event Registry.

        Args:
            database_pool: PostgreSQL connection pool
            unified_registry: UnifiedCapsuleRegistry instance
            protocol_connector: RegistryProtocolConnector instance
            event_bus: Event bus for security alerts
        """
        self.db_pool = database_pool
        self.unified_registry = unified_registry
        self.protocol_connector = protocol_connector
        self.event_bus = event_bus

        # In-memory cache
        self.threat_cache = {}
        self.baseline_cache = {}
        self.cache_ttl = 300  # 5 minutes

        # Statistics
        self.stats = {
            "events_registered": 0,
            "threats_detected": 0,
            "false_positives": 0,
            "mitigations_executed": 0
        }

        logger.info("Security Event Registry initialized")

    async def register_security_event(
        self,
        event_type: str,
        device_id: str,
        thermodynamic_data: Dict[str, Any],
        severity: str,
        confidence: float,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Register security event.

        Args:
            event_type: Type of security event
            device_id: Affected device
            thermodynamic_data: Physics measurements
            severity: low, medium, high, critical
            confidence: 0.0 to 1.0
            **kwargs: Additional event data

        Returns:
            Registered event data
        """
        logger.info(
            f"Registering security event: {event_type} "
            f"on device {device_id} (severity: {severity})"
        )

        try:
            async with self.db_pool.acquire() as conn:
                # Insert event
                event_id = await conn.fetchval("""
                    INSERT INTO security_events.events (
                        event_type,
                        device_id,
                        thermodynamic_data,
                        severity,
                        confidence,
                        threat_category,
                        anomaly_metrics,
                        source_sensor,
                        metadata
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    RETURNING event_id
                """,
                    event_type,
                    device_id,
                    thermodynamic_data,
                    severity,
                    confidence,
                    kwargs.get("threat_category"),
                    kwargs.get("anomaly_metrics", {}),
                    kwargs.get("source_sensor"),
                    kwargs.get("metadata", {})
                )

                self.stats["events_registered"] += 1

                # Check if matches known threat signature
                signature_id = await self._match_threat_signature(
                    conn,
                    thermodynamic_data,
                    event_type
                )

                if signature_id:
                    await conn.execute("""
                        UPDATE security_events.events
                        SET signature_id = $1
                        WHERE event_id = $2
                    """, signature_id, event_id)

                    self.stats["threats_detected"] += 1

                # Publish event
                if self.event_bus:
                    await self.event_bus.publish("security.event.registered", {
                        "event_id": str(event_id),
                        "event_type": event_type,
                        "device_id": device_id,
                        "severity": severity,
                        "signature_matched": signature_id is not None,
                        "timestamp": time.time()
                    })

                # Broadcast via MCP if critical
                if severity == "critical" and self.protocol_connector:
                    await self._broadcast_critical_threat(
                        event_id,
                        event_type,
                        thermodynamic_data
                    )

                return {
                    "event_id": str(event_id),
                    "registered_at": datetime.now().isoformat(),
                    "signature_matched": signature_id is not None
                }

        except Exception as e:
            logger.error(f"Failed to register security event: {e}")
            raise

    async def register_threat_signature(
        self,
        threat_type: str,
        threat_name: str,
        thermodynamic_fingerprint: Dict[str, Any],
        severity: str,
        mitigation_strategy: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Register new threat signature.

        Args:
            threat_type: Category of threat
            threat_name: Human-readable name
            thermodynamic_fingerprint: Physics signature
            severity: Threat severity level
            mitigation_strategy: Optional response strategy

        Returns:
            Signature ID
        """
        logger.info(f"Registering threat signature: {threat_name}")

        try:
            async with self.db_pool.acquire() as conn:
                signature_id = await conn.fetchval("""
                    INSERT INTO security_events.threat_signatures (
                        threat_type,
                        threat_name,
                        thermodynamic_fingerprint,
                        severity,
                        mitigation_strategy
                    ) VALUES ($1, $2, $3, $4, $5)
                    RETURNING signature_id
                """,
                    threat_type,
                    threat_name,
                    thermodynamic_fingerprint,
                    severity,
                    mitigation_strategy or {}
                )

                logger.info(f"Threat signature registered: {signature_id}")

                return str(signature_id)

        except Exception as e:
            logger.error(f"Failed to register threat signature: {e}")
            raise

    async def correlate_threats(
        self,
        thermodynamic_pattern: Dict[str, Any],
        time_window_minutes: int = 60,
        similarity_threshold: float = 0.75
    ) -> List[Dict[str, Any]]:
        """
        Find correlated threats with similar thermodynamic patterns.

        Args:
            thermodynamic_pattern: Reference pattern
            time_window_minutes: Time window for correlation
            similarity_threshold: Minimum similarity (0.0 to 1.0)

        Returns:
            List of correlated events
        """
        logger.info("Correlating threats...")

        try:
            async with self.db_pool.acquire() as conn:
                # Query recent events
                time_cutoff = datetime.now() - timedelta(minutes=time_window_minutes)

                rows = await conn.fetch("""
                    SELECT
                        event_id,
                        event_type,
                        device_id,
                        thermodynamic_data,
                        severity,
                        confidence,
                        detected_at
                    FROM security_events.events
                    WHERE detected_at >= $1
                    AND false_positive = FALSE
                    ORDER BY detected_at DESC
                """, time_cutoff)

                # Calculate similarity for each event
                correlated = []
                for row in rows:
                    similarity = self._calculate_pattern_similarity(
                        thermodynamic_pattern,
                        row["thermodynamic_data"]
                    )

                    if similarity >= similarity_threshold:
                        correlated.append({
                            "event_id": str(row["event_id"]),
                            "event_type": row["event_type"],
                            "device_id": row["device_id"],
                            "severity": row["severity"],
                            "similarity": similarity,
                            "detected_at": row["detected_at"].isoformat()
                        })

                logger.info(f"Found {len(correlated)} correlated threats")

                return correlated

        except Exception as e:
            logger.error(f"Threat correlation failed: {e}")
            return []

    async def get_device_security_health(
        self,
        device_id: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive security health for device.

        Returns:
            Security health metrics
        """
        try:
            async with self.db_pool.acquire() as conn:
                # Query device security health view
                health = await conn.fetchrow("""
                    SELECT * FROM security_events.device_security_health
                    WHERE device_id = $1
                """, device_id)

                if not health:
                    return {
                        "device_id": device_id,
                        "status": "unknown",
                        "message": "No security data available"
                    }

                return dict(health)

        except Exception as e:
            logger.error(f"Failed to get device security health: {e}")
            return {"error": str(e)}

    async def store_forensic_evidence(
        self,
        event_id: str,
        evidence_type: str,
        data: Dict[str, Any],
        collected_by: str
    ) -> str:
        """
        Store forensic evidence for event.

        Args:
            event_id: Related security event
            evidence_type: Type of evidence
            data: Evidence data
            collected_by: Collector identity

        Returns:
            Evidence ID
        """
        logger.info(f"Storing forensic evidence for event {event_id}")

        try:
            # Calculate cryptographic hash
            import hashlib
            import json
            data_str = json.dumps(data, sort_keys=True)
            data_hash = hashlib.sha256(data_str.encode()).hexdigest()

            async with self.db_pool.acquire() as conn:
                evidence_id = await conn.fetchval("""
                    INSERT INTO security_events.forensic_evidence (
                        event_id,
                        evidence_type,
                        data,
                        collected_by,
                        cryptographic_hash
                    ) VALUES ($1, $2, $3, $4, $5)
                    RETURNING evidence_id
                """,
                    event_id,
                    evidence_type,
                    data,
                    collected_by,
                    data_hash
                )

                return str(evidence_id)

        except Exception as e:
            logger.error(f"Failed to store forensic evidence: {e}")
            raise

    async def record_mitigation_action(
        self,
        event_id: str,
        action_type: str,
        executed_by: str,
        result: Dict[str, Any],
        automated: bool = False
    ) -> str:
        """
        Record mitigation action taken in response to event.

        Args:
            event_id: Event being mitigated
            action_type: Type of action
            executed_by: Who/what executed it
            result: Action result
            automated: If action was automated

        Returns:
            Action ID
        """
        logger.info(f"Recording mitigation action for event {event_id}")

        try:
            async with self.db_pool.acquire() as conn:
                action_id = await conn.fetchval("""
                    INSERT INTO security_events.mitigation_actions (
                        event_id,
                        action_type,
                        executed_by,
                        automated,
                        status,
                        result
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING action_id
                """,
                    event_id,
                    action_type,
                    executed_by,
                    automated,
                    "completed",
                    result
                )

                self.stats["mitigations_executed"] += 1

                return str(action_id)

        except Exception as e:
            logger.error(f"Failed to record mitigation action: {e}")
            raise

    async def get_active_threats(
        self,
        severity_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get currently active threats.

        Args:
            severity_filter: Optional severity filter

        Returns:
            List of active threats
        """
        try:
            async with self.db_pool.acquire() as conn:
                query = """
                    SELECT * FROM security_events.active_threats
                    WHERE TRUE
                """
                params = []

                if severity_filter:
                    query += " AND severity = $1"
                    params.append(severity_filter)

                query += " ORDER BY severity DESC, detected_at DESC LIMIT 100"

                rows = await conn.fetch(query, *params)

                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get active threats: {e}")
            return []

    async def _match_threat_signature(
        self,
        conn,
        thermodynamic_data: Dict[str, Any],
        event_type: str
    ) -> Optional[str]:
        """
        Match thermodynamic data against known threat signatures.

        Returns:
            Signature ID if match found, None otherwise
        """
        try:
            # Query threat signatures
            signatures = await conn.fetch("""
                SELECT signature_id, thermodynamic_fingerprint
                FROM security_events.threat_signatures
                WHERE threat_type = $1
            """, event_type)

            # Find best match
            best_match = None
            best_similarity = 0.0

            for sig in signatures:
                similarity = self._calculate_pattern_similarity(
                    thermodynamic_data,
                    sig["thermodynamic_fingerprint"]
                )

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = sig["signature_id"]

            # Require 80% similarity to match
            if best_similarity >= 0.80:
                return str(best_match)

            return None

        except Exception as e:
            logger.error(f"Signature matching failed: {e}")
            return None

    def _calculate_pattern_similarity(
        self,
        pattern1: Dict[str, Any],
        pattern2: Dict[str, Any]
    ) -> float:
        """
        Calculate similarity between two thermodynamic patterns.

        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Get common keys
        common_keys = set(pattern1.keys()) & set(pattern2.keys())

        if not common_keys:
            return 0.0

        # Calculate normalized difference for each key
        similarities = []
        for key in common_keys:
            val1 = pattern1[key]
            val2 = pattern2[key]

            # Handle numeric values
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                if val1 == 0 and val2 == 0:
                    sim = 1.0
                elif val1 == 0 or val2 == 0:
                    sim = 0.0
                else:
                    diff = abs(val1 - val2) / max(abs(val1), abs(val2))
                    sim = 1.0 - diff
                similarities.append(sim)

        if not similarities:
            return 0.0

        # Average similarity
        import statistics
        return statistics.mean(similarities)

    async def _broadcast_critical_threat(
        self,
        event_id: str,
        event_type: str,
        thermodynamic_data: Dict[str, Any]
    ):
        """
        Broadcast critical threat via MCP protocol.

        Enables federated threat intelligence sharing.
        """
        if not self.protocol_connector:
            return

        try:
            # Publish threat signature via MCP
            await self.protocol_connector.broadcast_threat_signature(
                signature={
                    "event_id": str(event_id),
                    "event_type": event_type,
                    "thermodynamic_data": thermodynamic_data
                },
                severity="critical",
                affected_domains=["all"]
            )

            logger.info(f"Critical threat {event_id} broadcast via MCP")

        except Exception as e:
            logger.error(f"Failed to broadcast critical threat: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get security registry statistics."""
        return {
            **self.stats,
            "cache_size": len(self.threat_cache) + len(self.baseline_cache)
        }


# ============================================================================
# Singleton instance
# ============================================================================

_security_registry_instance = None


def get_security_event_registry(
    database_pool=None,
    unified_registry=None,
    protocol_connector=None,
    event_bus=None
) -> SecurityEventRegistry:
    """
    Get singleton Security Event Registry instance.

    Args:
        database_pool: PostgreSQL connection pool
        unified_registry: UnifiedCapsuleRegistry instance
        protocol_connector: RegistryProtocolConnector instance
        event_bus: Event bus

    Returns:
        SecurityEventRegistry instance
    """
    global _security_registry_instance

    if _security_registry_instance is None:
        _security_registry_instance = SecurityEventRegistry(
            database_pool=database_pool,
            unified_registry=unified_registry,
            protocol_connector=protocol_connector,
            event_bus=event_bus
        )

    return _security_registry_instance
