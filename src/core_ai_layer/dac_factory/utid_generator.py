"""
UTID (Universal Traceable Identifier) Generator

This module implements the UTID generation system for creating unique, traceable
identifiers for DAC capsules with blockchain anchoring for immutable provenance.

The UTID Generator is responsible for:
1. Generating unique identifiers for capsules and hypotheses
2. Anchoring UTIDs to blockchain for immutable provenance
3. Creating UTID lineage chains for version tracking
4. Validating UTID format and integrity
5. Resolving UTIDs to capsule metadata

UTID Format: UTID:service:component:hash
Example: UTID:dac-factory:capsule:a1b2c3d4e5f6g7h8

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import json
import re

logger = logging.getLogger(__name__)


class UTIDType(Enum):
    """UTID entity types."""
    HYPOTHESIS = "hypothesis"
    CAPSULE = "capsule"
    DEPLOYMENT = "deployment"
    UPGRADE = "upgrade"
    PROOF = "proof"


class BlockchainNetwork(Enum):
    """Supported blockchain networks."""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    AVALANCHE = "avalanche"
    ARBITRUM = "arbitrum"
    LOCAL = "local"  # For testing


@dataclass
class UTID:
    """
    Universal Traceable Identifier.
    
    Attributes:
        id: Full UTID string
        service: Service name
        component: Component type
        hash: Content hash
        entity_type: Type of entity
        metadata: Additional metadata
        created_at: Creation timestamp
        blockchain_tx: Blockchain transaction hash
        parent_utid: Parent UTID (for lineage)
    """
    id: str
    service: str
    component: str
    hash: str
    entity_type: UTIDType
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    blockchain_tx: Optional[str] = None
    parent_utid: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "service": self.service,
            "component": self.component,
            "hash": self.hash,
            "entity_type": self.entity_type.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "blockchain_tx": self.blockchain_tx,
            "parent_utid": self.parent_utid
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UTID":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            service=data["service"],
            component=data["component"],
            hash=data["hash"],
            entity_type=UTIDType(data["entity_type"]),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            blockchain_tx=data.get("blockchain_tx"),
            parent_utid=data.get("parent_utid")
        )


@dataclass
class BlockchainAnchor:
    """
    Blockchain anchor information.
    
    Attributes:
        network: Blockchain network
        transaction_hash: Transaction hash
        block_number: Block number
        timestamp: Anchor timestamp
        gas_used: Gas used for transaction
        confirmation_count: Number of confirmations
    """
    network: BlockchainNetwork
    transaction_hash: str
    block_number: int
    timestamp: datetime
    gas_used: Optional[int] = None
    confirmation_count: int = 0


@dataclass
class UTIDGeneratorConfig:
    """
    Configuration for UTID Generator.
    
    Attributes:
        service_name: Service name for UTIDs
        blockchain_network: Target blockchain network
        enable_blockchain_anchoring: Enable blockchain anchoring
        confirmation_threshold: Required confirmations for finality
        batch_anchoring: Enable batch anchoring for efficiency
        batch_size: Number of UTIDs per batch
    """
    service_name: str = "dac-factory"
    blockchain_network: BlockchainNetwork = BlockchainNetwork.POLYGON
    enable_blockchain_anchoring: bool = True
    confirmation_threshold: int = 12
    batch_anchoring: bool = False  # Default to immediate anchoring
    batch_size: int = 100


class BlockchainConnector:
    """
    Blockchain connector for UTID anchoring.
    
    This is a simplified connector that simulates blockchain operations.
    In production, this would use actual blockchain clients (web3.py, ethers.js, etc.).
    """
    
    def __init__(self, network: BlockchainNetwork):
        """
        Initialize blockchain connector.
        
        Args:
            network: Target blockchain network
        """
        self.network = network
        self.connected = False
        logger.info(f"Blockchain connector initialized for {network.value}")
    
    async def connect(self) -> bool:
        """
        Connect to blockchain network.
        
        Returns:
            True if connection successful
        """
        # Simulate connection
        await asyncio.sleep(0.1)
        self.connected = True
        logger.info(f"Connected to {self.network.value} blockchain")
        return True
    
    async def anchor_utid(self, utid: str, metadata: Dict[str, Any]) -> BlockchainAnchor:
        """
        Anchor UTID to blockchain.
        
        Args:
            utid: UTID to anchor
            metadata: Additional metadata
        
        Returns:
            Blockchain anchor information
        """
        if not self.connected:
            raise RuntimeError("Blockchain connector not connected")
        
        # Simulate blockchain transaction
        await asyncio.sleep(0.2)
        
        # Generate mock transaction hash
        tx_data = f"{utid}:{json.dumps(metadata)}:{datetime.now().isoformat()}"
        tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
        
        anchor = BlockchainAnchor(
            network=self.network,
            transaction_hash=tx_hash,
            block_number=12345678,  # Mock block number
            timestamp=datetime.now(),
            gas_used=21000,
            confirmation_count=0
        )
        
        logger.info(f"Anchored UTID {utid} to blockchain: {tx_hash[:16]}...")
        return anchor
    
    async def batch_anchor_utids(
        self,
        utids: List[str],
        metadata_list: List[Dict[str, Any]]
    ) -> List[BlockchainAnchor]:
        """
        Anchor multiple UTIDs in a single transaction.
        
        Args:
            utids: List of UTIDs to anchor
            metadata_list: List of metadata for each UTID
        
        Returns:
            List of blockchain anchors
        """
        if not self.connected:
            raise RuntimeError("Blockchain connector not connected")
        
        # Simulate batch transaction
        await asyncio.sleep(0.3)
        
        anchors = []
        for utid, metadata in zip(utids, metadata_list):
            tx_data = f"{utid}:{json.dumps(metadata)}:{datetime.now().isoformat()}"
            tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
            
            anchor = BlockchainAnchor(
                network=self.network,
                transaction_hash=tx_hash,
                block_number=12345678,
                timestamp=datetime.now(),
                gas_used=21000 * len(utids),  # Batch gas
                confirmation_count=0
            )
            anchors.append(anchor)
        
        logger.info(f"Batch anchored {len(utids)} UTIDs to blockchain")
        return anchors
    
    async def verify_anchor(self, transaction_hash: str) -> bool:
        """
        Verify blockchain anchor.
        
        Args:
            transaction_hash: Transaction hash to verify
        
        Returns:
            True if anchor is valid
        """
        if not self.connected:
            raise RuntimeError("Blockchain connector not connected")
        
        # Simulate verification
        await asyncio.sleep(0.1)
        return True


class UTIDGenerator:
    """
    UTID Generator for creating and managing Universal Traceable Identifiers.
    
    This generator creates unique identifiers for capsules and hypotheses,
    anchors them to blockchain for immutable provenance, and manages lineage.
    """
    
    def __init__(self, config: Optional[UTIDGeneratorConfig] = None):
        """
        Initialize UTID Generator.
        
        Args:
            config: Generator configuration
        """
        self.config = config or UTIDGeneratorConfig()
        self.utid_registry: Dict[str, UTID] = {}
        self.pending_anchors: List[UTID] = []
        
        # Initialize blockchain connector
        if self.config.enable_blockchain_anchoring:
            self.blockchain = BlockchainConnector(self.config.blockchain_network)
        else:
            self.blockchain = None
        
        logger.info(f"UTID Generator initialized with config: {self.config}")
    
    async def connect(self) -> bool:
        """
        Connect to blockchain network.
        
        Returns:
            True if connection successful
        """
        if self.blockchain:
            return await self.blockchain.connect()
        return True
    
    def _generate_hash(self, content: str) -> str:
        """
        Generate content hash.
        
        Args:
            content: Content to hash
        
        Returns:
            Hash string (16 characters)
        """
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _format_utid(self, service: str, component: str, content_hash: str) -> str:
        """
        Format UTID string.
        
        Args:
            service: Service name
            component: Component type
            content_hash: Content hash
        
        Returns:
            Formatted UTID string
        """
        return f"UTID:{service}:{component}:{content_hash}"
    
    def _parse_utid(self, utid_string: str) -> Tuple[str, str, str]:
        """
        Parse UTID string.
        
        Args:
            utid_string: UTID string to parse
        
        Returns:
            Tuple of (service, component, hash)
        
        Raises:
            ValueError: If UTID format is invalid
        """
        pattern = r"^UTID:([a-z0-9-]+):([a-z0-9-]+):([a-z0-9]{16})$"
        match = re.match(pattern, utid_string)
        
        if not match:
            raise ValueError(f"Invalid UTID format: {utid_string}")
        
        return match.group(1), match.group(2), match.group(3)
    
    async def generate_utid(
        self,
        entity_type: UTIDType,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        parent_utid: Optional[str] = None
    ) -> UTID:
        """
        Generate a new UTID.
        
        Args:
            entity_type: Type of entity
            content: Content to generate UTID for
            metadata: Additional metadata
            parent_utid: Parent UTID (for lineage)
        
        Returns:
            Generated UTID
        """
        # Generate content hash
        content_hash = self._generate_hash(content)
        
        # Format UTID
        utid_string = self._format_utid(
            self.config.service_name,
            entity_type.value,
            content_hash
        )
        
        # Create UTID object
        utid = UTID(
            id=utid_string,
            service=self.config.service_name,
            component=entity_type.value,
            hash=content_hash,
            entity_type=entity_type,
            metadata=metadata or {},
            parent_utid=parent_utid
        )
        
        # Store in registry
        self.utid_registry[utid_string] = utid
        
        # Add to pending anchors if blockchain anchoring is enabled
        if self.config.enable_blockchain_anchoring:
            self.pending_anchors.append(utid)
            
            # Anchor immediately if batch anchoring is disabled, or if batch is full
            if not self.config.batch_anchoring:
                await self._anchor_pending_utids()
            elif len(self.pending_anchors) >= self.config.batch_size:
                await self._anchor_pending_utids()
        
        logger.info(f"Generated UTID: {utid_string}")
        return utid
    
    async def _anchor_pending_utids(self):
        """Anchor pending UTIDs to blockchain."""
        if not self.pending_anchors:
            return
        
        if not self.blockchain or not self.blockchain.connected:
            await self.connect()
        
        if self.config.batch_anchoring:
            # Batch anchor
            utid_strings = [utid.id for utid in self.pending_anchors]
            metadata_list = [utid.metadata for utid in self.pending_anchors]
            
            anchors = await self.blockchain.batch_anchor_utids(utid_strings, metadata_list)
            
            for utid, anchor in zip(self.pending_anchors, anchors):
                utid.blockchain_tx = anchor.transaction_hash
        else:
            # Individual anchoring
            for utid in self.pending_anchors:
                anchor = await self.blockchain.anchor_utid(utid.id, utid.metadata)
                utid.blockchain_tx = anchor.transaction_hash
        
        # Clear pending anchors
        self.pending_anchors.clear()
    
    async def anchor_utid(self, utid_string: str) -> Optional[str]:
        """
        Manually anchor a UTID to blockchain.
        
        Args:
            utid_string: UTID to anchor
        
        Returns:
            Blockchain transaction hash or None if not found
        """
        utid = self.utid_registry.get(utid_string)
        if not utid:
            logger.warning(f"UTID not found: {utid_string}")
            return None
        
        if not self.blockchain:
            logger.warning("Blockchain anchoring not enabled")
            return None
        
        if not self.blockchain.connected:
            await self.connect()
        
        anchor = await self.blockchain.anchor_utid(utid.id, utid.metadata)
        utid.blockchain_tx = anchor.transaction_hash
        
        return anchor.transaction_hash
    
    def validate_utid(self, utid_string: str) -> bool:
        """
        Validate UTID format.
        
        Args:
            utid_string: UTID to validate
        
        Returns:
            True if valid
        """
        try:
            self._parse_utid(utid_string)
            return True
        except ValueError:
            return False
    
    def resolve_utid(self, utid_string: str) -> Optional[UTID]:
        """
        Resolve UTID to get metadata.
        
        Args:
            utid_string: UTID to resolve
        
        Returns:
            UTID object or None if not found
        """
        return self.utid_registry.get(utid_string)
    
    def get_utid_lineage(self, utid_string: str) -> List[UTID]:
        """
        Get UTID lineage chain.
        
        Args:
            utid_string: UTID to get lineage for
        
        Returns:
            List of UTIDs in lineage (from root to current)
        """
        lineage = []
        current_utid = self.resolve_utid(utid_string)
        
        while current_utid:
            lineage.insert(0, current_utid)
            
            if current_utid.parent_utid:
                current_utid = self.resolve_utid(current_utid.parent_utid)
            else:
                break
        
        return lineage
    
    def get_utid_children(self, utid_string: str) -> List[UTID]:
        """
        Get child UTIDs.
        
        Args:
            utid_string: Parent UTID
        
        Returns:
            List of child UTIDs
        """
        children = []
        
        for utid in self.utid_registry.values():
            if utid.parent_utid == utid_string:
                children.append(utid)
        
        return children
    
    def get_utids_by_type(self, entity_type: UTIDType) -> List[UTID]:
        """
        Get all UTIDs of a specific type.
        
        Args:
            entity_type: Entity type to filter by
        
        Returns:
            List of UTIDs
        """
        return [
            utid for utid in self.utid_registry.values()
            if utid.entity_type == entity_type
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get UTID generation statistics.
        
        Returns:
            Statistics dictionary
        """
        total = len(self.utid_registry)
        by_type = {}
        anchored = 0
        
        for utid in self.utid_registry.values():
            # Count by type
            type_name = utid.entity_type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1
            
            # Count anchored
            if utid.blockchain_tx:
                anchored += 1
        
        return {
            "total_utids": total,
            "by_type": by_type,
            "anchored": anchored,
            "pending_anchors": len(self.pending_anchors),
            "anchor_percentage": (anchored / total * 100) if total > 0 else 0
        }


