"""
Capsule Manifest Validator Agent

This module provides a comprehensive agent for validating capsule manifests to ensure they meet
all requirements for deployment. It serves as a critical safeguard against deployment failures
by verifying that capsule manifests are complete, consistent, and compliant with organizational
policies.

The Capsule Manifest Validator Agent orchestrates the validation process, integrating with
other components of the Deployment Operations Layer to ensure that only valid capsules are
deployed to production environments.
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional, Tuple

from .capsule_manifest_validator import CapsuleManifestValidator
from ..agent_utils import AgentBase
from ...protocol.mcp_integration.mcp_context_schema import MCPContextSchema
from ...protocol.a2a_integration.a2a_agent_schema import A2AAgentSchema

logger = logging.getLogger(__name__)

class CapsuleManifestValidatorAgent(AgentBase):
    """
    Agent responsible for validating capsule manifests to ensure they meet all requirements
    for deployment.
    
    This agent serves as a critical safeguard against deployment failures by verifying
    that capsule manifests are complete, consistent, and compliant with organizational
    policies.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Capsule Manifest Validator Agent.
        
        Args:
            config: Configuration dictionary for the agent
        """
        super().__init__(config)
        
        self.agent_id = config.get("agent_id", "capsule-manifest-validator-agent")
        self.agent_name = config.get("agent_name", "Capsule Manifest Validator Agent")
        self.agent_version = config.get("agent_version", "1.0.0")
        
        # Initialize validator
        validator_config = config.get("validator_config", {})
        self.validator = CapsuleManifestValidator(validator_config)
        
        # Initialize validation history
        self.validation_history = []
        
        # MCP/A2A integration
        self.mcp_schema = MCPContextSchema()
        self.a2a_schema = A2AAgentSchema()
        
        logger.info(f"Capsule Manifest Validator Agent initialized: {self.agent_id}")
    
    def validate_manifest(self, manifest: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate a capsule manifest.
        
        Args:
            manifest: Capsule manifest dictionary
            context: Additional context for validation
            
        Returns:
            Validation results dictionary
        """
        logger.info(f"Validating manifest: {manifest.get('manifest_id', 'unknown')}")
        
        # Create validation context
        validation_context = {
            "agent_id": self.agent_id,
            "timestamp": time.time(),
            "context": context or {}
        }
        
        # Perform validation
        validation_results = self.validator.validate_manifest(manifest)
        
        # Enrich validation results with agent information
        validation_results["agent_id"] = self.agent_id
        validation_results["agent_name"] = self.agent_name
        validation_results["agent_version"] = self.agent_version
        validation_results["validation_context"] = validation_context
        
        # Add to validation history
        self.validation_history.append({
            "validation_id": validation_results["validation_id"],
            "timestamp": validation_results["timestamp"],
            "manifest_id": validation_results["manifest_id"],
            "capsule_id": validation_results["capsule_id"],
            "status": validation_results["status"],
            "issue_count": len(validation_results["issues"])
        })
        
        # Generate MCP context
        mcp_context = self._generate_mcp_context(validation_results)
        validation_results["mcp_context"] = mcp_context
        
        # Generate A2A agent card
        a2a_agent_card = self._generate_a2a_agent_card(validation_results)
        validation_results["a2a_agent_card"] = a2a_agent_card
        
        logger.info(f"Manifest validation completed: {validation_results['validation_id']} - Status: {validation_results['status']}")
        
        return validation_results
    
    def generate_validation_report(self, validation_id: str) -> Dict[str, Any]:
        """
        Generate a detailed validation report.
        
        Args:
            validation_id: Validation ID
            
        Returns:
            Validation report dictionary
        """
        logger.info(f"Generating validation report for: {validation_id}")
        
        # Get validation result
        validation_result = self.validator.get_validation_result(validation_id)
        
        if not validation_result:
            logger.error(f"Validation result not found for ID: {validation_id}")
            return {
                "status": "error",
                "message": f"Validation result not found for ID: {validation_id}"
            }
        
        # Generate report
        report = self.validator.generate_validation_report(validation_id)
        
        # Enrich report with agent information
        report["agent_id"] = self.agent_id
        report["agent_name"] = self.agent_name
        report["agent_version"] = self.agent_version
        
        # Generate MCP context
        mcp_context = self._generate_mcp_context(report)
        report["mcp_context"] = mcp_context
        
        # Generate A2A agent card
        a2a_agent_card = self._generate_a2a_agent_card(report)
        report["a2a_agent_card"] = a2a_agent_card
        
        logger.info(f"Validation report generated: {report['report_id']}")
        
        return report
    
    def get_validation_history(self) -> List[Dict[str, Any]]:
        """
        Get validation history.
        
        Returns:
            List of validation history entries
        """
        return self.validation_history
    
    def _generate_mcp_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate MCP context from validation data.
        
        Args:
            data: Validation data
            
        Returns:
            MCP context dictionary
        """
        # Create MCP context
        mcp_context = {
            "context_id": f"mcp-{data.get('validation_id', 'unknown')}",
            "context_type": "manifest_validation",
            "timestamp": time.time(),
            "agent_id": self.agent_id,
            "data": {
                "validation_id": data.get("validation_id", "unknown"),
                "manifest_id": data.get("manifest_id", "unknown"),
                "capsule_id": data.get("capsule_id", "unknown"),
                "status": data.get("status", "unknown"),
                "issue_count": len(data.get("issues", [])),
                "recommendation_count": len(data.get("recommendations", []))
            },
            "metadata": {
                "agent_name": self.agent_name,
                "agent_version": self.agent_version
            }
        }
        
        return mcp_context
    
    def _generate_a2a_agent_card(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate A2A agent card from validation data.
        
        Args:
            data: Validation data
            
        Returns:
            A2A agent card dictionary
        """
        # Create A2A agent card
        a2a_agent_card = {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "agent_version": self.agent_version,
            "agent_type": "validator",
            "capabilities": [
                {
                    "capability_id": "manifest_validation",
                    "capability_name": "Manifest Validation",
                    "capability_description": "Validates capsule manifests to ensure they meet all requirements for deployment"
                },
                {
                    "capability_id": "validation_reporting",
                    "capability_name": "Validation Reporting",
                    "capability_description": "Generates detailed validation reports"
                }
            ],
            "status": {
                "status_code": "active",
                "last_active": time.time(),
                "current_operation": f"Validation of {data.get('manifest_id', 'unknown')}"
            },
            "metadata": {
                "validation_id": data.get("validation_id", "unknown"),
                "manifest_id": data.get("manifest_id", "unknown"),
                "capsule_id": data.get("capsule_id", "unknown"),
                "validation_status": data.get("status", "unknown"),
                "issue_count": len(data.get("issues", [])),
                "industryTags": ["manufacturing", "logistics", "energy", "aerospace", "defense"]
            }
        }
        
        return a2a_agent_card
