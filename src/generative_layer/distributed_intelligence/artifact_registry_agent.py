"""
Artifact Registry Agent for Industriverse Generative Layer

This module implements the artifact registry agent that manages generated artifacts,
provides zero-knowledge traceability, and supports compliance verification for
regulated sectors like aerospace and defense.
"""

import json
import logging
import time
import hashlib
import uuid
import os
from typing import Dict, Any, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArtifactRegistryAgent:
    """
    Implements artifact registry and traceability for the Generative Layer.
    Provides zero-knowledge proof hashing and compliance verification.
    """
    
    def __init__(self, agent_core=None):
        """
        Initialize the artifact registry agent.
        
        Args:
            agent_core: The agent core instance (optional)
        """
        self.agent_core = agent_core
        self.artifacts = {}
        self.artifact_lineage = {}
        self.compliance_records = {}
        self.zk_proof_registry = {}
        
        # Initialize storage paths
        self.storage_path = os.path.join(os.getcwd(), "artifact_storage")
        os.makedirs(self.storage_path, exist_ok=True)
        
        logger.info("Artifact Registry Agent initialized")
    
    def register_artifact(self, 
                         artifact_type: str, 
                         content: Any, 
                         metadata: Dict[str, Any]) -> str:
        """
        Register a new artifact in the registry.
        
        Args:
            artifact_type: Type of artifact (template, component, documentation, etc.)
            content: The artifact content
            metadata: Additional metadata about the artifact
            
        Returns:
            The artifact ID
        """
        artifact_id = str(uuid.uuid4())
        timestamp = time.time()
        
        # Generate zero-knowledge proof hash
        zk_proof_hash = self._generate_zk_proof(content, metadata)
        
        # Create artifact record
        artifact = {
            "id": artifact_id,
            "type": artifact_type,
            "timestamp": timestamp,
            "metadata": metadata,
            "zk_proof_hash": zk_proof_hash,
            "status": "registered"
        }
        
        # Store artifact
        self.artifacts[artifact_id] = artifact
        
        # Store content
        self._store_artifact_content(artifact_id, content)
        
        # Initialize lineage
        self.artifact_lineage[artifact_id] = {
            "parent_artifacts": metadata.get("parent_artifacts", []),
            "child_artifacts": [],
            "versions": [
                {
                    "version": 1,
                    "timestamp": timestamp,
                    "zk_proof_hash": zk_proof_hash
                }
            ]
        }
        
        # Update parent artifacts' lineage
        for parent_id in metadata.get("parent_artifacts", []):
            if parent_id in self.artifact_lineage:
                self.artifact_lineage[parent_id]["child_artifacts"].append(artifact_id)
        
        logger.info(f"Registered artifact {artifact_id} of type {artifact_type}")
        
        # Emit MCP event for artifact registration
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/artifact/registered",
                {
                    "artifact_id": artifact_id,
                    "artifact_type": artifact_type,
                    "zk_proof_hash": zk_proof_hash
                }
            )
        
        return artifact_id
    
    def update_artifact(self, 
                       artifact_id: str, 
                       content: Any, 
                       metadata: Dict[str, Any]) -> bool:
        """
        Update an existing artifact.
        
        Args:
            artifact_id: The ID of the artifact to update
            content: The new artifact content
            metadata: Updated metadata
            
        Returns:
            True if the update was successful, False otherwise
        """
        if artifact_id not in self.artifacts:
            logger.warning(f"Artifact {artifact_id} not found")
            return False
        
        timestamp = time.time()
        
        # Generate zero-knowledge proof hash
        zk_proof_hash = self._generate_zk_proof(content, metadata)
        
        # Update artifact record
        artifact = self.artifacts[artifact_id]
        artifact["metadata"].update(metadata)
        artifact["zk_proof_hash"] = zk_proof_hash
        artifact["status"] = "updated"
        
        # Store updated content
        self._store_artifact_content(artifact_id, content)
        
        # Update lineage
        lineage = self.artifact_lineage[artifact_id]
        version = len(lineage["versions"]) + 1
        lineage["versions"].append({
            "version": version,
            "timestamp": timestamp,
            "zk_proof_hash": zk_proof_hash
        })
        
        logger.info(f"Updated artifact {artifact_id}")
        
        # Emit MCP event for artifact update
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/artifact/updated",
                {
                    "artifact_id": artifact_id,
                    "version": version,
                    "zk_proof_hash": zk_proof_hash
                }
            )
        
        return True
    
    def get_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an artifact by ID.
        
        Args:
            artifact_id: The ID of the artifact to retrieve
            
        Returns:
            The artifact record, or None if not found
        """
        if artifact_id not in self.artifacts:
            logger.warning(f"Artifact {artifact_id} not found")
            return None
        
        artifact = self.artifacts[artifact_id]
        content = self._load_artifact_content(artifact_id)
        
        return {
            **artifact,
            "content": content
        }
    
    def verify_artifact(self, artifact_id: str, content: Any) -> bool:
        """
        Verify an artifact's integrity using its zero-knowledge proof hash.
        
        Args:
            artifact_id: The ID of the artifact to verify
            content: The content to verify
            
        Returns:
            True if the verification was successful, False otherwise
        """
        if artifact_id not in self.artifacts:
            logger.warning(f"Artifact {artifact_id} not found")
            return False
        
        artifact = self.artifacts[artifact_id]
        expected_hash = artifact["zk_proof_hash"]
        
        # Generate hash from the provided content
        actual_hash = self._generate_zk_proof(content, artifact["metadata"])
        
        # Compare hashes
        is_valid = expected_hash == actual_hash
        
        logger.info(f"Verified artifact {artifact_id}: {'valid' if is_valid else 'invalid'}")
        
        return is_valid
    
    def register_compliance_check(self, 
                                artifact_id: str, 
                                compliance_type: str, 
                                result: bool, 
                                details: Dict[str, Any]) -> str:
        """
        Register a compliance check for an artifact.
        
        Args:
            artifact_id: The ID of the artifact
            compliance_type: Type of compliance check
            result: Result of the compliance check (True=pass, False=fail)
            details: Additional details about the compliance check
            
        Returns:
            The compliance record ID
        """
        if artifact_id not in self.artifacts:
            logger.warning(f"Artifact {artifact_id} not found")
            return ""
        
        compliance_id = str(uuid.uuid4())
        timestamp = time.time()
        
        # Create compliance record
        compliance_record = {
            "id": compliance_id,
            "artifact_id": artifact_id,
            "compliance_type": compliance_type,
            "result": result,
            "details": details,
            "timestamp": timestamp
        }
        
        # Store compliance record
        self.compliance_records[compliance_id] = compliance_record
        
        # Update artifact status if compliance failed
        if not result:
            self.artifacts[artifact_id]["status"] = "compliance_failed"
        
        logger.info(f"Registered compliance check {compliance_id} for artifact {artifact_id}")
        
        # Emit MCP event for compliance check
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/compliance/checked",
                {
                    "compliance_id": compliance_id,
                    "artifact_id": artifact_id,
                    "compliance_type": compliance_type,
                    "result": result
                }
            )
        
        return compliance_id
    
    def get_artifact_lineage(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the lineage of an artifact.
        
        Args:
            artifact_id: The ID of the artifact
            
        Returns:
            The artifact lineage, or None if not found
        """
        if artifact_id not in self.artifact_lineage:
            logger.warning(f"Artifact lineage for {artifact_id} not found")
            return None
        
        return self.artifact_lineage[artifact_id]
    
    def get_artifact_compliance_history(self, artifact_id: str) -> List[Dict[str, Any]]:
        """
        Get the compliance history of an artifact.
        
        Args:
            artifact_id: The ID of the artifact
            
        Returns:
            List of compliance records for the artifact
        """
        if artifact_id not in self.artifacts:
            logger.warning(f"Artifact {artifact_id} not found")
            return []
        
        # Find all compliance records for this artifact
        compliance_history = [
            record for record in self.compliance_records.values()
            if record["artifact_id"] == artifact_id
        ]
        
        # Sort by timestamp
        compliance_history.sort(key=lambda x: x["timestamp"])
        
        return compliance_history
    
    def _generate_zk_proof(self, content: Any, metadata: Dict[str, Any]) -> str:
        """
        Generate a zero-knowledge proof hash for an artifact.
        
        Args:
            content: The artifact content
            metadata: The artifact metadata
            
        Returns:
            The zero-knowledge proof hash
        """
        # Convert content to string if it's not already
        if isinstance(content, dict) or isinstance(content, list):
            content_str = json.dumps(content, sort_keys=True)
        else:
            content_str = str(content)
        
        # Extract relevant metadata for the hash
        relevant_metadata = {
            "type": metadata.get("type", ""),
            "author": metadata.get("author", ""),
            "timestamp": metadata.get("timestamp", time.time()),
            "parent_artifacts": metadata.get("parent_artifacts", [])
        }
        
        metadata_str = json.dumps(relevant_metadata, sort_keys=True)
        
        # Combine content and metadata
        combined = f"{content_str}|{metadata_str}"
        
        # Generate hash
        hash_obj = hashlib.sha256(combined.encode())
        zk_proof_hash = hash_obj.hexdigest()
        
        # Register the hash
        self.zk_proof_registry[zk_proof_hash] = {
            "timestamp": time.time(),
            "metadata_fingerprint": hashlib.sha256(metadata_str.encode()).hexdigest()
        }
        
        return zk_proof_hash
    
    def _store_artifact_content(self, artifact_id: str, content: Any) -> None:
        """
        Store artifact content.
        
        Args:
            artifact_id: The ID of the artifact
            content: The artifact content
        """
        # Create directory for artifact if it doesn't exist
        artifact_dir = os.path.join(self.storage_path, artifact_id)
        os.makedirs(artifact_dir, exist_ok=True)
        
        # Determine file path based on content type
        if isinstance(content, dict) or isinstance(content, list):
            file_path = os.path.join(artifact_dir, "content.json")
            with open(file_path, 'w') as f:
                json.dump(content, f, indent=2)
        else:
            file_path = os.path.join(artifact_dir, "content.txt")
            with open(file_path, 'w') as f:
                f.write(str(content))
    
    def _load_artifact_content(self, artifact_id: str) -> Any:
        """
        Load artifact content.
        
        Args:
            artifact_id: The ID of the artifact
            
        Returns:
            The artifact content
        """
        # Check for JSON content
        json_path = os.path.join(self.storage_path, artifact_id, "content.json")
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                return json.load(f)
        
        # Check for text content
        txt_path = os.path.join(self.storage_path, artifact_id, "content.txt")
        if os.path.exists(txt_path):
            with open(txt_path, 'r') as f:
                return f.read()
        
        logger.warning(f"No content found for artifact {artifact_id}")
        return None
    
    def export_registry(self) -> Dict[str, Any]:
        """
        Export the artifact registry for persistence.
        
        Returns:
            The artifact registry data
        """
        return {
            "artifacts": self.artifacts,
            "artifact_lineage": self.artifact_lineage,
            "compliance_records": self.compliance_records,
            "zk_proof_registry": self.zk_proof_registry
        }
    
    def import_registry(self, registry_data: Dict[str, Any]) -> None:
        """
        Import registry data from persistence.
        
        Args:
            registry_data: The registry data to import
        """
        if "artifacts" in registry_data:
            self.artifacts = registry_data["artifacts"]
        
        if "artifact_lineage" in registry_data:
            self.artifact_lineage = registry_data["artifact_lineage"]
        
        if "compliance_records" in registry_data:
            self.compliance_records = registry_data["compliance_records"]
        
        if "zk_proof_registry" in registry_data:
            self.zk_proof_registry = registry_data["zk_proof_registry"]
        
        logger.info("Imported artifact registry data")
    
    def verify_artifact_chain(self, artifact_id: str) -> Dict[str, Any]:
        """
        Verify the entire lineage chain of an artifact.
        
        Args:
            artifact_id: The ID of the artifact
            
        Returns:
            Verification results for the artifact and its ancestors
        """
        if artifact_id not in self.artifacts:
            logger.warning(f"Artifact {artifact_id} not found")
            return {"valid": False, "error": "Artifact not found"}
        
        results = {
            "valid": True,
            "artifact_id": artifact_id,
            "ancestors": {}
        }
        
        # Verify the artifact itself
        artifact = self.artifacts[artifact_id]
        content = self._load_artifact_content(artifact_id)
        is_valid = self.verify_artifact(artifact_id, content)
        
        if not is_valid:
            results["valid"] = False
            results["error"] = "Artifact verification failed"
            return results
        
        # Verify ancestors
        lineage = self.artifact_lineage[artifact_id]
        for parent_id in lineage["parent_artifacts"]:
            if parent_id in self.artifacts:
                parent_results = self.verify_artifact_chain(parent_id)
                results["ancestors"][parent_id] = parent_results
                
                if not parent_results["valid"]:
                    results["valid"] = False
                    results["error"] = f"Ancestor {parent_id} verification failed"
        
        return results
    
    def generate_compliance_report(self, artifact_id: str) -> Dict[str, Any]:
        """
        Generate a comprehensive compliance report for an artifact.
        
        Args:
            artifact_id: The ID of the artifact
            
        Returns:
            Compliance report for the artifact
        """
        if artifact_id not in self.artifacts:
            logger.warning(f"Artifact {artifact_id} not found")
            return {"error": "Artifact not found"}
        
        artifact = self.artifacts[artifact_id]
        compliance_history = self.get_artifact_compliance_history(artifact_id)
        lineage = self.get_artifact_lineage(artifact_id)
        
        # Check if all compliance checks passed
        all_passed = all(record["result"] for record in compliance_history)
        
        # Group compliance checks by type
        compliance_by_type = {}
        for record in compliance_history:
            compliance_type = record["compliance_type"]
            if compliance_type not in compliance_by_type:
                compliance_by_type[compliance_type] = []
            compliance_by_type[compliance_type].append(record)
        
        # Generate report
        report = {
            "artifact_id": artifact_id,
            "artifact_type": artifact["type"],
            "status": artifact["status"],
            "compliance_summary": {
                "all_passed": all_passed,
                "total_checks": len(compliance_history),
                "passed_checks": sum(1 for record in compliance_history if record["result"]),
                "failed_checks": sum(1 for record in compliance_history if not record["result"])
            },
            "compliance_by_type": compliance_by_type,
            "lineage_summary": {
                "parent_count": len(lineage["parent_artifacts"]),
                "child_count": len(lineage["child_artifacts"]),
                "version_count": len(lineage["versions"])
            },
            "zk_proof_hash": artifact["zk_proof_hash"],
            "timestamp": time.time()
        }
        
        logger.info(f"Generated compliance report for artifact {artifact_id}")
        
        return report