# Example usage
async def main():
    """Example usage of UTID Generator."""
    # Create generator
    generator = UTIDGenerator()
    await generator.connect()
    
    # Generate UTID for hypothesis
    print("\nGenerating UTID for hypothesis...")
    hypothesis_utid = await generator.generate_utid(
        entity_type=UTIDType.HYPOTHESIS,
        content="Optimize turbine blade geometry using topology optimization",
        metadata={"domain": "aerospace", "confidence": 0.85}
    )
    print(f"  UTID: {hypothesis_utid.id}")
    print(f"  Blockchain TX: {hypothesis_utid.blockchain_tx[:16]}...")
    
    # Generate UTID for capsule (with parent)
    print("\nGenerating UTID for capsule...")
    capsule_utid = await generator.generate_utid(
        entity_type=UTIDType.CAPSULE,
        content="aerospace-capsule-v1.0.0",
        metadata={"version": "1.0.0", "replicas": 2},
        parent_utid=hypothesis_utid.id
    )
    print(f"  UTID: {capsule_utid.id}")
    print(f"  Parent: {capsule_utid.parent_utid}")
    print(f"  Blockchain TX: {capsule_utid.blockchain_tx[:16]}...")
    
    # Validate UTID
    print("\nValidating UTID...")
    is_valid = generator.validate_utid(capsule_utid.id)
    print(f"  Valid: {is_valid}")
    
    # Resolve UTID
    print("\nResolving UTID...")
    resolved = generator.resolve_utid(capsule_utid.id)
    if resolved:
        print(f"  Service: {resolved.service}")
        print(f"  Component: {resolved.component}")
        print(f"  Metadata: {resolved.metadata}")
    
    # Get lineage
    print("\nGetting UTID lineage...")
    lineage = generator.get_utid_lineage(capsule_utid.id)
    for i, utid in enumerate(lineage):
        print(f"  {i + 1}. {utid.id} ({utid.entity_type.value})")
    
    # Get statistics
    print("\nUTID Statistics:")
    stats = generator.get_statistics()
    print(f"  Total UTIDs: {stats['total_utids']}")
    print(f"  By type: {stats['by_type']}")
    print(f"  Anchored: {stats['anchored']} ({stats['anchor_percentage']:.1f}%)")


if __name__ == "__main__":
    asyncio.run(main())
