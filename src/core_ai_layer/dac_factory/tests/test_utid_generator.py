"""
Unit tests for UTID Generator

Tests cover:
1. UTID generation and formatting
2. UTID validation and parsing
3. Blockchain anchoring (single and batch)
4. UTID lineage tracking
5. UTID resolution and metadata
6. Statistics and monitoring
7. Error handling

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import pytest
import asyncio
from datetime import datetime

from ..utid_generator import (
    UTIDGenerator,
    UTIDGeneratorConfig,
    UTID,
    UTIDType,
    BlockchainNetwork,
    BlockchainConnector,
    BlockchainAnchor
)


class TestUTIDFormatting:
    """Test suite for UTID formatting and parsing."""
    
    def test_utid_format(self):
        """Test UTID format structure."""
        generator = UTIDGenerator()
        
        utid_string = generator._format_utid("dac-factory", "capsule", "a1b2c3d4e5f6g7h8")
        
        assert utid_string == "UTID:dac-factory:capsule:a1b2c3d4e5f6g7h8"
    
    def test_utid_parse_valid(self):
        """Test parsing valid UTID."""
        generator = UTIDGenerator()
        
        service, component, hash_val = generator._parse_utid("UTID:dac-factory:capsule:a1b2c3d4e5f6g7h8")
        
        assert service == "dac-factory"
        assert component == "capsule"
        assert hash_val == "a1b2c3d4e5f6g7h8"
    
    def test_utid_parse_invalid_format(self):
        """Test parsing invalid UTID format."""
        generator = UTIDGenerator()
        
        with pytest.raises(ValueError):
            generator._parse_utid("INVALID:format:here")
    
    def test_utid_parse_invalid_prefix(self):
        """Test parsing UTID with invalid prefix."""
        generator = UTIDGenerator()
        
        with pytest.raises(ValueError):
            generator._parse_utid("NOTUTID:dac-factory:capsule:a1b2c3d4e5f6g7h8")
    
    def test_utid_parse_invalid_hash_length(self):
        """Test parsing UTID with invalid hash length."""
        generator = UTIDGenerator()
        
        with pytest.raises(ValueError):
            generator._parse_utid("UTID:dac-factory:capsule:tooshort")
    
    def test_hash_generation(self):
        """Test content hash generation."""
        generator = UTIDGenerator()
        
        hash1 = generator._generate_hash("test content")
        hash2 = generator._generate_hash("test content")
        hash3 = generator._generate_hash("different content")
        
        assert len(hash1) == 16
        assert hash1 == hash2
        assert hash1 != hash3


class TestBlockchainConnector:
    """Test suite for blockchain connector."""
    
    @pytest.mark.asyncio
    async def test_connector_initialization(self):
        """Test blockchain connector initialization."""
        connector = BlockchainConnector(BlockchainNetwork.POLYGON)
        
        assert connector.network == BlockchainNetwork.POLYGON
        assert not connector.connected
    
    @pytest.mark.asyncio
    async def test_connector_connection(self):
        """Test blockchain connector connection."""
        connector = BlockchainConnector(BlockchainNetwork.POLYGON)
        
        success = await connector.connect()
        
        assert success
        assert connector.connected
    
    @pytest.mark.asyncio
    async def test_anchor_utid(self):
        """Test anchoring single UTID."""
        connector = BlockchainConnector(BlockchainNetwork.POLYGON)
        await connector.connect()
        
        anchor = await connector.anchor_utid(
            "UTID:dac-factory:capsule:a1b2c3d4e5f6g7h8",
            {"version": "1.0.0"}
        )
        
        assert isinstance(anchor, BlockchainAnchor)
        assert anchor.network == BlockchainNetwork.POLYGON
        assert anchor.transaction_hash is not None
        assert len(anchor.transaction_hash) == 64
    
    @pytest.mark.asyncio
    async def test_batch_anchor_utids(self):
        """Test batch anchoring multiple UTIDs."""
        connector = BlockchainConnector(BlockchainNetwork.POLYGON)
        await connector.connect()
        
        utids = [
            "UTID:dac-factory:capsule:a1b2c3d4e5f6g7h8",
            "UTID:dac-factory:capsule:b2c3d4e5f6g7h8i9",
            "UTID:dac-factory:capsule:c3d4e5f6g7h8i9j0"
        ]
        metadata_list = [{"version": "1.0.0"}] * 3
        
        anchors = await connector.batch_anchor_utids(utids, metadata_list)
        
        assert len(anchors) == 3
        assert all(isinstance(a, BlockchainAnchor) for a in anchors)
    
    @pytest.mark.asyncio
    async def test_verify_anchor(self):
        """Test verifying blockchain anchor."""
        connector = BlockchainConnector(BlockchainNetwork.POLYGON)
        await connector.connect()
        
        anchor = await connector.anchor_utid(
            "UTID:dac-factory:capsule:a1b2c3d4e5f6g7h8",
            {}
        )
        
        is_valid = await connector.verify_anchor(anchor.transaction_hash)
        
        assert is_valid
    
    @pytest.mark.asyncio
    async def test_operations_without_connection(self):
        """Test that operations fail without connection."""
        connector = BlockchainConnector(BlockchainNetwork.POLYGON)
        
        with pytest.raises(RuntimeError):
            await connector.anchor_utid("UTID:test:test:1234567890abcdef", {})


class TestUTIDGenerator:
    """Test suite for UTID Generator."""
    
    def test_generator_initialization(self):
        """Test generator initialization with default config."""
        generator = UTIDGenerator()
        
        assert generator.config is not None
        assert generator.config.service_name == "dac-factory"
        assert len(generator.utid_registry) == 0
    
    def test_generator_initialization_custom_config(self):
        """Test generator initialization with custom config."""
        config = UTIDGeneratorConfig(
            service_name="custom-service",
            blockchain_network=BlockchainNetwork.ETHEREUM,
            batch_size=50
        )
        
        generator = UTIDGenerator(config=config)
        
        assert generator.config.service_name == "custom-service"
        assert generator.config.blockchain_network == BlockchainNetwork.ETHEREUM
        assert generator.config.batch_size == 50
    
    @pytest.mark.asyncio
    async def test_generate_utid_hypothesis(self):
        """Test generating UTID for hypothesis."""
        generator = UTIDGenerator()
        await generator.connect()
        
        utid = await generator.generate_utid(
            entity_type=UTIDType.HYPOTHESIS,
            content="Optimize turbine blade geometry",
            metadata={"domain": "aerospace"}
        )
        
        assert isinstance(utid, UTID)
        assert utid.id.startswith("UTID:dac-factory:hypothesis:")
        assert utid.entity_type == UTIDType.HYPOTHESIS
        assert utid.metadata["domain"] == "aerospace"
    
    @pytest.mark.asyncio
    async def test_generate_utid_capsule(self):
        """Test generating UTID for capsule."""
        generator = UTIDGenerator()
        await generator.connect()
        
        utid = await generator.generate_utid(
            entity_type=UTIDType.CAPSULE,
            content="aerospace-capsule-v1.0.0",
            metadata={"version": "1.0.0"}
        )
        
        assert utid.id.startswith("UTID:dac-factory:capsule:")
        assert utid.entity_type == UTIDType.CAPSULE
    
    @pytest.mark.asyncio
    async def test_generate_utid_with_parent(self):
        """Test generating UTID with parent lineage."""
        generator = UTIDGenerator()
        await generator.connect()
        
        parent_utid = await generator.generate_utid(
            entity_type=UTIDType.HYPOTHESIS,
            content="Parent hypothesis"
        )
        
        child_utid = await generator.generate_utid(
            entity_type=UTIDType.CAPSULE,
            content="Child capsule",
            parent_utid=parent_utid.id
        )
        
        assert child_utid.parent_utid == parent_utid.id
    
    @pytest.mark.asyncio
    async def test_utid_blockchain_anchoring(self):
        """Test UTID is anchored to blockchain."""
        generator = UTIDGenerator()
        await generator.connect()
        
        utid = await generator.generate_utid(
            entity_type=UTIDType.CAPSULE,
            content="test capsule"
        )
        
        assert utid.blockchain_tx is not None
        assert len(utid.blockchain_tx) == 64
    
    @pytest.mark.asyncio
    async def test_utid_batch_anchoring(self):
        """Test batch anchoring of UTIDs."""
        config = UTIDGeneratorConfig(batch_size=3, batch_anchoring=True)
        generator = UTIDGenerator(config=config)
        await generator.connect()
        
        # Generate 3 UTIDs to trigger batch
        utids = []
        for i in range(3):
            utid = await generator.generate_utid(
                entity_type=UTIDType.CAPSULE,
                content=f"capsule {i}"
            )
            utids.append(utid)
        
        # All should be anchored
        assert all(utid.blockchain_tx is not None for utid in utids)
    
    @pytest.mark.asyncio
    async def test_manual_anchor_utid(self):
        """Test manually anchoring a UTID."""
        config = UTIDGeneratorConfig(enable_blockchain_anchoring=False)
        generator = UTIDGenerator(config=config)
        generator.blockchain = BlockchainConnector(BlockchainNetwork.POLYGON)
        await generator.connect()
        
        utid = await generator.generate_utid(
            entity_type=UTIDType.CAPSULE,
            content="test capsule"
        )
        
        # Should not be anchored initially
        assert utid.blockchain_tx is None
        
        # Manually anchor
        tx_hash = await generator.anchor_utid(utid.id)
        
        assert tx_hash is not None
        assert utid.blockchain_tx == tx_hash
    
    def test_validate_utid_valid(self):
        """Test validating valid UTID."""
        generator = UTIDGenerator()
        
        is_valid = generator.validate_utid("UTID:dac-factory:capsule:a1b2c3d4e5f6g7h8")
        
        assert is_valid
    
    def test_validate_utid_invalid(self):
        """Test validating invalid UTID."""
        generator = UTIDGenerator()
        
        is_valid = generator.validate_utid("INVALID:format")
        
        assert not is_valid
    
    @pytest.mark.asyncio
    async def test_resolve_utid(self):
        """Test resolving UTID to get metadata."""
        generator = UTIDGenerator()
        await generator.connect()
        
        original_utid = await generator.generate_utid(
            entity_type=UTIDType.CAPSULE,
            content="test capsule",
            metadata={"version": "1.0.0", "domain": "aerospace"}
        )
        
        resolved = generator.resolve_utid(original_utid.id)
        
        assert resolved is not None
        assert resolved.id == original_utid.id
        assert resolved.metadata["version"] == "1.0.0"
        assert resolved.metadata["domain"] == "aerospace"
    
    @pytest.mark.asyncio
    async def test_resolve_utid_not_found(self):
        """Test resolving non-existent UTID."""
        generator = UTIDGenerator()
        
        resolved = generator.resolve_utid("UTID:dac-factory:capsule:nonexistent123")
        
        assert resolved is None
    
    @pytest.mark.asyncio
    async def test_get_utid_lineage(self):
        """Test getting UTID lineage chain."""
        generator = UTIDGenerator()
        await generator.connect()
        
        # Create lineage: hypothesis -> capsule -> deployment
        utid1 = await generator.generate_utid(
            entity_type=UTIDType.HYPOTHESIS,
            content="hypothesis"
        )
        
        utid2 = await generator.generate_utid(
            entity_type=UTIDType.CAPSULE,
            content="capsule",
            parent_utid=utid1.id
        )
        
        utid3 = await generator.generate_utid(
            entity_type=UTIDType.DEPLOYMENT,
            content="deployment",
            parent_utid=utid2.id
        )
        
        lineage = generator.get_utid_lineage(utid3.id)
        
        assert len(lineage) == 3
        assert lineage[0].id == utid1.id
        assert lineage[1].id == utid2.id
        assert lineage[2].id == utid3.id
    
    @pytest.mark.asyncio
    async def test_get_utid_lineage_single(self):
        """Test getting lineage for UTID without parent."""
        generator = UTIDGenerator()
        await generator.connect()
        
        utid = await generator.generate_utid(
            entity_type=UTIDType.HYPOTHESIS,
            content="hypothesis"
        )
        
        lineage = generator.get_utid_lineage(utid.id)
        
        assert len(lineage) == 1
        assert lineage[0].id == utid.id
    
    @pytest.mark.asyncio
    async def test_get_utid_children(self):
        """Test getting child UTIDs."""
        generator = UTIDGenerator()
        await generator.connect()
        
        parent = await generator.generate_utid(
            entity_type=UTIDType.HYPOTHESIS,
            content="parent"
        )
        
        child1 = await generator.generate_utid(
            entity_type=UTIDType.CAPSULE,
            content="child1",
            parent_utid=parent.id
        )
        
        child2 = await generator.generate_utid(
            entity_type=UTIDType.CAPSULE,
            content="child2",
            parent_utid=parent.id
        )
        
        children = generator.get_utid_children(parent.id)
        
        assert len(children) == 2
        assert child1 in children
        assert child2 in children
    
    @pytest.mark.asyncio
    async def test_get_utids_by_type(self):
        """Test getting UTIDs filtered by type."""
        generator = UTIDGenerator()
        await generator.connect()
        
        await generator.generate_utid(UTIDType.HYPOTHESIS, "hyp1")
        await generator.generate_utid(UTIDType.HYPOTHESIS, "hyp2")
        await generator.generate_utid(UTIDType.CAPSULE, "cap1")
        
        hypotheses = generator.get_utids_by_type(UTIDType.HYPOTHESIS)
        capsules = generator.get_utids_by_type(UTIDType.CAPSULE)
        
        assert len(hypotheses) == 2
        assert len(capsules) == 1
    
    @pytest.mark.asyncio
    async def test_get_statistics(self):
        """Test getting UTID statistics."""
        generator = UTIDGenerator()
        await generator.connect()
        
        await generator.generate_utid(UTIDType.HYPOTHESIS, "hyp1")
        await generator.generate_utid(UTIDType.CAPSULE, "cap1")
        await generator.generate_utid(UTIDType.CAPSULE, "cap2")
        
        stats = generator.get_statistics()
        
        assert stats["total_utids"] == 3
        assert stats["by_type"]["hypothesis"] == 1
        assert stats["by_type"]["capsule"] == 2
        assert stats["anchored"] == 3
        assert stats["anchor_percentage"] == 100.0
    
    @pytest.mark.asyncio
    async def test_utid_registry_storage(self):
        """Test that UTIDs are stored in registry."""
        generator = UTIDGenerator()
        await generator.connect()
        
        utid = await generator.generate_utid(
            entity_type=UTIDType.CAPSULE,
            content="test"
        )
        
        assert utid.id in generator.utid_registry
        assert generator.utid_registry[utid.id] == utid
    
    @pytest.mark.asyncio
    async def test_utid_deterministic_hash(self):
        """Test that same content produces same hash."""
        generator = UTIDGenerator()
        await generator.connect()
        
        utid1 = await generator.generate_utid(
            entity_type=UTIDType.CAPSULE,
            content="identical content"
        )
        
        utid2 = await generator.generate_utid(
            entity_type=UTIDType.CAPSULE,
            content="identical content"
        )
        
        # Same content should produce same hash
        assert utid1.hash == utid2.hash
        assert utid1.id == utid2.id


class TestUTIDDataclass:
    """Test suite for UTID dataclass."""
    
    @pytest.mark.asyncio
    async def test_utid_to_dict(self):
        """Test UTID serialization to dictionary."""
        generator = UTIDGenerator()
        await generator.connect()
        
        utid = await generator.generate_utid(
            entity_type=UTIDType.CAPSULE,
            content="test",
            metadata={"version": "1.0.0"}
        )
        
        utid_dict = utid.to_dict()
        
        assert isinstance(utid_dict, dict)
        assert utid_dict["id"] == utid.id
        assert utid_dict["entity_type"] == "capsule"
        assert utid_dict["metadata"]["version"] == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_utid_from_dict(self):
        """Test UTID deserialization from dictionary."""
        data = {
            "id": "UTID:dac-factory:capsule:a1b2c3d4e5f6g7h8",
            "service": "dac-factory",
            "component": "capsule",
            "hash": "a1b2c3d4e5f6g7h8",
            "entity_type": "capsule",
            "metadata": {"version": "1.0.0"},
            "created_at": datetime.now().isoformat(),
            "blockchain_tx": "0x1234567890abcdef",
            "parent_utid": None
        }
        
        utid = UTID.from_dict(data)
        
        assert utid.id == data["id"]
        assert utid.entity_type == UTIDType.CAPSULE
        assert utid.metadata["version"] == "1.0.0"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
