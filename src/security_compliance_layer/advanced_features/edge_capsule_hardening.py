"""
Edge Capsule Hardening with PQC Runtime for the Security & Compliance Layer

This module extends PQC runtime to BitNet edge capsules, including local zone compliance
caching for offline validation. It ensures quantum-resistant security at the edge.

Key features:
1. PQC runtime for edge capsules
2. Local zone compliance caching
3. Offline validation capabilities
4. Resource-optimized cryptographic operations
5. Edge-specific security policies

Dependencies:
- core.identity_trust.identity_provider
- core.data_security.data_security_system
- advanced_features.quantum_ready_crypto_zone
- advanced_features.trust_score_crypto_modifier

Author: Industriverse Security Team
"""

import logging
import json
import yaml
import os
import time
import uuid
import hashlib
import base64
from typing import Dict, List, Optional, Tuple, Union, Any
from enum import Enum
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

class EdgeDeviceType(Enum):
    """Enumeration of edge device types"""
    BITNET_NODE = "bitnet_node"  # BitNet node
    INDUSTRIAL_CONTROLLER = "industrial_controller"  # Industrial controller
    SENSOR_GATEWAY = "sensor_gateway"  # Sensor gateway
    FIELD_DEVICE = "field_device"  # Field device
    MOBILE_EDGE = "mobile_edge"  # Mobile edge device
    IOT_DEVICE = "iot_device"  # IoT device

class SecurityLevel(Enum):
    """Enumeration of security levels"""
    STANDARD = "standard"  # Standard security level
    ENHANCED = "enhanced"  # Enhanced security level
    HIGH = "high"  # High security level
    CRITICAL = "critical"  # Critical security level

