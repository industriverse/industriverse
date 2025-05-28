"""
Compliance Snapshot Agent

This module implements the Compliance Snapshot Agent, which captures and validates
the compliance state of deployments against security and regulatory requirements.
It ensures that all deployments meet the necessary compliance standards before
going live and maintains an auditable record of compliance states.
"""

import logging
import uuid
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from ..agent_utils import AgentBase
from .compliance_validator import ComplianceValidator
from .compliance_reporter import ComplianceReporter
from .compliance_policy_manager import CompliancePolicyManager
from .compliance_evidence_collector import ComplianceEvidenceCollector

logger = logging.getLogger(__name__)

class ComplianceSnapshotAgent(AgentBase):
    """
    Agent responsible for capturing and validating compliance states of deployments.
    
    This agent ensures that all deployments meet the necessary security and regulatory
    requirements before going live, and maintains an auditable record of compliance
    states throughout the deployment lifecycle.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Compliance Snapshot Agent.
        
        Args:
            config: Configuration dictionary for the agent
        """
        super().__init__(name="ComplianceSnapshotAgent", config=config)
        
        # Initialize components
        self.validator = ComplianceValidator(config.get("validator", {}))
        self.reporter = ComplianceReporter(config.get("reporter", {}))
        self.policy_manager = CompliancePolicyManager(config.get("policy_manager", {}))
        self.evidence_collector = ComplianceEvidenceCollector(config.get("evidence_collector", {}))
        
        # Snapshot history
        self.snapshot_history = {}
        
        logger.info("Compliance Snapshot Agent initialized")
    
    def create_snapshot(self, 
                       deployment_manifest: Dict[str, Any],
                       environment_config: Dict[str, Any],
                       policy_set_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a compliance snapshot for a deployment.
        
        Args:
            deployment_manifest: The deployment manifest to validate
            environment_config: Configuration of the target environment
            policy_set_id: Optional ID of the policy set to use for validation
            
        Returns:
            Dictionary containing snapshot results
        """
        snapshot_id = str(uuid.uuid4())
        logger.info(f"Creating compliance snapshot {snapshot_id}")
        
        # Determine policy set to use
        if policy_set_id is None:
            policy_set_id = self._determine_policy_set(deployment_manifest, environment_config)
        
        policy_set = self.policy_manager.get_policy_set(policy_set_id)
        
        if not policy_set:
            logger.error(f"Policy set {policy_set_id} not found")
            return {
                "snapshot_id": snapshot_id,
                "status": "error",
                "error": f"Policy set {policy_set_id} not found",
                "timestamp": time.time()
            }
        
        # Collect evidence
        evidence = self.evidence_collector.collect_evidence(
            deployment_manifest,
            environment_config,
            policy_set
        )
        
        # Validate compliance
        validation_results = self.validator.validate_compliance(
            deployment_manifest,
            environment_config,
            policy_set,
            evidence
        )
        
        # Generate report
        report = self.reporter.generate_report(
            snapshot_id,
            deployment_manifest,
            environment_config,
            policy_set,
            evidence,
            validation_results
        )
        
        # Create snapshot
        snapshot = {
            "snapshot_id": snapshot_id,
            "timestamp": time.time(),
            "deployment_manifest_id": deployment_manifest.get("id", "unknown"),
            "environment": environment_config.get("name", "unknown"),
            "policy_set_id": policy_set_id,
            "validation_results": validation_results,
            "report": report,
            "status": "completed",
            "compliant": validation_results.get("compliant", False)
        }
        
        # Store in history
        self.snapshot_history[snapshot_id] = snapshot
        
        logger.info(f"Completed compliance snapshot {snapshot_id}, compliant: {snapshot['compliant']}")
        
        return snapshot
    
    def get_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific compliance snapshot.
        
        Args:
            snapshot_id: ID of the snapshot to retrieve
            
        Returns:
            Dictionary containing snapshot data or None if not found
        """
        return self.snapshot_history.get(snapshot_id)
    
    def get_snapshot_history(self, 
                            deployment_id: Optional[str] = None,
                            environment: Optional[str] = None,
                            limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the history of compliance snapshots.
        
        Args:
            deployment_id: Optional deployment ID to filter by
            environment: Optional environment name to filter by
            limit: Maximum number of history items to return
            
        Returns:
            List of snapshot history items
        """
        # Filter snapshots
        filtered_snapshots = []
        for snapshot_id, snapshot in self.snapshot_history.items():
            if deployment_id and snapshot.get("deployment_manifest_id") != deployment_id:
                continue
            
            if environment and snapshot.get("environment") != environment:
                continue
            
            filtered_snapshots.append(snapshot)
        
        # Sort by timestamp (newest first)
        filtered_snapshots.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Limit results
        return filtered_snapshots[:limit]
    
    def compare_snapshots(self, snapshot_ids: List[str]) -> Dict[str, Any]:
        """
        Compare multiple compliance snapshots.
        
        Args:
            snapshot_ids: List of snapshot IDs to compare
            
        Returns:
            Dictionary with comparison results
        """
        snapshots = []
        for snapshot_id in snapshot_ids:
            if snapshot_id in self.snapshot_history:
                snapshots.append(self.snapshot_history[snapshot_id])
            else:
                logger.warning(f"Snapshot {snapshot_id} not found for comparison")
        
        if len(snapshots) < 2:
            return {"error": "Need at least two valid snapshots to compare"}
        
        # Sort by timestamp
        snapshots.sort(key=lambda x: x["timestamp"])
        
        # Extract key information
        comparison = {
            "snapshots": [
                {
                    "snapshot_id": s["snapshot_id"],
                    "timestamp": s["timestamp"],
                    "deployment_manifest_id": s["deployment_manifest_id"],
                    "environment": s["environment"],
                    "policy_set_id": s["policy_set_id"],
                    "compliant": s["compliant"]
                }
                for s in snapshots
            ],
            "policy_changes": self._detect_policy_changes(snapshots),
            "compliance_changes": self._detect_compliance_changes(snapshots),
            "insights": self._generate_comparison_insights(snapshots)
        }
        
        return comparison
    
    def _determine_policy_set(self, 
                             deployment_manifest: Dict[str, Any],
                             environment_config: Dict[str, Any]) -> str:
        """
        Determine the appropriate policy set for a deployment.
        
        Args:
            deployment_manifest: The deployment manifest
            environment_config: Configuration of the target environment
            
        Returns:
            ID of the appropriate policy set
        """
        # Extract relevant information
        environment_type = environment_config.get("type", "kubernetes")
        is_edge = environment_config.get("is_edge", False)
        region = environment_config.get("region", "unknown")
        industry = deployment_manifest.get("industry", "general")
        
        # Get available policy sets
        policy_sets = self.policy_manager.list_policy_sets()
        
        # Find matching policy set
        for policy_set_id, policy_set in policy_sets.items():
            metadata = policy_set.get("metadata", {})
            
            # Check for exact match
            if (metadata.get("environment_type") == environment_type and
                metadata.get("is_edge") == is_edge and
                metadata.get("region") == region and
                metadata.get("industry") == industry):
                return policy_set_id
        
        # Find best match (prioritize industry and region)
        best_match = None
        best_score = -1
        
        for policy_set_id, policy_set in policy_sets.items():
            metadata = policy_set.get("metadata", {})
            score = 0
            
            if metadata.get("industry") == industry:
                score += 3
            
            if metadata.get("region") == region:
                score += 2
            
            if metadata.get("environment_type") == environment_type:
                score += 1
            
            if metadata.get("is_edge") == is_edge:
                score += 1
            
            if score > best_score:
                best_score = score
                best_match = policy_set_id
        
        # Return default if no match found
        if best_match is None:
            return "default"
        
        return best_match
    
    def _detect_policy_changes(self, snapshots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect changes in policy sets between snapshots.
        
        Args:
            snapshots: List of snapshots to compare
            
        Returns:
            List of policy change events
        """
        changes = []
        
        for i in range(1, len(snapshots)):
            prev = snapshots[i-1]
            curr = snapshots[i]
            
            if prev["policy_set_id"] != curr["policy_set_id"]:
                changes.append({
                    "type": "policy_set_change",
                    "timestamp": curr["timestamp"],
                    "previous_policy_set": prev["policy_set_id"],
                    "new_policy_set": curr["policy_set_id"]
                })
        
        return changes
    
    def _detect_compliance_changes(self, snapshots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect changes in compliance status between snapshots.
        
        Args:
            snapshots: List of snapshots to compare
            
        Returns:
            List of compliance change events
        """
        changes = []
        
        for i in range(1, len(snapshots)):
            prev = snapshots[i-1]
            curr = snapshots[i]
            
            if prev["compliant"] != curr["compliant"]:
                changes.append({
                    "type": "compliance_status_change",
                    "timestamp": curr["timestamp"],
                    "previous_status": "compliant" if prev["compliant"] else "non_compliant",
                    "new_status": "compliant" if curr["compliant"] else "non_compliant"
                })
        
        return changes
    
    def _generate_comparison_insights(self, snapshots: List[Dict[str, Any]]) -> List[str]:
        """
        Generate insights from snapshot comparison.
        
        Args:
            snapshots: List of snapshots to compare
            
        Returns:
            List of insight strings
        """
        insights = []
        
        # Check for policy changes
        policy_changes = self._detect_policy_changes(snapshots)
        if policy_changes:
            insights.append(f"Policy set changed {len(policy_changes)} times during the period")
        
        # Check for compliance status changes
        compliance_changes = self._detect_compliance_changes(snapshots)
        if compliance_changes:
            insights.append(f"Compliance status changed {len(compliance_changes)} times during the period")
        
        # Check for consistent compliance
        all_compliant = all(s["compliant"] for s in snapshots)
        if all_compliant:
            insights.append("Deployment maintained compliance throughout the entire period")
        
        # Check for improvement
        first_compliant = snapshots[0]["compliant"]
        last_compliant = snapshots[-1]["compliant"]
        
        if not first_compliant and last_compliant:
            insights.append("Deployment improved from non-compliant to compliant")
        elif first_compliant and not last_compliant:
            insights.append("Deployment regressed from compliant to non-compliant")
        
        return insights
    
    def export_snapshot(self, snapshot_id: str, format: str = "json") -> Dict[str, Any]:
        """
        Export a compliance snapshot in the specified format.
        
        Args:
            snapshot_id: ID of the snapshot to export
            format: Export format (json, pdf, html)
            
        Returns:
            Dictionary with export information
        """
        snapshot = self.get_snapshot(snapshot_id)
        if not snapshot:
            return {
                "success": False,
                "error": f"Snapshot {snapshot_id} not found"
            }
        
        return self.reporter.export_report(snapshot["report"], format)
    
    def cleanup_snapshot_history(self, max_age_days: int = 90) -> int:
        """
        Clean up old snapshot history entries.
        
        Args:
            max_age_days: Maximum age in days to keep snapshots
            
        Returns:
            Number of entries removed
        """
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        to_remove = [
            snapshot_id for snapshot_id, snapshot in self.snapshot_history.items()
            if current_time - snapshot["timestamp"] > max_age_seconds
        ]
        
        for snapshot_id in to_remove:
            del self.snapshot_history[snapshot_id]
        
        logger.info(f"Cleaned up {len(to_remove)} old snapshot history entries")
        return len(to_remove)
