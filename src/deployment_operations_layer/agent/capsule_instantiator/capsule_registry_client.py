"""
Capsule Registry Client

This module provides a client for interacting with the Capsule Registry.
It handles registration, querying, and management of capsules in the registry.
"""

import logging
import requests
import json
import os
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class CapsuleRegistryClient:
    """
    Client for interacting with the Capsule Registry.
    """
    
    def __init__(self, registry_url: Optional[str] = None):
        """
        Initialize the Capsule Registry Client.
        
        Args:
            registry_url: URL of the capsule registry service
        """
        self.registry_url = registry_url or os.environ.get(
            "CAPSULE_REGISTRY_URL", "http://capsule-registry.industriverse-system.svc.cluster.local"
        )
        logger.info(f"Capsule Registry Client initialized with URL: {self.registry_url}")
    
    def register_capsule(self, capsule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a capsule with the registry.
        
        Args:
            capsule: Capsule to register
            
        Returns:
            Registration result
        """
        capsule_id = capsule.get("metadata", {}).get("id")
        capsule_name = capsule.get("name", "unnamed")
        
        logger.info(f"Registering capsule {capsule_name} with ID {capsule_id}")
        
        try:
            # In a real implementation, this would make an API call to the registry
            # For now, simulate a successful registration
            
            # Extract lineage information for tracking
            lineage = capsule.get("metadata", {}).get("lineage", {})
            
            # Record registration in registry
            result = {
                "success": True,
                "capsule_id": capsule_id,
                "timestamp": self._get_timestamp(),
                "registry_entry": {
                    "id": capsule_id,
                    "name": capsule_name,
                    "type": capsule.get("type", "generic"),
                    "version": capsule.get("version", "1.0.0"),
                    "status": "registered",
                    "lineage": lineage,
                    "trust_score": capsule.get("security", {}).get("trust_score", 100),
                    "crypto_zone": capsule.get("security", {}).get("crypto_zone", "default"),
                    "trust_zone": capsule.get("security", {}).get("trust_zone", "default"),
                    "protocols": {
                        "mcp": capsule.get("protocols", {}).get("mcp", {}).get("enabled", True),
                        "a2a": capsule.get("protocols", {}).get("a2a", {}).get("enabled", True)
                    }
                }
            }
            
            logger.info(f"Capsule {capsule_name} registered successfully")
            return result
            
        except Exception as e:
            logger.exception(f"Error registering capsule {capsule_name}: {str(e)}")
            return {
                "success": False,
                "capsule_id": capsule_id,
                "error": str(e)
            }
    
    def get_capsule(self, capsule_id: str) -> Dict[str, Any]:
        """
        Get a capsule from the registry.
        
        Args:
            capsule_id: ID of the capsule to retrieve
            
        Returns:
            Capsule data or error
        """
        logger.info(f"Getting capsule with ID {capsule_id}")
        
        try:
            # In a real implementation, this would make an API call to the registry
            # For now, return a simulated response
            return {
                "success": True,
                "capsule": {
                    "metadata": {
                        "id": capsule_id,
                        "status": "active"
                    },
                    "name": f"Capsule-{capsule_id[:8]}",
                    "type": "generic",
                    "version": "1.0.0"
                }
            }
            
        except Exception as e:
            logger.exception(f"Error getting capsule {capsule_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_capsule_status(self, capsule_id: str, status: str) -> Dict[str, Any]:
        """
        Update the status of a capsule in the registry.
        
        Args:
            capsule_id: ID of the capsule to update
            status: New status
            
        Returns:
            Update result
        """
        logger.info(f"Updating capsule {capsule_id} status to {status}")
        
        try:
            # In a real implementation, this would make an API call to the registry
            # For now, return a simulated response
            return {
                "success": True,
                "capsule_id": capsule_id,
                "status": status,
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            logger.exception(f"Error updating capsule {capsule_id} status: {str(e)}")
            return {
                "success": False,
                "capsule_id": capsule_id,
                "error": str(e)
            }
    
    def update_capsule_trust_score(self, capsule_id: str, trust_score: int) -> Dict[str, Any]:
        """
        Update the trust score of a capsule in the registry.
        
        Args:
            capsule_id: ID of the capsule to update
            trust_score: New trust score
            
        Returns:
            Update result
        """
        logger.info(f"Updating capsule {capsule_id} trust score to {trust_score}")
        
        try:
            # In a real implementation, this would make an API call to the registry
            # For now, return a simulated response
            return {
                "success": True,
                "capsule_id": capsule_id,
                "trust_score": trust_score,
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            logger.exception(f"Error updating capsule {capsule_id} trust score: {str(e)}")
            return {
                "success": False,
                "capsule_id": capsule_id,
                "error": str(e)
            }
    
    def record_capsule_mutation(self, 
                              capsule_id: str, 
                              mutation_type: str, 
                              mutation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record a mutation event for a capsule in the registry.
        
        Args:
            capsule_id: ID of the capsule
            mutation_type: Type of mutation
            mutation_data: Data about the mutation
            
        Returns:
            Recording result
        """
        logger.info(f"Recording {mutation_type} mutation for capsule {capsule_id}")
        
        try:
            # In a real implementation, this would make an API call to the registry
            # For now, return a simulated response
            return {
                "success": True,
                "capsule_id": capsule_id,
                "mutation_type": mutation_type,
                "mutation_id": self._generate_id(),
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            logger.exception(f"Error recording mutation for capsule {capsule_id}: {str(e)}")
            return {
                "success": False,
                "capsule_id": capsule_id,
                "error": str(e)
            }
    
    def get_capsule_lineage(self, capsule_id: str) -> Dict[str, Any]:
        """
        Get the lineage of a capsule from the registry.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            Lineage data or error
        """
        logger.info(f"Getting lineage for capsule {capsule_id}")
        
        try:
            # In a real implementation, this would make an API call to the registry
            # For now, return a simulated response
            return {
                "success": True,
                "capsule_id": capsule_id,
                "lineage": {
                    "parent_blueprint": f"blueprint-{self._generate_id()[:8]}",
                    "parent_version": "1.0.0",
                    "creation_timestamp": self._get_timestamp(),
                    "mutations": [
                        {
                            "mutation_id": self._generate_id(),
                            "mutation_type": "configuration_update",
                            "timestamp": self._get_timestamp()
                        }
                    ]
                }
            }
            
        except Exception as e:
            logger.exception(f"Error getting lineage for capsule {capsule_id}: {str(e)}")
            return {
                "success": False,
                "capsule_id": capsule_id,
                "error": str(e)
            }
    
    def search_capsules(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for capsules in the registry.
        
        Args:
            query: Search query
            
        Returns:
            Search results
        """
        logger.info(f"Searching capsules with query: {query}")
        
        try:
            # In a real implementation, this would make an API call to the registry
            # For now, return a simulated response
            return {
                "success": True,
                "results": [
                    {
                        "id": self._generate_id(),
                        "name": "Sample Capsule 1",
                        "type": "generic",
                        "version": "1.0.0",
                        "status": "active"
                    },
                    {
                        "id": self._generate_id(),
                        "name": "Sample Capsule 2",
                        "type": "generic",
                        "version": "1.0.0",
                        "status": "active"
                    }
                ],
                "total": 2,
                "page": 1,
                "page_size": 10
            }
            
        except Exception as e:
            logger.exception(f"Error searching capsules: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_timestamp(self):
        """Get the current timestamp."""
        import datetime
        return datetime.datetime.utcnow().isoformat()
    
    def _generate_id(self):
        """Generate a unique ID."""
        import uuid
        return str(uuid.uuid4())