class EdgeCapsuleHardening:
    """
    Edge Capsule Hardening with PQC Runtime for the Security & Compliance Layer
    
    This class extends PQC runtime to BitNet edge capsules, including local zone compliance
    caching for offline validation. It ensures quantum-resistant security at the edge.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Edge Capsule Hardening
        
        Args:
            config: Configuration dictionary for the Edge Capsule Hardening
        """
        self.config = config or {}
        
        # Default configuration
        self.default_config = {
            "crypto_zone_manifest_path": "/etc/industriverse/security/crypto_zone_manifest.yaml",
            "regional_policy_registry_path": "/etc/industriverse/security/regional_crypto_policy_registry.yaml",
            "cache_dir": "/var/cache/industriverse/edge_capsule",
            "cache_retention_days": 30,
            "offline_validation_enabled": True,
            "resource_optimization_enabled": True,
            "memory_constrained_mode": False,
            "memory_threshold_kb": 1024,
            "sync_interval_hours": 24,
            "compliance_check_interval_hours": 1,
            "max_cached_policies": 10,
            "max_cached_certificates": 100,
            "emergency_mode_enabled": True
        }
        
        # Merge default config with provided config
        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value
        
        # Load crypto zone manifest
        self.crypto_zone_manifest = self._load_crypto_zone_manifest()
        
        # Load regional policy registry
        self.regional_policy_registry = self._load_regional_policy_registry()
        
        # Initialize edge device registry
        self.edge_device_registry = {}  # Maps device_id to device details
        
        # Initialize edge capsule registry
        self.edge_capsule_registry = {}  # Maps capsule_id to capsule details
        
        # Initialize compliance cache
        self.compliance_cache = {}  # Maps cache_key to compliance details
        
        # Initialize certificate cache
        self.certificate_cache = {}  # Maps certificate_id to certificate details
        
        # Dependencies (will be set via dependency injection)
        self.identity_provider = None
        self.data_security_system = None
        self.quantum_ready_crypto_zone = None
        self.trust_score_crypto_modifier = None
        
        logger.info("Edge Capsule Hardening initialized")
    
    def set_dependencies(self, identity_provider=None, data_security_system=None,
                        quantum_ready_crypto_zone=None, trust_score_crypto_modifier=None):
        """
        Set dependencies for the Edge Capsule Hardening
        
        Args:
            identity_provider: Identity Provider instance
            data_security_system: Data Security System instance
            quantum_ready_crypto_zone: Quantum Ready Crypto Zone instance
            trust_score_crypto_modifier: Trust Score Crypto Modifier instance
        """
        self.identity_provider = identity_provider
        self.data_security_system = data_security_system
        self.quantum_ready_crypto_zone = quantum_ready_crypto_zone
        self.trust_score_crypto_modifier = trust_score_crypto_modifier
        logger.info("Edge Capsule Hardening dependencies set")
    
    def _load_crypto_zone_manifest(self) -> Dict[str, Any]:
        """
        Load the crypto zone manifest
        
        Returns:
            Crypto zone manifest
        """
        manifest_path = self.config.get("crypto_zone_manifest_path")
        
        # For development/testing, use a default path if the configured path doesn't exist
        if not os.path.exists(manifest_path):
            manifest_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "advanced_features",
                "crypto_zone_manifest.yaml"
            )
        
        try:
            with open(manifest_path, "r") as f:
                manifest = yaml.safe_load(f)
            logger.info(f"Loaded crypto zone manifest from {manifest_path}")
            return manifest
        except Exception as e:
            logger.error(f"Failed to load crypto zone manifest: {e}")
            # Return a minimal default manifest
            return {
                "crypto_algorithms": {},
                "crypto_zones": {},
                "regional_overrides": {},
                "transition_policy": {},
                "trust_score_modifiers": {
                    "algorithms": {},
                    "practices": {},
                    "compliance": {}
                }
            }
    
    def _load_regional_policy_registry(self) -> Dict[str, Any]:
        """
        Load the regional policy registry
        
        Returns:
            Regional policy registry
        """
        registry_path = self.config.get("regional_policy_registry_path")
        
        # For development/testing, use a default path if the configured path doesn't exist
        if not os.path.exists(registry_path):
            registry_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "advanced_features",
                "regional_crypto_policy_registry.yaml"
            )
        
        try:
            with open(registry_path, "r") as f:
                registry = yaml.safe_load(f)
            logger.info(f"Loaded regional policy registry from {registry_path}")
            return registry
        except Exception as e:
            logger.error(f"Failed to load regional policy registry: {e}")
            # Return a minimal default registry
            return {
                "regional_policies": {},
                "cross_regional_requirements": {},
                "global_policy": {}
            }
    
    def register_edge_device(self, device_id: str, device_type: Union[EdgeDeviceType, str],
                           region: str, capabilities: Dict[str, Any],
                           metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Register an edge device
        
        Args:
            device_id: ID of the device
            device_type: Type of the device
            region: Region of the device
            capabilities: Capabilities of the device
            metadata: Metadata for the device
            
        Returns:
            Device details
        """
        # Convert enum to value
        if isinstance(device_type, EdgeDeviceType):
            device_type = device_type.value
        
        # Create device record
        device_record = {
            "device_id": device_id,
            "device_type": device_type,
            "region": region,
            "capabilities": capabilities,
            "metadata": metadata or {},
            "status": "active",
            "registered_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "last_sync_at": None,
            "security_level": self._determine_device_security_level(device_type, capabilities),
            "pqc_enabled": self._is_pqc_enabled(device_type, capabilities),
            "offline_validation_enabled": self.config.get("offline_validation_enabled"),
            "resource_optimization_enabled": self.config.get("resource_optimization_enabled"),
            "memory_constrained_mode": self._is_memory_constrained(capabilities),
            "emergency_mode_enabled": self.config.get("emergency_mode_enabled"),
            "compliance_status": None,
            "compliance_details": None,
            "assigned_capsules": []
        }
        
        # Add to device registry
        self.edge_device_registry[device_id] = device_record
        
        logger.info(f"Registered edge device {device_id} of type {device_type} in region {region}")
        return device_record
    
    def _determine_device_security_level(self, device_type: str, capabilities: Dict[str, Any]) -> str:
        """
        Determine security level for a device
        
        Args:
            device_type: Type of the device
            capabilities: Capabilities of the device
            
        Returns:
            Security level
        """
        # In a real implementation, this would determine the security level based on device type and capabilities
        # For this implementation, we'll use a simple mapping
        
        if device_type == EdgeDeviceType.BITNET_NODE.value:
            return SecurityLevel.HIGH.value
        elif device_type == EdgeDeviceType.INDUSTRIAL_CONTROLLER.value:
            return SecurityLevel.CRITICAL.value
        elif device_type == EdgeDeviceType.SENSOR_GATEWAY.value:
            return SecurityLevel.ENHANCED.value
        elif device_type == EdgeDeviceType.FIELD_DEVICE.value:
            return SecurityLevel.ENHANCED.value
        elif device_type == EdgeDeviceType.MOBILE_EDGE.value:
            return SecurityLevel.STANDARD.value
        elif device_type == EdgeDeviceType.IOT_DEVICE.value:
            return SecurityLevel.STANDARD.value
        else:
            return SecurityLevel.STANDARD.value
    
    def _is_pqc_enabled(self, device_type: str, capabilities: Dict[str, Any]) -> bool:
        """
        Check if PQC is enabled for a device
        
        Args:
            device_type: Type of the device
            capabilities: Capabilities of the device
            
        Returns:
            True if PQC is enabled, False otherwise
        """
        # In a real implementation, this would check if PQC is enabled based on device type and capabilities
        # For this implementation, we'll use a simple mapping
        
        # Check if device has crypto capabilities
        crypto_capabilities = capabilities.get("crypto", {})
        
        # Check if PQC is explicitly enabled or disabled
        if "pqc_enabled" in crypto_capabilities:
            return crypto_capabilities["pqc_enabled"]
        
        # Check if device has PQC algorithms
        pqc_algorithms = crypto_capabilities.get("pqc_algorithms", [])
        
        if pqc_algorithms:
            return True
        
        # Default based on device type
        if device_type in [
            EdgeDeviceType.BITNET_NODE.value,
            EdgeDeviceType.INDUSTRIAL_CONTROLLER.value,
            EdgeDeviceType.SENSOR_GATEWAY.value
        ]:
            return True
        
        return False
    
    def _is_memory_constrained(self, capabilities: Dict[str, Any]) -> bool:
        """
        Check if device is memory constrained
        
        Args:
            capabilities: Capabilities of the device
            
        Returns:
            True if device is memory constrained, False otherwise
        """
        # In a real implementation, this would check if device is memory constrained based on capabilities
        # For this implementation, we'll use a simple check
        
        # Check if memory constrained mode is forced
        if self.config.get("memory_constrained_mode"):
            return True
        
        # Check if device has memory capabilities
        memory_capabilities = capabilities.get("memory", {})
        
        # Check if memory is explicitly constrained
        if "constrained" in memory_capabilities:
            return memory_capabilities["constrained"]
        
        # Check if device has memory size
        memory_size_kb = memory_capabilities.get("size_kb", 0)
        
        if memory_size_kb > 0:
            # Check if memory size is below threshold
            return memory_size_kb < self.config.get("memory_threshold_kb")
        
        return False
    
    def get_edge_device(self, device_id: str) -> Dict[str, Any]:
        """
        Get edge device details
        
        Args:
            device_id: ID of the device
            
        Returns:
            Device details
        """
        if device_id not in self.edge_device_registry:
            raise ValueError(f"Edge device not found: {device_id}")
        
        return self.edge_device_registry[device_id]
    
    def update_edge_device(self, device_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update edge device
        
        Args:
            device_id: ID of the device
            updates: Updates to apply
            
        Returns:
            Updated device details
        """
        if device_id not in self.edge_device_registry:
            raise ValueError(f"Edge device not found: {device_id}")
        
        device_record = self.edge_device_registry[device_id]
        
        # Apply updates
        for key, value in updates.items():
            if key in ["device_id", "registered_at"]:
                # These fields cannot be updated
                continue
            
            device_record[key] = value
        
        # Update timestamp
        device_record["updated_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Updated edge device {device_id}")
        return device_record
    
    def register_edge_capsule(self, capsule_id: str, capsule_type: str,
                           device_id: str, security_level: Union[SecurityLevel, str],
                           algorithms: Dict[str, str] = None,
                           metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Register an edge capsule
        
        Args:
            capsule_id: ID of the capsule
            capsule_type: Type of the capsule
            device_id: ID of the device
            security_level: Security level of the capsule
            algorithms: Algorithms used by the capsule
            metadata: Metadata for the capsule
            
        Returns:
            Capsule details
        """
        # Check if device exists
        if device_id not in self.edge_device_registry:
            raise ValueError(f"Edge device not found: {device_id}")
        
        # Get device record
        device_record = self.edge_device_registry[device_id]
        
        # Convert enum to value
        if isinstance(security_level, SecurityLevel):
            security_level = security_level.value
        
        # Determine algorithms if not provided
        if algorithms is None:
            algorithms = self._get_algorithms_for_security_level(security_level, device_record["region"])
        
        # Create capsule record
        capsule_record = {
            "capsule_id": capsule_id,
            "capsule_type": capsule_type,
            "device_id": device_id,
            "security_level": security_level,
            "algorithms": algorithms,
            "metadata": metadata or {},
            "status": "active",
            "registered_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "last_sync_at": None,
            "pqc_enabled": self._is_capsule_pqc_enabled(algorithms),
            "offline_validation_enabled": device_record["offline_validation_enabled"],
            "resource_optimization_enabled": device_record["resource_optimization_enabled"],
            "memory_constrained_mode": device_record["memory_constrained_mode"],
            "compliance_status": None,
            "compliance_details": None,
            "trust_score": None
        }
        
        # Add to capsule registry
        self.edge_capsule_registry[capsule_id] = capsule_record
        
        # Add to device's assigned capsules
        if capsule_id not in device_record["assigned_capsules"]:
            device_record["assigned_capsules"].append(capsule_id)
        
        logger.info(f"Registered edge capsule {capsule_id} of type {capsule_type} on device {device_id}")
        return capsule_record
    
    def _get_algorithms_for_security_level(self, security_level: str, region: str) -> Dict[str, str]:
        """
        Get algorithms for a security level
        
        Args:
            security_level: Security level
            region: Region
            
        Returns:
            Dictionary of algorithms
        """
        # In a real implementation, this would get algorithms from the crypto zone manifest and regional policy registry
        # For this implementation, we'll use a simple mapping
        
        # Check if region has a policy
        regional_policies = self.regional_policy_registry.get("regional_policies", {})
        
        if region in regional_policies:
            region_policy = regional_policies[region]
            
            # Check if region has a default policy
            default_policy = region_policy.get("default_policy", {})
            
            if default_policy:
                # Check if security level matches
                if default_policy.get("security_level") == security_level:
                    # Return algorithms from default policy
                    return {
                        "key_encapsulation": default_policy.get("key_encapsulation", "kyber-768"),
                        "signatures": default_policy.get("signatures", "dilithium-3"),
                        "symmetric": default_policy.get("symmetric", "aes-256-gcm"),
                        "hash": default_policy.get("hash", "sha-384")
                    }
        
        # Use global defaults based on security level
        if security_level == SecurityLevel.STANDARD.value:
            return {
                "key_encapsulation": "kyber-512",
                "signatures": "dilithium-2",
                "symmetric": "aes-256-gcm",
                "hash": "sha-256"
            }
        elif security_level == SecurityLevel.ENHANCED.value:
            return {
                "key_encapsulation": "kyber-768",
                "signatures": "dilithium-3",
                "symmetric": "aes-256-gcm",
                "hash": "sha-384"
            }
        elif security_level == SecurityLevel.HIGH.value:
            return {
                "key_encapsulation": "kyber-1024",
                "signatures": "dilithium-5",
                "symmetric": "aes-256-gcm",
                "hash": "sha-512"
            }
        elif security_level == SecurityLevel.CRITICAL.value:
            return {
                "key_encapsulation": "kyber-1024",
                "signatures": "dilithium-5",
                "symmetric": "aes-256-gcm",
                "hash": "sha3-512"
            }
        else:
            # Default to enhanced
            return {
                "key_encapsulation": "kyber-768",
                "signatures": "dilithium-3",
                "symmetric": "aes-256-gcm",
                "hash": "sha-384"
            }
    
    def _is_capsule_pqc_enabled(self, algorithms: Dict[str, str]) -> bool:
        """
        Check if PQC is enabled for a capsule
        
        Args:
            algorithms: Algorithms used by the capsule
            
        Returns:
            True if PQC is enabled, False otherwise
        """
        # Check if key encapsulation is PQC
        key_encapsulation = algorithms.get("key_encapsulation", "")
        
        if key_encapsulation.startswith("kyber-"):
            return True
        
        # Check if signatures is PQC
        signatures = algorithms.get("signatures", "")
        
        if signatures.startswith("dilithium-") or signatures.startswith("falcon-"):
            return True
        
        return False
    
    def get_edge_capsule(self, capsule_id: str) -> Dict[str, Any]:
        """
        Get edge capsule details
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            Capsule details
        """
        if capsule_id not in self.edge_capsule_registry:
            raise ValueError(f"Edge capsule not found: {capsule_id}")
        
        return self.edge_capsule_registry[capsule_id]
    
    def update_edge_capsule(self, capsule_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update edge capsule
        
        Args:
            capsule_id: ID of the capsule
            updates: Updates to apply
            
        Returns:
            Updated capsule details
        """
        if capsule_id not in self.edge_capsule_registry:
            raise ValueError(f"Edge capsule not found: {capsule_id}")
        
        capsule_record = self.edge_capsule_registry[capsule_id]
        
        # Apply updates
        for key, value in updates.items():
            if key in ["capsule_id", "device_id", "registered_at"]:
                # These fields cannot be updated
                continue
            
            capsule_record[key] = value
        
        # Update timestamp
        capsule_record["updated_at"] = datetime.utcnow().isoformat()
        
        # Update PQC enabled status if algorithms were updated
        if "algorithms" in updates:
            capsule_record["pqc_enabled"] = self._is_capsule_pqc_enabled(capsule_record["algorithms"])
        
        logger.info(f"Updated edge capsule {capsule_id}")
        return capsule_record
    
    def get_device_capsules(self, device_id: str) -> List[Dict[str, Any]]:
        """
        Get capsules assigned to a device
        
        Args:
            device_id: ID of the device
            
        Returns:
            List of capsule details
        """
        if device_id not in self.edge_device_registry:
            raise ValueError(f"Edge device not found: {device_id}")
        
        device_record = self.edge_device_registry[device_id]
        
        # Get assigned capsules
        assigned_capsules = device_record["assigned_capsules"]
        
        # Get capsule details
        capsule_details = []
        
        for capsule_id in assigned_capsules:
            if capsule_id in self.edge_capsule_registry:
                capsule_details.append(self.edge_capsule_registry[capsule_id])
        
        return capsule_details
    
    def sync_device(self, device_id: str) -> Dict[str, Any]:
        """
        Sync device with latest policies and certificates
        
        Args:
            device_id: ID of the device
            
        Returns:
            Sync results
        """
        if device_id not in self.edge_device_registry:
            raise ValueError(f"Edge device not found: {device_id}")
        
        device_record = self.edge_device_registry[device_id]
        
        # Initialize sync results
        sync_results = {
            "device_id": device_id,
            "timestamp": datetime.utcnow().isoformat(),
            "policies_synced": 0,
            "certificates_synced": 0,
            "capsules_synced": 0,
            "compliance_checks": 0,
            "compliance_issues": 0
        }
        
        # Sync regional policies
        region = device_record["region"]
        
        # Get regional policy
        regional_policies = self.regional_policy_registry.get("regional_policies", {})
        
        if region in regional_policies:
            region_policy = regional_policies[region]
            
            # Cache regional policy
            cache_key = f"policy:{region}"
            self.compliance_cache[cache_key] = {
                "type": "policy",
                "region": region,
                "policy": region_policy,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            sync_results["policies_synced"] += 1
        
        # Sync global policy
        global_policy = self.regional_policy_registry.get("global_policy", {})
        
        if global_policy:
            # Cache global policy
            cache_key = "policy:global"
            self.compliance_cache[cache_key] = {
                "type": "policy",
                "region": "global",
                "policy": global_policy,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            sync_results["policies_synced"] += 1
        
        # Sync cross-regional requirements
        cross_regional_requirements = self.regional_policy_registry.get("cross_regional_requirements", {})
        
        if cross_regional_requirements:
            # Cache cross-regional requirements
            cache_key = "policy:cross_regional"
            self.compliance_cache[cache_key] = {
                "type": "policy",
                "region": "cross_regional",
                "policy": cross_regional_requirements,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            sync_results["policies_synced"] += 1
        
        # Sync certificates
        # In a real implementation, this would sync certificates from a certificate authority
        # For this implementation, we'll simulate it
        
        # Simulate syncing certificates
        sync_results["certificates_synced"] = 5
        
        # Sync capsules
        device_capsules = self.get_device_capsules(device_id)
        
        for capsule in device_capsules:
            # Check capsule compliance
            compliance_result = self.check_capsule_compliance(capsule["capsule_id"])
            
            sync_results["capsules_synced"] += 1
            sync_results["compliance_checks"] += 1
            
            if not compliance_result["compliant"]:
                sync_results["compliance_issues"] += 1
        
        # Update device record
        device_record["last_sync_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Synced device {device_id}")
        return sync_results
    
    def check_capsule_compliance(self, capsule_id: str) -> Dict[str, Any]:
        """
        Check capsule compliance
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            Compliance result
        """
        if capsule_id not in self.edge_capsule_registry:
            raise ValueError(f"Edge capsule not found: {capsule_id}")
        
        capsule_record = self.edge_capsule_registry[capsule_id]
        
        # Get device record
        device_id = capsule_record["device_id"]
        
        if device_id not in self.edge_device_registry:
            raise ValueError(f"Edge device not found: {device_id}")
        
        device_record = self.edge_device_registry[device_id]
        
        # Initialize compliance result
        compliance_result = {
            "capsule_id": capsule_id,
            "timestamp": datetime.utcnow().isoformat(),
            "compliant": True,
            "issues": [],
            "recommendations": []
        }
        
        # Check if PQC is enabled
        if not capsule_record["pqc_enabled"]:
            # Check if PQC is required
            region = device_record["region"]
            security_level = capsule_record["security_level"]
            
            # Get regional policy
            regional_policies = self.regional_policy_registry.get("regional_policies", {})
            
            if region in regional_policies:
                region_policy = regional_policies[region]
                
                # Check if region has a default policy
                default_policy = region_policy.get("default_policy", {})
                
                if default_policy:
                    # Check if PQC is required
                    if default_policy.get("quantum_resistant_required", False):
                        compliance_result["compliant"] = False
                        compliance_result["issues"].append("PQC is required by regional policy")
                        compliance_result["recommendations"].append("Enable PQC for this capsule")
            
            # Check if security level requires PQC
            if security_level in [SecurityLevel.HIGH.value, SecurityLevel.CRITICAL.value]:
                compliance_result["compliant"] = False
                compliance_result["issues"].append(f"PQC is required for security level {security_level}")
                compliance_result["recommendations"].append("Enable PQC for this capsule")
        
        # Check algorithms
        algorithms = capsule_record["algorithms"]
        
        # Check key encapsulation
        key_encapsulation = algorithms.get("key_encapsulation", "")
        
        if not key_encapsulation:
            compliance_result["compliant"] = False
            compliance_result["issues"].append("Key encapsulation algorithm not specified")
            compliance_result["recommendations"].append("Specify a key encapsulation algorithm")
        elif key_encapsulation.startswith("rsa-") and capsule_record["security_level"] in [SecurityLevel.HIGH.value, SecurityLevel.CRITICAL.value]:
            compliance_result["compliant"] = False
            compliance_result["issues"].append(f"RSA is not recommended for security level {capsule_record['security_level']}")
            compliance_result["recommendations"].append("Use a post-quantum key encapsulation algorithm like Kyber")
        
        # Check signatures
        signatures = algorithms.get("signatures", "")
        
        if not signatures:
            compliance_result["compliant"] = False
            compliance_result["issues"].append("Signature algorithm not specified")
            compliance_result["recommendations"].append("Specify a signature algorithm")
        elif signatures.startswith(("rsa-", "ecdsa-")) and capsule_record["security_level"] in [SecurityLevel.HIGH.value, SecurityLevel.CRITICAL.value]:
            compliance_result["compliant"] = False
            compliance_result["issues"].append(f"RSA/ECDSA is not recommended for security level {capsule_record['security_level']}")
            compliance_result["recommendations"].append("Use a post-quantum signature algorithm like Dilithium")
        
        # Check symmetric
        symmetric = algorithms.get("symmetric", "")
        
        if not symmetric:
            compliance_result["compliant"] = False
            compliance_result["issues"].append("Symmetric algorithm not specified")
            compliance_result["recommendations"].append("Specify a symmetric algorithm")
        elif symmetric == "aes-128-gcm" and capsule_record["security_level"] in [SecurityLevel.HIGH.value, SecurityLevel.CRITICAL.value]:
            compliance_result["compliant"] = False
            compliance_result["issues"].append(f"AES-128 is not recommended for security level {capsule_record['security_level']}")
            compliance_result["recommendations"].append("Use AES-256-GCM")
        
        # Check hash
        hash_algorithm = algorithms.get("hash", "")
        
        if not hash_algorithm:
            compliance_result["compliant"] = False
            compliance_result["issues"].append("Hash algorithm not specified")
            compliance_result["recommendations"].append("Specify a hash algorithm")
        elif hash_algorithm in ["sha-1", "md5"]:
            compliance_result["compliant"] = False
            compliance_result["issues"].append(f"{hash_algorithm} is not recommended")
            compliance_result["recommendations"].append("Use SHA-256 or stronger")
        elif hash_algorithm == "sha-256" and capsule_record["security_level"] in [SecurityLevel.HIGH.value, SecurityLevel.CRITICAL.value]:
            compliance_result["compliant"] = False
            compliance_result["issues"].append(f"SHA-256 is not recommended for security level {capsule_record['security_level']}")
            compliance_result["recommendations"].append("Use SHA-384, SHA-512, or SHA3")
        
        # Update capsule record
        capsule_record["compliance_status"] = compliance_result["compliant"]
        capsule_record["compliance_details"] = {
            "timestamp": compliance_result["timestamp"],
            "issues": compliance_result["issues"],
            "recommendations": compliance_result["recommendations"]
        }
        
        # Calculate trust score
        trust_score = self._calculate_trust_score(capsule_record)
        capsule_record["trust_score"] = trust_score
        
        logger.info(f"Checked compliance for capsule {capsule_id}: {compliance_result['compliant']}")
        return compliance_result
    
    def _calculate_trust_score(self, capsule_record: Dict[str, Any]) -> float:
        """
        Calculate trust score for a capsule
        
        Args:
            capsule_record: Capsule record
            
        Returns:
            Trust score
        """
        # In a real implementation, this would calculate a trust score based on various factors
        # For this implementation, we'll use a simple calculation
        
        # Base score
        base_score = 0.5
        
        # Adjust for PQC
        if capsule_record["pqc_enabled"]:
            base_score += 0.3
        
        # Adjust for compliance
        if capsule_record["compliance_status"]:
            base_score += 0.2
        else:
            # Reduce score based on number of issues
            issues = capsule_record.get("compliance_details", {}).get("issues", [])
            base_score -= 0.05 * len(issues)
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, base_score))
    
    def harden_capsule(self, capsule_id: str) -> Dict[str, Any]:
        """
        Harden a capsule
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            Hardening result
        """
        if capsule_id not in self.edge_capsule_registry:
            raise ValueError(f"Edge capsule not found: {capsule_id}")
        
        capsule_record = self.edge_capsule_registry[capsule_id]
        
        # Check compliance
        compliance_result = self.check_capsule_compliance(capsule_id)
        
        # Initialize hardening result
        hardening_result = {
            "capsule_id": capsule_id,
            "timestamp": datetime.utcnow().isoformat(),
            "hardened": False,
            "actions_taken": [],
            "new_algorithms": None,
            "new_compliance_status": None,
            "new_trust_score": None
        }
        
        # Check if capsule is already compliant
        if compliance_result["compliant"]:
            hardening_result["hardened"] = True
            hardening_result["actions_taken"].append("Capsule already compliant, no hardening needed")
            return hardening_result
        
        # Harden capsule
        algorithms = capsule_record["algorithms"].copy()
        actions_taken = []
        
        # Fix key encapsulation
        key_encapsulation = algorithms.get("key_encapsulation", "")
        
        if not key_encapsulation:
            algorithms["key_encapsulation"] = "kyber-768"
            actions_taken.append("Added Kyber-768 key encapsulation")
        elif key_encapsulation.startswith("rsa-"):
            if capsule_record["security_level"] in [SecurityLevel.HIGH.value, SecurityLevel.CRITICAL.value]:
                algorithms["key_encapsulation"] = "kyber-1024"
                actions_taken.append(f"Upgraded {key_encapsulation} to Kyber-1024")
            else:
                algorithms["key_encapsulation"] = "kyber-768"
                actions_taken.append(f"Upgraded {key_encapsulation} to Kyber-768")
        
        # Fix signatures
        signatures = algorithms.get("signatures", "")
        
        if not signatures:
            algorithms["signatures"] = "dilithium-3"
            actions_taken.append("Added Dilithium-3 signatures")
        elif signatures.startswith(("rsa-", "ecdsa-")):
            if capsule_record["security_level"] in [SecurityLevel.HIGH.value, SecurityLevel.CRITICAL.value]:
                algorithms["signatures"] = "dilithium-5"
                actions_taken.append(f"Upgraded {signatures} to Dilithium-5")
            else:
                algorithms["signatures"] = "dilithium-3"
                actions_taken.append(f"Upgraded {signatures} to Dilithium-3")
        
        # Fix symmetric
        symmetric = algorithms.get("symmetric", "")
        
        if not symmetric:
            algorithms["symmetric"] = "aes-256-gcm"
            actions_taken.append("Added AES-256-GCM symmetric encryption")
        elif symmetric == "aes-128-gcm" and capsule_record["security_level"] in [SecurityLevel.HIGH.value, SecurityLevel.CRITICAL.value]:
            algorithms["symmetric"] = "aes-256-gcm"
            actions_taken.append("Upgraded AES-128-GCM to AES-256-GCM")
        
        # Fix hash
        hash_algorithm = algorithms.get("hash", "")
        
        if not hash_algorithm:
            algorithms["hash"] = "sha-384"
            actions_taken.append("Added SHA-384 hash")
        elif hash_algorithm in ["sha-1", "md5"]:
            algorithms["hash"] = "sha-256"
            actions_taken.append(f"Upgraded {hash_algorithm} to SHA-256")
        elif hash_algorithm == "sha-256" and capsule_record["security_level"] in [SecurityLevel.HIGH.value, SecurityLevel.CRITICAL.value]:
            algorithms["hash"] = "sha-384"
            actions_taken.append("Upgraded SHA-256 to SHA-384")
        
        # Update capsule record
        updates = {
            "algorithms": algorithms,
            "pqc_enabled": True
        }
        
        self.update_edge_capsule(capsule_id, updates)
        
        # Check compliance again
        compliance_result = self.check_capsule_compliance(capsule_id)
        
        # Update hardening result
        hardening_result["hardened"] = compliance_result["compliant"]
        hardening_result["actions_taken"] = actions_taken
        hardening_result["new_algorithms"] = algorithms
        hardening_result["new_compliance_status"] = compliance_result["compliant"]
        hardening_result["new_trust_score"] = capsule_record["trust_score"]
        
        logger.info(f"Hardened capsule {capsule_id}: {hardening_result['hardened']}")
        return hardening_result
    
    def verify_capsule_offline(self, capsule_id: str) -> Dict[str, Any]:
        """
        Verify capsule offline
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            Verification result
        """
        if capsule_id not in self.edge_capsule_registry:
            raise ValueError(f"Edge capsule not found: {capsule_id}")
        
        capsule_record = self.edge_capsule_registry[capsule_id]
        
        # Check if offline validation is enabled
        if not capsule_record["offline_validation_enabled"]:
            return {
                "capsule_id": capsule_id,
                "timestamp": datetime.utcnow().isoformat(),
                "verified": False,
                "reason": "Offline validation not enabled for this capsule"
            }
        
        # Initialize verification result
        verification_result = {
            "capsule_id": capsule_id,
            "timestamp": datetime.utcnow().isoformat(),
            "verified": False,
            "reason": None,
            "trust_score": capsule_record["trust_score"]
        }
        
        # Check if capsule is compliant
        if capsule_record["compliance_status"] is not None:
            verification_result["verified"] = capsule_record["compliance_status"]
            
            if verification_result["verified"]:
                verification_result["reason"] = "Capsule is compliant"
            else:
                verification_result["reason"] = "Capsule is not compliant"
                
                # Add compliance details
                verification_result["compliance_details"] = capsule_record["compliance_details"]
        else:
            # Check compliance
            compliance_result = self.check_capsule_compliance(capsule_id)
            
            verification_result["verified"] = compliance_result["compliant"]
            
            if verification_result["verified"]:
                verification_result["reason"] = "Capsule is compliant"
            else:
                verification_result["reason"] = "Capsule is not compliant"
                
                # Add compliance details
                verification_result["compliance_details"] = {
                    "issues": compliance_result["issues"],
                    "recommendations": compliance_result["recommendations"]
                }
        
        logger.info(f"Verified capsule {capsule_id} offline: {verification_result['verified']}")
        return verification_result
    
    def optimize_capsule_resources(self, capsule_id: str) -> Dict[str, Any]:
        """
        Optimize capsule resources
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            Optimization result
        """
        if capsule_id not in self.edge_capsule_registry:
            raise ValueError(f"Edge capsule not found: {capsule_id}")
        
        capsule_record = self.edge_capsule_registry[capsule_id]
        
        # Check if resource optimization is enabled
        if not capsule_record["resource_optimization_enabled"]:
            return {
                "capsule_id": capsule_id,
                "timestamp": datetime.utcnow().isoformat(),
                "optimized": False,
                "reason": "Resource optimization not enabled for this capsule"
            }
        
        # Initialize optimization result
        optimization_result = {
            "capsule_id": capsule_id,
            "timestamp": datetime.utcnow().isoformat(),
            "optimized": False,
            "actions_taken": [],
            "new_algorithms": None,
            "memory_savings_kb": 0,
            "performance_improvement_percent": 0
        }
        
        # Check if capsule is memory constrained
        if capsule_record["memory_constrained_mode"]:
            # Optimize for memory constrained devices
            algorithms = capsule_record["algorithms"].copy()
            actions_taken = []
            memory_savings_kb = 0
            performance_improvement_percent = 0
            
            # Optimize key encapsulation
            key_encapsulation = algorithms.get("key_encapsulation", "")
            
            if key_encapsulation == "kyber-1024":
                algorithms["key_encapsulation"] = "kyber-768"
                actions_taken.append("Downgraded Kyber-1024 to Kyber-768")
                memory_savings_kb += 64
                performance_improvement_percent += 10
            elif key_encapsulation == "kyber-768" and capsule_record["security_level"] == SecurityLevel.STANDARD.value:
                algorithms["key_encapsulation"] = "kyber-512"
                actions_taken.append("Downgraded Kyber-768 to Kyber-512")
                memory_savings_kb += 64
                performance_improvement_percent += 10
            
            # Optimize signatures
            signatures = algorithms.get("signatures", "")
            
            if signatures == "dilithium-5":
                algorithms["signatures"] = "dilithium-3"
                actions_taken.append("Downgraded Dilithium-5 to Dilithium-3")
                memory_savings_kb += 96
                performance_improvement_percent += 15
            elif signatures == "dilithium-3" and capsule_record["security_level"] == SecurityLevel.STANDARD.value:
                algorithms["signatures"] = "dilithium-2"
                actions_taken.append("Downgraded Dilithium-3 to Dilithium-2")
                memory_savings_kb += 64
                performance_improvement_percent += 10
            
            # Optimize hash
            hash_algorithm = algorithms.get("hash", "")
            
            if hash_algorithm == "sha3-512":
                algorithms["hash"] = "sha3-384"
                actions_taken.append("Downgraded SHA3-512 to SHA3-384")
                memory_savings_kb += 16
                performance_improvement_percent += 5
            elif hash_algorithm == "sha-512":
                algorithms["hash"] = "sha-384"
                actions_taken.append("Downgraded SHA-512 to SHA-384")
                memory_savings_kb += 16
                performance_improvement_percent += 5
            
            # Update capsule record if optimizations were made
            if actions_taken:
                updates = {
                    "algorithms": algorithms
                }
                
                self.update_edge_capsule(capsule_id, updates)
                
                # Check compliance
                self.check_capsule_compliance(capsule_id)
                
                # Update optimization result
                optimization_result["optimized"] = True
                optimization_result["actions_taken"] = actions_taken
                optimization_result["new_algorithms"] = algorithms
                optimization_result["memory_savings_kb"] = memory_savings_kb
                optimization_result["performance_improvement_percent"] = performance_improvement_percent
            else:
                optimization_result["optimized"] = False
                optimization_result["reason"] = "No optimizations available for this capsule"
        else:
            optimization_result["optimized"] = False
            optimization_result["reason"] = "Capsule is not memory constrained"
        
        logger.info(f"Optimized capsule {capsule_id} resources: {optimization_result['optimized']}")
        return optimization_result
    
    def handle_emergency_mode(self, device_id: str, emergency_type: str) -> Dict[str, Any]:
        """
        Handle emergency mode for a device
        
        Args:
            device_id: ID of the device
            emergency_type: Type of emergency
            
        Returns:
            Emergency mode result
        """
        if device_id not in self.edge_device_registry:
            raise ValueError(f"Edge device not found: {device_id}")
        
        device_record = self.edge_device_registry[device_id]
        
        # Check if emergency mode is enabled
        if not device_record["emergency_mode_enabled"]:
            return {
                "device_id": device_id,
                "timestamp": datetime.utcnow().isoformat(),
                "emergency_mode_activated": False,
                "reason": "Emergency mode not enabled for this device"
            }
        
        # Initialize emergency mode result
        emergency_mode_result = {
            "device_id": device_id,
            "timestamp": datetime.utcnow().isoformat(),
            "emergency_mode_activated": True,
            "emergency_type": emergency_type,
            "actions_taken": [],
            "capsules_affected": 0
        }
        
        # Get device capsules
        device_capsules = self.get_device_capsules(device_id)
        
        # Handle emergency based on type
        if emergency_type == "quantum_breakthrough":
            # Upgrade all capsules to highest security level
            for capsule in device_capsules:
                # Get highest security algorithms
                algorithms = {
                    "key_encapsulation": "kyber-1024",
                    "signatures": "dilithium-5",
                    "symmetric": "aes-256-gcm",
                    "hash": "sha3-512"
                }
                
                # Update capsule
                updates = {
                    "security_level": SecurityLevel.CRITICAL.value,
                    "algorithms": algorithms,
                    "pqc_enabled": True
                }
                
                self.update_edge_capsule(capsule["capsule_id"], updates)
                
                emergency_mode_result["capsules_affected"] += 1
            
            emergency_mode_result["actions_taken"].append("Upgraded all capsules to highest security level")
        elif emergency_type == "network_breach":
            # Isolate capsules and enforce strict validation
            for capsule in device_capsules:
                # Update capsule
                updates = {
                    "status": "isolated",
                    "offline_validation_enabled": True
                }
                
                self.update_edge_capsule(capsule["capsule_id"], updates)
                
                emergency_mode_result["capsules_affected"] += 1
            
            emergency_mode_result["actions_taken"].append("Isolated all capsules and enforced strict validation")
        elif emergency_type == "compliance_violation":
            # Check and harden all capsules
            for capsule in device_capsules:
                # Harden capsule
                hardening_result = self.harden_capsule(capsule["capsule_id"])
                
                if hardening_result["hardened"]:
                    emergency_mode_result["capsules_affected"] += 1
            
            emergency_mode_result["actions_taken"].append("Checked and hardened all capsules")
        else:
            # Unknown emergency type
            emergency_mode_result["emergency_mode_activated"] = False
            emergency_mode_result["reason"] = f"Unknown emergency type: {emergency_type}"
        
        logger.info(f"Handled emergency mode for device {device_id}: {emergency_type}")
        return emergency_mode_result
    
    def get_device_compliance_summary(self, device_id: str) -> Dict[str, Any]:
        """
        Get compliance summary for a device
        
        Args:
            device_id: ID of the device
            
        Returns:
            Compliance summary
        """
        if device_id not in self.edge_device_registry:
            raise ValueError(f"Edge device not found: {device_id}")
        
        # Get device capsules
        device_capsules = self.get_device_capsules(device_id)
        
        # Initialize compliance summary
        compliance_summary = {
            "device_id": device_id,
            "timestamp": datetime.utcnow().isoformat(),
            "total_capsules": len(device_capsules),
            "compliant_capsules": 0,
            "non_compliant_capsules": 0,
            "pqc_enabled_capsules": 0,
            "average_trust_score": 0.0,
            "security_level_distribution": {
                SecurityLevel.STANDARD.value: 0,
                SecurityLevel.ENHANCED.value: 0,
                SecurityLevel.HIGH.value: 0,
                SecurityLevel.CRITICAL.value: 0
            },
            "compliance_issues": []
        }
        
        # Calculate compliance summary
        total_trust_score = 0.0
        
        for capsule in device_capsules:
            # Check if capsule is compliant
            if capsule["compliance_status"]:
                compliance_summary["compliant_capsules"] += 1
            else:
                compliance_summary["non_compliant_capsules"] += 1
                
                # Add compliance issues
                if capsule["compliance_details"] and "issues" in capsule["compliance_details"]:
                    compliance_summary["compliance_issues"].extend(capsule["compliance_details"]["issues"])
            
            # Check if PQC is enabled
            if capsule["pqc_enabled"]:
                compliance_summary["pqc_enabled_capsules"] += 1
            
            # Add to security level distribution
            security_level = capsule["security_level"]
            
            if security_level in compliance_summary["security_level_distribution"]:
                compliance_summary["security_level_distribution"][security_level] += 1
            
            # Add to total trust score
            if capsule["trust_score"] is not None:
                total_trust_score += capsule["trust_score"]
        
        # Calculate average trust score
        if compliance_summary["total_capsules"] > 0:
            compliance_summary["average_trust_score"] = total_trust_score / compliance_summary["total_capsules"]
        
        # Remove duplicate compliance issues
        compliance_summary["compliance_issues"] = list(set(compliance_summary["compliance_issues"]))
        
        logger.info(f"Generated compliance summary for device {device_id}")
        return compliance_summary
"""
