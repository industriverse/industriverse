"""
Blockchain Anchoring Integration for the Security & Compliance Layer

This module implements blockchain anchoring for PQC-compliance proof per override,
mutation, or trust-based decision. It provides immutable verification of cryptographic
decisions and compliance status.

Key features:
1. Blockchain anchoring of cryptographic decisions
2. Immutable proof of PQC-compliance
3. Override certificates with blockchain verification
4. Trust-based decision anchoring
5. Mutation tracking with blockchain receipts

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

class AnchorType(Enum):
    """Enumeration of anchor types"""
    PQC_COMPLIANCE = "pqc_compliance"  # PQC compliance anchor
    OVERRIDE_CERTIFICATE = "override_certificate"  # Override certificate anchor
    TRUST_DECISION = "trust_decision"  # Trust-based decision anchor
    MUTATION_RECORD = "mutation_record"  # Capsule mutation record anchor
    KEY_ROTATION = "key_rotation"  # Key rotation record anchor
    COMPLIANCE_VERIFICATION = "compliance_verification"  # Compliance verification anchor

class BlockchainType(Enum):
    """Enumeration of blockchain types"""
    ETHEREUM = "ethereum"  # Ethereum blockchain
    QUORUM = "quorum"  # Quorum blockchain (enterprise Ethereum)
    CORDA = "corda"  # Corda blockchain (enterprise DLT)
    HYPERLEDGER = "hyperledger"  # Hyperledger Fabric blockchain
    POLYGON = "polygon"  # Polygon blockchain (Ethereum L2)

class BlockchainAnchoringIntegration:
    """
    Blockchain Anchoring Integration for the Security & Compliance Layer
    
    This class implements blockchain anchoring for PQC-compliance proof per override,
    mutation, or trust-based decision. It provides immutable verification of cryptographic
    decisions and compliance status.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Blockchain Anchoring Integration
        
        Args:
            config: Configuration dictionary for the Blockchain Anchoring Integration
        """
        self.config = config or {}
        
        # Default configuration
        self.default_config = {
            "blockchain_type": BlockchainType.QUORUM.value,
            "blockchain_endpoint": "https://quorum.industriverse.io",
            "blockchain_api_key": None,
            "contract_address": "0x1234567890123456789012345678901234567890",
            "gas_limit": 300000,
            "gas_price": 0,  # For private blockchains
            "confirmation_blocks": 2,
            "retry_attempts": 3,
            "retry_delay_seconds": 5,
            "batch_size": 10,
            "batch_interval_seconds": 60,
            "enable_local_caching": True,
            "cache_dir": "/var/cache/industriverse/blockchain",
            "anchor_retention_days": 365
        }
        
        # Merge default config with provided config
        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value
        
        # Initialize anchor registry
        self.anchor_registry = {}  # Maps anchor_id to anchor details
        
        # Initialize anchor batch
        self.anchor_batch = []  # List of anchors to be batched
        self.last_batch_time = datetime.utcnow()
        
        # Initialize blockchain client
        self.blockchain_client = self._initialize_blockchain_client()
        
        # Dependencies (will be set via dependency injection)
        self.identity_provider = None
        self.data_security_system = None
        self.quantum_ready_crypto_zone = None
        self.trust_score_crypto_modifier = None
        
        logger.info("Blockchain Anchoring Integration initialized")
    
    def set_dependencies(self, identity_provider=None, data_security_system=None,
                        quantum_ready_crypto_zone=None, trust_score_crypto_modifier=None):
        """
        Set dependencies for the Blockchain Anchoring Integration
        
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
        logger.info("Blockchain Anchoring Integration dependencies set")
    
    def _initialize_blockchain_client(self) -> Any:
        """
        Initialize blockchain client
        
        Returns:
            Blockchain client
        """
        # In a real implementation, this would initialize a blockchain client
        # For this implementation, we'll simulate it
        
        blockchain_type = self.config.get("blockchain_type")
        
        logger.info(f"Initialized blockchain client for {blockchain_type}")
        return {"type": blockchain_type}
    
    def create_anchor(self, entity_id: str, entity_type: str,
                    anchor_type: Union[AnchorType, str],
                    data: Dict[str, Any], metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a blockchain anchor
        
        Args:
            entity_id: ID of the entity (agent, capsule, layer, etc.)
            entity_type: Type of the entity
            anchor_type: Type of anchor
            data: Data to anchor
            metadata: Metadata for the anchor
            
        Returns:
            Anchor details
        """
        # Convert enum to value
        if isinstance(anchor_type, AnchorType):
            anchor_type = anchor_type.value
        
        # Create anchor ID
        anchor_id = str(uuid.uuid4())
        
        # Create anchor record
        anchor_record = {
            "anchor_id": anchor_id,
            "entity_id": entity_id,
            "entity_type": entity_type,
            "anchor_type": anchor_type,
            "data": data,
            "metadata": metadata or {},
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "anchored_at": None,
            "blockchain_type": self.config.get("blockchain_type"),
            "transaction_hash": None,
            "block_number": None,
            "block_timestamp": None,
            "merkle_proof": None,
            "verification_url": None,
            "error": None
        }
        
        # Add to anchor registry
        self.anchor_registry[anchor_id] = anchor_record
        
        # Add to anchor batch
        self.anchor_batch.append(anchor_id)
        
        # Check if batch should be processed
        self._check_batch_processing()
        
        logger.info(f"Created anchor {anchor_id} for {entity_type} {entity_id} with type {anchor_type}")
        return anchor_record
    
    def _check_batch_processing(self):
        """
        Check if anchor batch should be processed
        """
        current_time = datetime.utcnow()
        batch_interval = timedelta(seconds=self.config.get("batch_interval_seconds"))
        
        # Process batch if it's full or if batch interval has elapsed
        if (len(self.anchor_batch) >= self.config.get("batch_size") or
            current_time - self.last_batch_time >= batch_interval):
            self._process_anchor_batch()
    
    def _process_anchor_batch(self):
        """
        Process anchor batch
        """
        if not self.anchor_batch:
            return
        
        # Get anchors to process
        anchor_ids = self.anchor_batch.copy()
        self.anchor_batch = []
        
        # Update last batch time
        self.last_batch_time = datetime.utcnow()
        
        # Process anchors
        try:
            self._anchor_to_blockchain(anchor_ids)
            
            logger.info(f"Processed anchor batch with {len(anchor_ids)} anchors")
        except Exception as e:
            # Return anchors to batch
            self.anchor_batch.extend(anchor_ids)
            
            logger.error(f"Failed to process anchor batch: {e}")
    
    def _anchor_to_blockchain(self, anchor_ids: List[str]):
        """
        Anchor data to blockchain
        
        Args:
            anchor_ids: List of anchor IDs to anchor
        """
        # In a real implementation, this would anchor data to blockchain
        # For this implementation, we'll simulate it
        
        # Prepare batch data
        batch_data = []
        
        for anchor_id in anchor_ids:
            anchor_record = self.anchor_registry[anchor_id]
            
            # Create anchor data
            anchor_data = {
                "anchor_id": anchor_id,
                "entity_id": anchor_record["entity_id"],
                "entity_type": anchor_record["entity_type"],
                "anchor_type": anchor_record["anchor_type"],
                "data_hash": self._hash_data(anchor_record["data"]),
                "metadata_hash": self._hash_data(anchor_record["metadata"]),
                "timestamp": anchor_record["created_at"]
            }
            
            batch_data.append(anchor_data)
        
        # Create batch hash
        batch_hash = self._hash_data(batch_data)
        
        # Simulate blockchain transaction
        transaction_hash = f"0x{uuid.uuid4().hex}"
        block_number = int(time.time())
        block_timestamp = datetime.utcnow().isoformat()
        
        # Create Merkle tree and proofs
        merkle_tree = self._create_merkle_tree(batch_data)
        
        # Update anchor records
        for i, anchor_id in enumerate(anchor_ids):
            anchor_record = self.anchor_registry[anchor_id]
            
            # Update anchor record
            anchor_record["status"] = "anchored"
            anchor_record["updated_at"] = datetime.utcnow().isoformat()
            anchor_record["anchored_at"] = datetime.utcnow().isoformat()
            anchor_record["transaction_hash"] = transaction_hash
            anchor_record["block_number"] = block_number
            anchor_record["block_timestamp"] = block_timestamp
            anchor_record["merkle_proof"] = merkle_tree["proofs"][i]
            anchor_record["verification_url"] = self._get_verification_url(transaction_hash)
            
            # Cache anchor locally if enabled
            if self.config.get("enable_local_caching"):
                self._cache_anchor_locally(anchor_id, anchor_record)
        
        logger.info(f"Anchored {len(anchor_ids)} anchors to blockchain with transaction {transaction_hash}")
    
    def _hash_data(self, data: Any) -> str:
        """
        Hash data
        
        Args:
            data: Data to hash
            
        Returns:
            Hash of data
        """
        # Convert data to JSON string
        data_str = json.dumps(data, sort_keys=True)
        
        # Hash data
        data_hash = hashlib.sha256(data_str.encode()).hexdigest()
        
        return data_hash
    
    def _create_merkle_tree(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create Merkle tree
        
        Args:
            data: Data to create Merkle tree for
            
        Returns:
            Merkle tree
        """
        # In a real implementation, this would create a Merkle tree
        # For this implementation, we'll simulate it
        
        # Create leaf nodes
        leaves = [self._hash_data(item) for item in data]
        
        # Simulate Merkle root
        merkle_root = self._hash_data(leaves)
        
        # Simulate Merkle proofs
        proofs = []
        
        for i in range(len(leaves)):
            # Simulate proof
            proof = {
                "leaf_index": i,
                "leaf_hash": leaves[i],
                "siblings": [leaves[j] for j in range(len(leaves)) if j != i][:2],  # Take at most 2 siblings
                "root_hash": merkle_root
            }
            
            proofs.append(proof)
        
        return {
            "leaves": leaves,
            "root": merkle_root,
            "proofs": proofs
        }
    
    def _get_verification_url(self, transaction_hash: str) -> str:
        """
        Get verification URL for transaction
        
        Args:
            transaction_hash: Transaction hash
            
        Returns:
            Verification URL
        """
        # In a real implementation, this would return a URL to verify the transaction
        # For this implementation, we'll simulate it
        
        blockchain_type = self.config.get("blockchain_type")
        
        if blockchain_type == BlockchainType.ETHEREUM.value:
            return f"https://etherscan.io/tx/{transaction_hash}"
        elif blockchain_type == BlockchainType.QUORUM.value:
            return f"https://quorum.industriverse.io/tx/{transaction_hash}"
        elif blockchain_type == BlockchainType.CORDA.value:
            return f"https://corda.industriverse.io/tx/{transaction_hash}"
        elif blockchain_type == BlockchainType.HYPERLEDGER.value:
            return f"https://hyperledger.industriverse.io/tx/{transaction_hash}"
        elif blockchain_type == BlockchainType.POLYGON.value:
            return f"https://polygonscan.com/tx/{transaction_hash}"
        else:
            return f"https://industriverse.io/blockchain/tx/{transaction_hash}"
    
    def _cache_anchor_locally(self, anchor_id: str, anchor_record: Dict[str, Any]):
        """
        Cache anchor locally
        
        Args:
            anchor_id: Anchor ID
            anchor_record: Anchor record
        """
        # In a real implementation, this would cache the anchor locally
        # For this implementation, we'll simulate it
        
        cache_dir = self.config.get("cache_dir")
        
        # Ensure cache directory exists
        if not os.path.exists(cache_dir):
            try:
                os.makedirs(cache_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create cache directory: {e}")
                return
        
        # Create cache file path
        cache_file = os.path.join(cache_dir, f"{anchor_id}.json")
        
        # Write anchor record to cache file
        try:
            with open(cache_file, "w") as f:
                json.dump(anchor_record, f, indent=2)
            
            logger.info(f"Cached anchor {anchor_id} locally at {cache_file}")
        except Exception as e:
            logger.error(f"Failed to cache anchor {anchor_id} locally: {e}")
    
    def get_anchor(self, anchor_id: str) -> Dict[str, Any]:
        """
        Get anchor details
        
        Args:
            anchor_id: ID of the anchor
            
        Returns:
            Anchor details
        """
        if anchor_id not in self.anchor_registry:
            # Try to load from cache
            if self.config.get("enable_local_caching"):
                cache_file = os.path.join(self.config.get("cache_dir"), f"{anchor_id}.json")
                
                if os.path.exists(cache_file):
                    try:
                        with open(cache_file, "r") as f:
                            anchor_record = json.load(f)
                        
                        # Add to registry
                        self.anchor_registry[anchor_id] = anchor_record
                        
                        logger.info(f"Loaded anchor {anchor_id} from cache")
                    except Exception as e:
                        logger.error(f"Failed to load anchor {anchor_id} from cache: {e}")
                        raise ValueError(f"Anchor not found: {anchor_id}")
                else:
                    raise ValueError(f"Anchor not found: {anchor_id}")
            else:
                raise ValueError(f"Anchor not found: {anchor_id}")
        
        return self.anchor_registry[anchor_id]
    
    def get_entity_anchors(self, entity_id: str, entity_type: str = None,
                         anchor_type: Union[AnchorType, str] = None) -> List[Dict[str, Any]]:
        """
        Get anchors for an entity
        
        Args:
            entity_id: ID of the entity
            entity_type: Type of the entity
            anchor_type: Type of anchor
            
        Returns:
            List of anchor details
        """
        # Convert enum to value
        if isinstance(anchor_type, AnchorType):
            anchor_type = anchor_type.value
        
        # Filter anchors
        anchors = []
        
        for anchor_id, anchor_record in self.anchor_registry.items():
            if anchor_record["entity_id"] == entity_id:
                if entity_type is None or anchor_record["entity_type"] == entity_type:
                    if anchor_type is None or anchor_record["anchor_type"] == anchor_type:
                        anchors.append(anchor_record)
        
        # Sort by creation time (newest first)
        anchors.sort(key=lambda a: a["created_at"], reverse=True)
        
        return anchors
    
    def verify_anchor(self, anchor_id: str) -> Dict[str, Any]:
        """
        Verify anchor
        
        Args:
            anchor_id: ID of the anchor
            
        Returns:
            Verification result
        """
        # Get anchor record
        anchor_record = self.get_anchor(anchor_id)
        
        # Check if anchor is anchored
        if anchor_record["status"] != "anchored":
            return {
                "anchor_id": anchor_id,
                "verified": False,
                "reason": f"Anchor not anchored, status: {anchor_record['status']}"
            }
        
        # In a real implementation, this would verify the anchor on the blockchain
        # For this implementation, we'll simulate it
        
        # Verify data hash
        data_hash = self._hash_data(anchor_record["data"])
        merkle_proof = anchor_record["merkle_proof"]
        
        if merkle_proof and "leaf_hash" in merkle_proof:
            leaf_hash = merkle_proof["leaf_hash"]
            
            # Check if leaf hash matches data hash
            if leaf_hash != data_hash:
                return {
                    "anchor_id": anchor_id,
                    "verified": False,
                    "reason": "Data hash mismatch"
                }
        
        # Verify Merkle proof
        if merkle_proof and "root_hash" in merkle_proof:
            # In a real implementation, this would verify the Merkle proof
            # For this implementation, we'll assume it's valid
            
            # Simulate verification
            verified = True
            
            if not verified:
                return {
                    "anchor_id": anchor_id,
                    "verified": False,
                    "reason": "Merkle proof verification failed"
                }
        
        # Verify blockchain transaction
        transaction_hash = anchor_record["transaction_hash"]
        
        if transaction_hash:
            # In a real implementation, this would verify the blockchain transaction
            # For this implementation, we'll assume it's valid
            
            # Simulate verification
            verified = True
            
            if not verified:
                return {
                    "anchor_id": anchor_id,
                    "verified": False,
                    "reason": "Blockchain transaction verification failed"
                }
        
        # All verifications passed
        return {
            "anchor_id": anchor_id,
            "verified": True,
            "reason": "Anchor verified"
        }
    
    def create_pqc_compliance_anchor(self, entity_id: str, entity_type: str,
                                  algorithms: Dict[str, str],
                                  compliance_status: bool,
                                  compliance_details: Dict[str, Any] = None,
                                  metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create PQC compliance anchor
        
        Args:
            entity_id: ID of the entity
            entity_type: Type of the entity
            algorithms: Dictionary of algorithms used by the entity
            compliance_status: Compliance status
            compliance_details: Compliance details
            metadata: Metadata for the anchor
            
        Returns:
            Anchor details
        """
        # Create anchor data
        data = {
            "algorithms": algorithms,
            "compliance_status": compliance_status,
            "compliance_details": compliance_details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Create anchor
        anchor_record = self.create_anchor(
            entity_id=entity_id,
            entity_type=entity_type,
            anchor_type=AnchorType.PQC_COMPLIANCE,
            data=data,
            metadata=metadata
        )
        
        logger.info(f"Created PQC compliance anchor {anchor_record['anchor_id']} for {entity_type} {entity_id}")
        return anchor_record
    
    def create_override_certificate_anchor(self, entity_id: str, entity_type: str,
                                        override_type: str,
                                        override_reason: str,
                                        override_details: Dict[str, Any],
                                        approver_id: str = None,
                                        expiration_date: str = None,
                                        metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create override certificate anchor
        
        Args:
            entity_id: ID of the entity
            entity_type: Type of the entity
            override_type: Type of override
            override_reason: Reason for override
            override_details: Override details
            approver_id: ID of the approver
            expiration_date: Expiration date (ISO format)
            metadata: Metadata for the anchor
            
        Returns:
            Anchor details
        """
        # Create anchor data
        data = {
            "override_type": override_type,
            "override_reason": override_reason,
            "override_details": override_details,
            "approver_id": approver_id,
            "expiration_date": expiration_date,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Create anchor
        anchor_record = self.create_anchor(
            entity_id=entity_id,
            entity_type=entity_type,
            anchor_type=AnchorType.OVERRIDE_CERTIFICATE,
            data=data,
            metadata=metadata
        )
        
        logger.info(f"Created override certificate anchor {anchor_record['anchor_id']} for {entity_type} {entity_id}")
        return anchor_record
    
    def create_trust_decision_anchor(self, entity_id: str, entity_type: str,
                                  decision_type: str,
                                  decision_result: bool,
                                  decision_details: Dict[str, Any],
                                  decision_maker_id: str = None,
                                  metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create trust decision anchor
        
        Args:
            entity_id: ID of the entity
            entity_type: Type of the entity
            decision_type: Type of decision
            decision_result: Result of decision
            decision_details: Decision details
            decision_maker_id: ID of the decision maker
            metadata: Metadata for the anchor
            
        Returns:
            Anchor details
        """
        # Create anchor data
        data = {
            "decision_type": decision_type,
            "decision_result": decision_result,
            "decision_details": decision_details,
            "decision_maker_id": decision_maker_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Create anchor
        anchor_record = self.create_anchor(
            entity_id=entity_id,
            entity_type=entity_type,
            anchor_type=AnchorType.TRUST_DECISION,
            data=data,
            metadata=metadata
        )
        
        logger.info(f"Created trust decision anchor {anchor_record['anchor_id']} for {entity_type} {entity_id}")
        return anchor_record
    
    def create_mutation_record_anchor(self, entity_id: str, entity_type: str,
                                   mutation_type: str,
                                   mutation_details: Dict[str, Any],
                                   previous_state: Dict[str, Any],
                                   new_state: Dict[str, Any],
                                   metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create mutation record anchor
        
        Args:
            entity_id: ID of the entity
            entity_type: Type of the entity
            mutation_type: Type of mutation
            mutation_details: Mutation details
            previous_state: Previous state
            new_state: New state
            metadata: Metadata for the anchor
            
        Returns:
            Anchor details
        """
        # Create anchor data
        data = {
            "mutation_type": mutation_type,
            "mutation_details": mutation_details,
            "previous_state": previous_state,
            "new_state": new_state,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Create anchor
        anchor_record = self.create_anchor(
            entity_id=entity_id,
            entity_type=entity_type,
            anchor_type=AnchorType.MUTATION_RECORD,
            data=data,
            metadata=metadata
        )
        
        logger.info(f"Created mutation record anchor {anchor_record['anchor_id']} for {entity_type} {entity_id}")
        return anchor_record
    
    def create_key_rotation_anchor(self, entity_id: str, entity_type: str,
                                rotation_type: str,
                                algorithm_changes: Dict[str, Dict[str, str]],
                                rotation_details: Dict[str, Any] = None,
                                metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create key rotation anchor
        
        Args:
            entity_id: ID of the entity
            entity_type: Type of the entity
            rotation_type: Type of rotation
            algorithm_changes: Algorithm changes
            rotation_details: Rotation details
            metadata: Metadata for the anchor
            
        Returns:
            Anchor details
        """
        # Create anchor data
        data = {
            "rotation_type": rotation_type,
            "algorithm_changes": algorithm_changes,
            "rotation_details": rotation_details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Create anchor
        anchor_record = self.create_anchor(
            entity_id=entity_id,
            entity_type=entity_type,
            anchor_type=AnchorType.KEY_ROTATION,
            data=data,
            metadata=metadata
        )
        
        logger.info(f"Created key rotation anchor {anchor_record['anchor_id']} for {entity_type} {entity_id}")
        return anchor_record
    
    def create_compliance_verification_anchor(self, entity_id: str, entity_type: str,
                                           compliance_type: str,
                                           compliance_status: bool,
                                           compliance_details: Dict[str, Any],
                                           metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create compliance verification anchor
        
        Args:
            entity_id: ID of the entity
            entity_type: Type of the entity
            compliance_type: Type of compliance
            compliance_status: Compliance status
            compliance_details: Compliance details
            metadata: Metadata for the anchor
            
        Returns:
            Anchor details
        """
        # Create anchor data
        data = {
            "compliance_type": compliance_type,
            "compliance_status": compliance_status,
            "compliance_details": compliance_details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Create anchor
        anchor_record = self.create_anchor(
            entity_id=entity_id,
            entity_type=entity_type,
            anchor_type=AnchorType.COMPLIANCE_VERIFICATION,
            data=data,
            metadata=metadata
        )
        
        logger.info(f"Created compliance verification anchor {anchor_record['anchor_id']} for {entity_type} {entity_id}")
        return anchor_record
    
    def get_latest_pqc_compliance_anchor(self, entity_id: str, entity_type: str) -> Optional[Dict[str, Any]]:
        """
        Get latest PQC compliance anchor for an entity
        
        Args:
            entity_id: ID of the entity
            entity_type: Type of the entity
            
        Returns:
            Latest PQC compliance anchor or None if not found
        """
        # Get anchors for entity
        anchors = self.get_entity_anchors(
            entity_id=entity_id,
            entity_type=entity_type,
            anchor_type=AnchorType.PQC_COMPLIANCE
        )
        
        # Return latest anchor if found
        if anchors:
            return anchors[0]
        
        return None
    
    def get_active_override_certificates(self, entity_id: str, entity_type: str) -> List[Dict[str, Any]]:
        """
        Get active override certificates for an entity
        
        Args:
            entity_id: ID of the entity
            entity_type: Type of the entity
            
        Returns:
            List of active override certificates
        """
        # Get anchors for entity
        anchors = self.get_entity_anchors(
            entity_id=entity_id,
            entity_type=entity_type,
            anchor_type=AnchorType.OVERRIDE_CERTIFICATE
        )
        
        # Filter active certificates
        active_certificates = []
        
        for anchor in anchors:
            # Check if certificate is active
            if anchor["status"] == "anchored":
                data = anchor["data"]
                
                # Check expiration date
                expiration_date = data.get("expiration_date")
                
                if expiration_date:
                    try:
                        expiration_datetime = datetime.fromisoformat(expiration_date)
                        
                        # Check if certificate is expired
                        if expiration_datetime < datetime.utcnow():
                            continue
                    except Exception:
                        # Invalid expiration date, consider certificate active
                        pass
                
                active_certificates.append(anchor)
        
        return active_certificates
    
    def get_mutation_history(self, entity_id: str, entity_type: str) -> List[Dict[str, Any]]:
        """
        Get mutation history for an entity
        
        Args:
            entity_id: ID of the entity
            entity_type: Type of the entity
            
        Returns:
            List of mutation records
        """
        # Get anchors for entity
        anchors = self.get_entity_anchors(
            entity_id=entity_id,
            entity_type=entity_type,
            anchor_type=AnchorType.MUTATION_RECORD
        )
        
        return anchors
    
    def get_key_rotation_history(self, entity_id: str, entity_type: str) -> List[Dict[str, Any]]:
        """
        Get key rotation history for an entity
        
        Args:
            entity_id: ID of the entity
            entity_type: Type of the entity
            
        Returns:
            List of key rotation records
        """
        # Get anchors for entity
        anchors = self.get_entity_anchors(
            entity_id=entity_id,
            entity_type=entity_type,
            anchor_type=AnchorType.KEY_ROTATION
        )
        
        return anchors
    
    def get_compliance_verification_history(self, entity_id: str, entity_type: str,
                                         compliance_type: str = None) -> List[Dict[str, Any]]:
        """
        Get compliance verification history for an entity
        
        Args:
            entity_id: ID of the entity
            entity_type: Type of the entity
            compliance_type: Type of compliance
            
        Returns:
            List of compliance verification records
        """
        # Get anchors for entity
        anchors = self.get_entity_anchors(
            entity_id=entity_id,
            entity_type=entity_type,
            anchor_type=AnchorType.COMPLIANCE_VERIFICATION
        )
        
        # Filter by compliance type if provided
        if compliance_type:
            anchors = [
                anchor for anchor in anchors
                if anchor["data"].get("compliance_type") == compliance_type
            ]
        
        return anchors
    
    def process_pending_anchors(self) -> List[Dict[str, Any]]:
        """
        Process pending anchors
        
        Returns:
            List of processed anchor details
        """
        # Process anchor batch
        self._process_anchor_batch()
        
        # Get processed anchors
        processed_anchors = [
            anchor for anchor_id, anchor in self.anchor_registry.items()
            if anchor["status"] == "anchored" and anchor["anchored_at"] is not None
        ]
        
        # Sort by anchored time (newest first)
        processed_anchors.sort(key=lambda a: a["anchored_at"], reverse=True)
        
        return processed_anchors
"""
