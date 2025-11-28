"""
ASAL Policy Generator for Global UX Distribution.

This module generates Global Interaction Policies (GIPs) from UX Genomes
and integrates with ASAL (from Week 1) to distribute policies to all devices.
Week 11 deliverable.

Key Concepts:
- Global Interaction Policy (GIP): A distributable policy that devices can apply locally
- Policy Generation: Convert UX Genomes into ASAL-compatible policies
- Policy Distribution: Push policies to all devices via ASAL
- Local Application: Devices apply policies without server round-trip

Architecture:
  UX Genomes → Policy Generator → GIPs → ASAL → Devices
                                                    ↓
                                          Local Policy Application
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio

# Import ASAL service (from Week 1)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PolicyType(Enum):
    """Types of interaction policies."""
    LAYOUT_POLICY = "layout_policy"
    DENSITY_POLICY = "density_policy"
    INTERACTION_POLICY = "interaction_policy"
    ADAPTIVE_POLICY = "adaptive_policy"
    ERROR_MITIGATION_POLICY = "error_mitigation_policy"


class PolicyPriority(Enum):
    """Priority levels for policy application."""
    CRITICAL = 1    # Always apply (error mitigation)
    HIGH = 2        # Apply unless user override
    NORMAL = 3      # Apply as default
    LOW = 4         # Apply as suggestion


@dataclass
class GlobalInteractionPolicy:
    """
    A Global Interaction Policy (GIP) that can be distributed to all devices.
    
    Devices apply GIPs locally without server round-trip, enabling
    instant personalization even offline.
    """
    policy_id: str
    policy_name: str
    policy_type: str
    description: str
    
    # Trigger conditions (when to apply)
    trigger_conditions: Dict[str, Any]
    
    # Actions (what to apply)
    ux_actions: Dict[str, Any]
    
    # Priority and confidence
    priority: int  # PolicyPriority value
    confidence: float
    effectiveness: float
    
    # Source genome
    source_genome_id: str
    
    # Versioning
    version: str
    created_at: str
    updated_at: str
    
    # Distribution
    distributed_at: Optional[str] = None
    devices_applied: int = 0


@dataclass
class PolicyDistributionResult:
    """Result of policy distribution to devices."""
    policy_id: str
    devices_reached: int
    devices_applied: int
    devices_failed: int
    distribution_time_ms: float


class ASALPolicyGenerator:
    """
    ASAL Policy Generator that converts UX Genomes into distributable policies.
    
    Integrates with ASAL service (from Week 1) to push policies globally.
    
    Key Functions:
    - Generate GIPs from UX Genomes
    - Validate policy consistency
    - Distribute policies via ASAL
    - Track policy effectiveness
    """
    
    def __init__(self, asal_service_url: str = "http://localhost:8000"):
        """Initialize the ASAL Policy Generator."""
        self.asal_service_url = asal_service_url
        self.policies: Dict[str, GlobalInteractionPolicy] = {}
        self.distribution_history: List[PolicyDistributionResult] = []
        
        logger.info(f"ASALPolicyGenerator initialized (ASAL: {asal_service_url})")
    
    async def generate_policy_from_genome(
        self,
        genome: Dict[str, Any]
    ) -> GlobalInteractionPolicy:
        """
        Generate a Global Interaction Policy from a UX Genome.
        
        Args:
            genome: UX Genome dictionary
        
        Returns:
            GlobalInteractionPolicy ready for distribution
        """
        genome_id = genome["genome_id"]
        genome_type = genome["genome_type"]
        
        # Determine policy type
        policy_type_map = {
            "layout_preference": PolicyType.LAYOUT_POLICY.value,
            "density_preference": PolicyType.DENSITY_POLICY.value,
            "interaction_pattern": PolicyType.INTERACTION_POLICY.value,
            "error_pattern": PolicyType.ERROR_MITIGATION_POLICY.value
        }
        
        policy_type = policy_type_map.get(genome_type, PolicyType.ADAPTIVE_POLICY.value)
        
        # Determine priority
        if genome_type == "error_pattern":
            priority = PolicyPriority.CRITICAL.value
        elif genome["confidence"] > 0.9:
            priority = PolicyPriority.HIGH.value
        elif genome["confidence"] > 0.7:
            priority = PolicyPriority.NORMAL.value
        else:
            priority = PolicyPriority.LOW.value
        
        # Generate policy ID
        policy_id = f"gip_{genome_id}_{datetime.utcnow().strftime('%Y%m%d')}"
        
        policy = GlobalInteractionPolicy(
            policy_id=policy_id,
            policy_name=genome["pattern_name"],
            policy_type=policy_type,
            description=genome["description"],
            trigger_conditions=genome["trigger_conditions"],
            ux_actions=genome["ux_actions"],
            priority=priority,
            confidence=genome["confidence"],
            effectiveness=genome["effectiveness"],
            source_genome_id=genome_id,
            version="1.0",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )
        
        self.policies[policy_id] = policy
        
        logger.info(
            f"Generated policy {policy_id} from genome {genome_id} "
            f"(type={policy_type}, priority={priority})"
        )
        
        return policy
    
    async def generate_policies_from_genomes(
        self,
        genomes: List[Dict[str, Any]]
    ) -> List[GlobalInteractionPolicy]:
        """Generate policies from multiple genomes."""
        policies = []
        
        for genome in genomes:
            policy = await self.generate_policy_from_genome(genome)
            policies.append(policy)
        
        logger.info(f"Generated {len(policies)} policies from {len(genomes)} genomes")
        
        return policies
    
    async def validate_policy_consistency(
        self,
        policies: List[GlobalInteractionPolicy]
    ) -> Dict[str, Any]:
        """
        Validate that policies don't conflict with each other.
        
        Returns:
            Validation report with conflicts and warnings
        """
        conflicts = []
        warnings = []
        
        # Group policies by archetype
        by_archetype: Dict[str, List[GlobalInteractionPolicy]] = {}
        
        for policy in policies:
            archetype = policy.trigger_conditions.get("expertise_level", "unknown")
            if archetype not in by_archetype:
                by_archetype[archetype] = []
            by_archetype[archetype].append(policy)
        
        # Check for conflicts within each archetype
        for archetype, archetype_policies in by_archetype.items():
            # Check for conflicting layout policies
            layout_policies = [
                p for p in archetype_policies
                if p.policy_type == PolicyType.LAYOUT_POLICY.value
            ]
            
            if len(layout_policies) > 1:
                conflicts.append({
                    "archetype": archetype,
                    "conflict_type": "multiple_layout_policies",
                    "policies": [p.policy_id for p in layout_policies],
                    "resolution": "Use highest confidence policy"
                })
            
            # Check for conflicting density policies
            density_policies = [
                p for p in archetype_policies
                if p.policy_type == PolicyType.DENSITY_POLICY.value
            ]
            
            if len(density_policies) > 1:
                conflicts.append({
                    "archetype": archetype,
                    "conflict_type": "multiple_density_policies",
                    "policies": [p.policy_id for p in density_policies],
                    "resolution": "Use highest confidence policy"
                })
            
            # Warn about low-confidence policies
            low_confidence = [
                p for p in archetype_policies
                if p.confidence < 0.7
            ]
            
            if low_confidence:
                warnings.append({
                    "archetype": archetype,
                    "warning_type": "low_confidence_policies",
                    "policies": [p.policy_id for p in low_confidence],
                    "recommendation": "Collect more evidence before distributing"
                })
        
        validation_report = {
            "total_policies": len(policies),
            "conflicts": conflicts,
            "warnings": warnings,
            "valid": len(conflicts) == 0
        }
        
        logger.info(
            f"Policy validation: {len(policies)} policies, "
            f"{len(conflicts)} conflicts, {len(warnings)} warnings"
        )
        
        return validation_report
    
    async def resolve_conflicts(
        self,
        policies: List[GlobalInteractionPolicy],
        validation_report: Dict[str, Any]
    ) -> List[GlobalInteractionPolicy]:
        """
        Resolve policy conflicts by selecting highest confidence policies.
        
        Args:
            policies: List of policies with potential conflicts
            validation_report: Validation report from validate_policy_consistency
        
        Returns:
            List of policies with conflicts resolved
        """
        if validation_report["valid"]:
            return policies  # No conflicts
        
        resolved_policies = list(policies)
        
        for conflict in validation_report["conflicts"]:
            conflict_type = conflict["conflict_type"]
            conflicting_policy_ids = conflict["policies"]
            
            # Get conflicting policies
            conflicting_policies = [
                p for p in resolved_policies
                if p.policy_id in conflicting_policy_ids
            ]
            
            # Select highest confidence policy
            best_policy = max(conflicting_policies, key=lambda p: p.confidence)
            
            # Remove other policies
            for policy in conflicting_policies:
                if policy.policy_id != best_policy.policy_id:
                    resolved_policies.remove(policy)
                    logger.info(
                        f"Resolved conflict: Removed {policy.policy_id}, "
                        f"kept {best_policy.policy_id} (confidence={best_policy.confidence:.2f})"
                    )
        
        logger.info(
            f"Conflict resolution: {len(policies)} → {len(resolved_policies)} policies"
        )
        
        return resolved_policies
    
    async def distribute_policy_via_asal(
        self,
        policy: GlobalInteractionPolicy
    ) -> PolicyDistributionResult:
        """
        Distribute a policy to all devices via ASAL.
        
        Args:
            policy: Policy to distribute
        
        Returns:
            Distribution result
        """
        start_time = datetime.utcnow()
        
        # Prepare ASAL policy payload
        asal_payload = {
            "policy_id": policy.policy_id,
            "policy_type": policy.policy_type,
            "policy_name": policy.policy_name,
            "description": policy.description,
            
            # Trigger conditions (when to apply)
            "trigger": policy.trigger_conditions,
            
            # Actions (what to apply)
            "actions": policy.ux_actions,
            
            # Metadata
            "priority": policy.priority,
            "confidence": policy.confidence,
            "version": policy.version,
            "created_at": policy.created_at
        }
        
        # TODO: Actual ASAL API call
        # For now, simulate distribution
        logger.info(f"Distributing policy {policy.policy_id} via ASAL...")
        
        # Simulate API call
        await asyncio.sleep(0.1)
        
        # Simulate results
        devices_reached = 1000  # Would come from ASAL
        devices_applied = 950   # 95% success rate
        devices_failed = 50
        
        end_time = datetime.utcnow()
        distribution_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # Update policy
        policy.distributed_at = datetime.utcnow().isoformat()
        policy.devices_applied = devices_applied
        
        result = PolicyDistributionResult(
            policy_id=policy.policy_id,
            devices_reached=devices_reached,
            devices_applied=devices_applied,
            devices_failed=devices_failed,
            distribution_time_ms=distribution_time_ms
        )
        
        self.distribution_history.append(result)
        
        logger.info(
            f"Policy {policy.policy_id} distributed: "
            f"{devices_applied}/{devices_reached} devices ({distribution_time_ms:.1f}ms)"
        )
        
        return result
    
    async def distribute_all_policies(
        self,
        policies: List[GlobalInteractionPolicy]
    ) -> List[PolicyDistributionResult]:
        """Distribute multiple policies to all devices."""
        results = []
        
        for policy in policies:
            result = await self.distribute_policy_via_asal(policy)
            results.append(result)
        
        total_devices = sum(r.devices_applied for r in results)
        logger.info(
            f"Distributed {len(policies)} policies to {total_devices} total device-policy applications"
        )
        
        return results
    
    async def track_policy_effectiveness(
        self,
        policy_id: str,
        effectiveness_metrics: Dict[str, float]
    ):
        """
        Track effectiveness of a distributed policy.
        
        Args:
            policy_id: Policy identifier
            effectiveness_metrics: Metrics from devices (engagement, errors, etc.)
        """
        policy = self.policies.get(policy_id)
        if not policy:
            logger.warning(f"Policy {policy_id} not found")
            return
        
        # Update effectiveness score
        current_effectiveness = policy.effectiveness
        new_effectiveness = effectiveness_metrics.get("engagement_score", current_effectiveness)
        
        # Weighted average (80% current, 20% new)
        policy.effectiveness = 0.8 * current_effectiveness + 0.2 * new_effectiveness
        policy.updated_at = datetime.utcnow().isoformat()
        
        logger.info(
            f"Updated policy {policy_id} effectiveness: "
            f"{current_effectiveness:.2f} → {policy.effectiveness:.2f}"
        )
    
    def get_policy(self, policy_id: str) -> Optional[GlobalInteractionPolicy]:
        """Get a specific policy."""
        return self.policies.get(policy_id)
    
    def get_all_policies(self) -> List[GlobalInteractionPolicy]:
        """Get all generated policies."""
        return list(self.policies.values())
    
    def get_distribution_history(self) -> List[PolicyDistributionResult]:
        """Get policy distribution history."""
        return self.distribution_history


# Singleton instance
asal_policy_generator = ASALPolicyGenerator()
