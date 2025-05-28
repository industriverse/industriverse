"""
Trust Score Initializer

This module initializes trust scores for capsules and components in a deployment.
It establishes the initial trust baseline that will be monitored and updated
throughout the deployment lifecycle.
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class TrustScoreInitializer:
    """
    Initializer for trust scores in deployments.
    """
    
    def __init__(self, score_policies_path: Optional[str] = None):
        """
        Initialize the Trust Score Initializer.
        
        Args:
            score_policies_path: Path to score policies file
        """
        self.score_policies_path = score_policies_path or os.environ.get(
            "TRUST_SCORE_POLICIES_PATH", "/var/lib/industriverse/trust/score_policies.json"
        )
        self.score_policies = self._load_score_policies()
        logger.info("Trust Score Initializer initialized")
    
    def initialize_scores(self, 
                         deployment_manifest: Dict[str, Any], 
                         context: Dict[str, Any],
                         zones: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initialize trust scores for a deployment.
        
        Args:
            deployment_manifest: Deployment manifest
            context: Deployment context
            zones: Trust zones configuration
            
        Returns:
            Dict containing initialized scores
        """
        logger.info(f"Initializing trust scores for deployment: {deployment_manifest.get('name', 'unnamed')}")
        
        try:
            # Initialize scores for each component in the deployment
            component_scores = {}
            
            # Get components from manifest
            components = deployment_manifest.get("components", {})
            
            for component_name, component_config in components.items():
                # Calculate initial score for component
                component_score = self._calculate_initial_score(
                    component_name, component_config, deployment_manifest, context, zones
                )
                
                component_scores[component_name] = component_score
            
            # Calculate overall deployment score
            deployment_score = self._calculate_deployment_score(component_scores, deployment_manifest, context)
            
            # Prepare result
            scores = {
                "deployment": deployment_score,
                "components": component_scores,
                "timestamp": self._get_timestamp()
            }
            
            return {
                "success": True,
                "scores": scores
            }
            
        except Exception as e:
            logger.exception(f"Error initializing trust scores: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_component_score(self, 
                              component_name: str, 
                              current_score: Dict[str, Any],
                              event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update trust score for a component based on an event.
        
        Args:
            component_name: Name of the component
            current_score: Current trust score data
            event_data: Event data affecting the score
            
        Returns:
            Dict containing updated score
        """
        logger.info(f"Updating trust score for component: {component_name}")
        
        try:
            # Get base score
            base_score = current_score.get("score", 100)
            
            # Apply event impact
            event_type = event_data.get("type", "unknown")
            event_severity = event_data.get("severity", "low")
            
            # Get score adjustment based on event type and severity
            adjustment = self._get_score_adjustment(event_type, event_severity)
            
            # Calculate new score
            new_score = max(0, min(100, base_score + adjustment))
            
            # Prepare updated score data
            updated_score = dict(current_score)
            updated_score.update({
                "score": new_score,
                "previous_score": base_score,
                "last_updated": self._get_timestamp(),
                "last_event": {
                    "type": event_type,
                    "severity": event_severity,
                    "adjustment": adjustment,
                    "timestamp": self._get_timestamp()
                }
            })
            
            # Add event to history
            if "history" not in updated_score:
                updated_score["history"] = []
            
            updated_score["history"].append({
                "type": event_type,
                "severity": event_severity,
                "adjustment": adjustment,
                "previous_score": base_score,
                "new_score": new_score,
                "timestamp": self._get_timestamp()
            })
            
            # Trim history if too long
            if len(updated_score["history"]) > 100:
                updated_score["history"] = updated_score["history"][-100:]
            
            return {
                "success": True,
                "component_name": component_name,
                "updated_score": updated_score
            }
            
        except Exception as e:
            logger.exception(f"Error updating trust score: {str(e)}")
            return {
                "success": False,
                "component_name": component_name,
                "error": str(e)
            }
    
    def _load_score_policies(self) -> Dict[str, Any]:
        """
        Load trust score policies from file.
        
        Returns:
            Dict containing score policies
        """
        try:
            if os.path.exists(self.score_policies_path):
                with open(self.score_policies_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Score policies file not found: {self.score_policies_path}")
                return self._get_default_score_policies()
                
        except Exception as e:
            logger.exception(f"Error loading score policies: {str(e)}")
            return self._get_default_score_policies()
    
    def _get_default_score_policies(self) -> Dict[str, Any]:
        """
        Get default trust score policies.
        
        Returns:
            Dict containing default score policies
        """
        return {
            "base_scores": {
                "default": 80,
                "public": 70,
                "dmz": 75,
                "internal": 85,
                "secure": 90
            },
            "factors": {
                "verified_source": 10,
                "signed_code": 5,
                "vulnerability_scan": 5,
                "compliance_check": 5,
                "security_review": 10
            },
            "penalties": {
                "unverified_source": -15,
                "unsigned_code": -10,
                "failed_vulnerability_scan": -20,
                "failed_compliance_check": -15,
                "missing_security_review": -10
            },
            "event_adjustments": {
                "security_patch": {
                    "low": 2,
                    "medium": 5,
                    "high": 10
                },
                "vulnerability_found": {
                    "low": -5,
                    "medium": -15,
                    "high": -30
                },
                "authentication_failure": {
                    "low": -5,
                    "medium": -10,
                    "high": -20
                },
                "authorization_failure": {
                    "low": -5,
                    "medium": -10,
                    "high": -20
                },
                "anomalous_behavior": {
                    "low": -5,
                    "medium": -15,
                    "high": -25
                }
            }
        }
    
    def _calculate_initial_score(self, 
                               component_name: str,
                               component_config: Dict[str, Any],
                               deployment_manifest: Dict[str, Any],
                               context: Dict[str, Any],
                               zones: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate initial trust score for a component.
        
        Args:
            component_name: Name of the component
            component_config: Component configuration
            deployment_manifest: Deployment manifest
            context: Deployment context
            zones: Trust zones configuration
            
        Returns:
            Dict containing component trust score
        """
        # Determine component's trust zone
        component_zone = component_config.get("trust_zone", "internal")
        
        # Get base score for zone
        base_score = self.score_policies["base_scores"].get(
            component_zone, self.score_policies["base_scores"]["default"]
        )
        
        # Apply factors and penalties
        score_adjustments = []
        
        # Check for verified source
        if component_config.get("verified_source", False):
            adjustment = self.score_policies["factors"]["verified_source"]
            score_adjustments.append(("verified_source", adjustment))
        else:
            adjustment = self.score_policies["penalties"]["unverified_source"]
            score_adjustments.append(("unverified_source", adjustment))
        
        # Check for signed code
        if component_config.get("signed_code", False):
            adjustment = self.score_policies["factors"]["signed_code"]
            score_adjustments.append(("signed_code", adjustment))
        else:
            adjustment = self.score_policies["penalties"]["unsigned_code"]
            score_adjustments.append(("unsigned_code", adjustment))
        
        # Check for vulnerability scan
        if component_config.get("vulnerability_scan", False):
            adjustment = self.score_policies["factors"]["vulnerability_scan"]
            score_adjustments.append(("vulnerability_scan", adjustment))
        else:
            adjustment = self.score_policies["penalties"]["failed_vulnerability_scan"]
            score_adjustments.append(("failed_vulnerability_scan", adjustment))
        
        # Check for compliance check
        if component_config.get("compliance_check", False):
            adjustment = self.score_policies["factors"]["compliance_check"]
            score_adjustments.append(("compliance_check", adjustment))
        else:
            adjustment = self.score_policies["penalties"]["failed_compliance_check"]
            score_adjustments.append(("failed_compliance_check", adjustment))
        
        # Check for security review
        if component_config.get("security_review", False):
            adjustment = self.score_policies["factors"]["security_review"]
            score_adjustments.append(("security_review", adjustment))
        else:
            adjustment = self.score_policies["penalties"]["missing_security_review"]
            score_adjustments.append(("missing_security_review", adjustment))
        
        # Calculate final score
        final_score = base_score
        for factor, adjustment in score_adjustments:
            final_score += adjustment
        
        # Ensure score is within valid range
        final_score = max(0, min(100, final_score))
        
        return {
            "score": final_score,
            "base_score": base_score,
            "zone": component_zone,
            "adjustments": score_adjustments,
            "last_updated": self._get_timestamp(),
            "history": []
        }
    
    def _calculate_deployment_score(self, 
                                  component_scores: Dict[str, Dict[str, Any]],
                                  deployment_manifest: Dict[str, Any],
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate overall trust score for a deployment.
        
        Args:
            component_scores: Trust scores for components
            deployment_manifest: Deployment manifest
            context: Deployment context
            
        Returns:
            Dict containing deployment trust score
        """
        # Calculate weighted average of component scores
        if not component_scores:
            # No components, use default score
            return {
                "score": 80,
                "components_count": 0,
                "last_updated": self._get_timestamp()
            }
        
        # Get component weights
        components = deployment_manifest.get("components", {})
        total_weight = 0
        weighted_sum = 0
        
        for component_name, score_data in component_scores.items():
            # Get component weight (default to 1)
            weight = components.get(component_name, {}).get("trust_weight", 1)
            total_weight += weight
            weighted_sum += score_data["score"] * weight
        
        # Calculate weighted average
        average_score = weighted_sum / total_weight if total_weight > 0 else 80
        
        return {
            "score": average_score,
            "components_count": len(component_scores),
            "last_updated": self._get_timestamp()
        }
    
    def _get_score_adjustment(self, event_type: str, event_severity: str) -> int:
        """
        Get score adjustment for an event.
        
        Args:
            event_type: Type of event
            event_severity: Severity of event
            
        Returns:
            Score adjustment value
        """
        # Get adjustment from policies
        if event_type in self.score_policies["event_adjustments"]:
            return self.score_policies["event_adjustments"][event_type].get(event_severity, 0)
        
        # Default adjustment
        if event_severity == "high":
            return -20
        elif event_severity == "medium":
            return -10
        elif event_severity == "low":
            return -5
        else:
            return 0
    
    def _get_timestamp(self):
        """Get the current timestamp."""
        import datetime
        return datetime.datetime.utcnow().isoformat()
