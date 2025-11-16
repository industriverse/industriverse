"""
Unit tests for zk-SNARK Proof Generator

Tests cover:
1. Circuit creation and key generation
2. Proof generation with public/private inputs
3. Proof verification
4. Batch proving and verification
5. Circuit and proof retrieval
6. Statistics and monitoring
7. Error handling

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import pytest
import asyncio

from ..proof_generator import (
    ProofGenerator,
    ProofGeneratorConfig,
    Proof,
    Circuit,
    ProofProtocol,
    ProofStatus,
    ProvingKey,
    VerificationKey
)


class TestProofGenerator:
    """Test suite for Proof Generator."""
    
    def test_generator_initialization(self):
        """Test generator initialization with default config."""
        generator = ProofGenerator()
        
        assert generator.config is not None
        assert generator.config.default_protocol == ProofProtocol.GROTH16
        assert len(generator.circuits) == 0
        assert len(generator.proofs) == 0
    
    def test_generator_initialization_custom_config(self):
        """Test generator initialization with custom config."""
        config = ProofGeneratorConfig(
            default_protocol=ProofProtocol.PLONK,
            batch_size=20,
            proof_expiry_hours=48
        )
        
        generator = ProofGenerator(config=config)
        
        assert generator.config.default_protocol == ProofProtocol.PLONK
        assert generator.config.batch_size == 20
        assert generator.config.proof_expiry_hours == 48
    
    @pytest.mark.asyncio
    async def test_create_circuit_groth16(self):
        """Test creating Groth16 circuit."""
        generator = ProofGenerator()
        
        circuit = await generator.create_circuit(
            name="test_circuit",
            description="Test circuit",
            constraints=100,
            public_inputs_count=2,
            private_inputs_count=3,
            protocol=ProofProtocol.GROTH16
        )
        
        assert isinstance(circuit, Circuit)
        assert circuit.name == "test_circuit"
        assert circuit.protocol == ProofProtocol.GROTH16
        assert circuit.constraints == 100
        assert circuit.public_inputs_count == 2
        assert circuit.private_inputs_count == 3
    
    @pytest.mark.asyncio
    async def test_create_circuit_plonk(self):
        """Test creating PLONK circuit."""
        generator = ProofGenerator()
        
        circuit = await generator.create_circuit(
            name="test_circuit",
            description="Test circuit",
            constraints=100,
            public_inputs_count=2,
            private_inputs_count=3,
            protocol=ProofProtocol.PLONK
        )
        
        assert circuit.protocol == ProofProtocol.PLONK
    
    @pytest.mark.asyncio
    async def test_create_circuit_with_metadata(self):
        """Test creating circuit with metadata."""
        generator = ProofGenerator()
        
        circuit = await generator.create_circuit(
            name="test_circuit",
            description="Test circuit",
            constraints=100,
            public_inputs_count=2,
            private_inputs_count=3,
            metadata={"domain": "aerospace", "version": "1.0"}
        )
        
        assert circuit.metadata["domain"] == "aerospace"
        assert circuit.metadata["version"] == "1.0"
    
    @pytest.mark.asyncio
    async def test_circuit_key_generation(self):
        """Test that circuit generates proving and verification keys."""
        generator = ProofGenerator()
        
        circuit = await generator.create_circuit(
            name="test_circuit",
            description="Test circuit",
            constraints=100,
            public_inputs_count=2,
            private_inputs_count=3
        )
        
        assert circuit.proving_key is not None
        assert isinstance(circuit.proving_key, ProvingKey)
        assert circuit.verification_key is not None
        assert isinstance(circuit.verification_key, VerificationKey)
    
    @pytest.mark.asyncio
    async def test_circuit_storage(self):
        """Test that circuits are stored in registry."""
        generator = ProofGenerator()
        
        circuit = await generator.create_circuit(
            name="test_circuit",
            description="Test circuit",
            constraints=100,
            public_inputs_count=2,
            private_inputs_count=3
        )
        
        assert circuit.circuit_id in generator.circuits
        assert generator.circuits[circuit.circuit_id] == circuit
    
    @pytest.mark.asyncio
    async def test_proving_key_caching(self):
        """Test that proving keys are cached."""
        generator = ProofGenerator()
        
        circuit = await generator.create_circuit(
            name="test_circuit",
            description="Test circuit",
            constraints=100,
            public_inputs_count=2,
            private_inputs_count=3
        )
        
        assert circuit.circuit_id in generator.proving_key_cache
    
    @pytest.mark.asyncio
    async def test_generate_proof(self):
        """Test generating a proof."""
        generator = ProofGenerator()
        
        circuit = await generator.create_circuit(
            name="test_circuit",
            description="Test circuit",
            constraints=100,
            public_inputs_count=2,
            private_inputs_count=3
        )
        
        proof = await generator.generate_proof(
            circuit_id=circuit.circuit_id,
            public_inputs=["input1", "input2"],
            private_inputs=["private1", "private2", "private3"]
        )
        
        assert isinstance(proof, Proof)
        assert proof.circuit_id == circuit.circuit_id
        assert proof.protocol == circuit.protocol
        assert len(proof.public_inputs) == 2
        assert proof.private_inputs_hash is not None
    
    @pytest.mark.asyncio
    async def test_generate_proof_with_metadata(self):
        """Test generating proof with metadata."""
        generator = ProofGenerator()
        
        circuit = await generator.create_circuit(
            name="test_circuit",
            description="Test circuit",
            constraints=100,
            public_inputs_count=2,
            private_inputs_count=3
        )
        
        proof = await generator.generate_proof(
            circuit_id=circuit.circuit_id,
            public_inputs=["input1", "input2"],
            private_inputs=["private1", "private2", "private3"],
            metadata={"capsule_name": "test-capsule"}
        )
        
        assert proof.metadata["capsule_name"] == "test-capsule"
    
    @pytest.mark.asyncio
    async def test_generate_proof_invalid_circuit(self):
        """Test generating proof for non-existent circuit."""
        generator = ProofGenerator()
        
        with pytest.raises(ValueError):
            await generator.generate_proof(
                circuit_id="nonexistent",
                public_inputs=["input1"],
                private_inputs=["private1"]
            )
    
    @pytest.mark.asyncio
    async def test_generate_proof_wrong_public_inputs_count(self):
        """Test generating proof with wrong number of public inputs."""
        generator = ProofGenerator()
        
        circuit = await generator.create_circuit(
            name="test_circuit",
            description="Test circuit",
            constraints=100,
            public_inputs_count=2,
            private_inputs_count=3
        )
        
        with pytest.raises(ValueError):
            await generator.generate_proof(
                circuit_id=circuit.circuit_id,
                public_inputs=["input1"],  # Should be 2
                private_inputs=["private1", "private2", "private3"]
            )
    
    @pytest.mark.asyncio
    async def test_generate_proof_wrong_private_inputs_count(self):
        """Test generating proof with wrong number of private inputs."""
        generator = ProofGenerator()
        
        circuit = await generator.create_circuit(
            name="test_circuit",
            description="Test circuit",
            constraints=100,
            public_inputs_count=2,
            private_inputs_count=3
        )
        
        with pytest.raises(ValueError):
            await generator.generate_proof(
                circuit_id=circuit.circuit_id,
                public_inputs=["input1", "input2"],
                private_inputs=["private1", "private2"]  # Should be 3
            )
    
    @pytest.mark.asyncio
    async def test_proof_storage(self):
        """Test that proofs are stored in registry."""
        generator = ProofGenerator()
        
        circuit = await generator.create_circuit(
            name="test_circuit",
            description="Test circuit",
            constraints=100,
            public_inputs_count=2,
            private_inputs_count=3
        )
        
        proof = await generator.generate_proof(
            circuit_id=circuit.circuit_id,
            public_inputs=["input1", "input2"],
            private_inputs=["private1", "private2", "private3"]
        )
        
        assert proof.proof_id in generator.proofs
        assert generator.proofs[proof.proof_id] == proof
    
    @pytest.mark.asyncio
    async def test_verify_proof(self):
        """Test verifying a proof."""
        generator = ProofGenerator()
        
        circuit = await generator.create_circuit(
            name="test_circuit",
            description="Test circuit",
            constraints=100,
            public_inputs_count=2,
            private_inputs_count=3
        )
        
        proof = await generator.generate_proof(
            circuit_id=circuit.circuit_id,
            public_inputs=["input1", "input2"],
            private_inputs=["private1", "private2", "private3"]
        )
        
        is_valid = await generator.verify_proof(proof.proof_id)
        
        assert is_valid
        assert proof.verified == ProofStatus.VALID
    
    @pytest.mark.asyncio
    async def test_verify_proof_invalid_proof_id(self):
        """Test verifying non-existent proof."""
        generator = ProofGenerator()
        
        with pytest.raises(ValueError):
            await generator.verify_proof("nonexistent")
    
    @pytest.mark.asyncio
    async def test_batch_generate_proofs(self):
        """Test batch proof generation."""
        generator = ProofGenerator()
        
        circuit = await generator.create_circuit(
            name="test_circuit",
            description="Test circuit",
            constraints=100,
            public_inputs_count=2,
            private_inputs_count=3
        )
        
        inputs_list = [
            (["input1", "input2"], ["private1", "private2", "private3"]),
            (["input3", "input4"], ["private4", "private5", "private6"]),
            (["input5", "input6"], ["private7", "private8", "private9"])
        ]
        
        proofs = await generator.batch_generate_proofs(circuit.circuit_id, inputs_list)
        
        assert len(proofs) == 3
        assert all(isinstance(p, Proof) for p in proofs)
    
    @pytest.mark.asyncio
    async def test_batch_generate_proofs_with_metadata(self):
        """Test batch proof generation with metadata."""
        generator = ProofGenerator()
        
        circuit = await generator.create_circuit(
            name="test_circuit",
            description="Test circuit",
            constraints=100,
            public_inputs_count=2,
            private_inputs_count=3
        )
        
        inputs_list = [
            (["input1", "input2"], ["private1", "private2", "private3"]),
            (["input3", "input4"], ["private4", "private5", "private6"])
        ]
        
        metadata_list = [
            {"capsule": "capsule1"},
            {"capsule": "capsule2"}
        ]
        
        proofs = await generator.batch_generate_proofs(
            circuit.circuit_id,
            inputs_list,
            metadata_list
        )
        
        assert proofs[0].metadata["capsule"] == "capsule1"
        assert proofs[1].metadata["capsule"] == "capsule2"
    
    @pytest.mark.asyncio
    async def test_batch_verify_proofs(self):
        """Test batch proof verification."""
        generator = ProofGenerator()
        
        circuit = await generator.create_circuit(
            name="test_circuit",
            description="Test circuit",
            constraints=100,
            public_inputs_count=2,
            private_inputs_count=3
        )
        
        inputs_list = [
            (["input1", "input2"], ["private1", "private2", "private3"]),
            (["input3", "input4"], ["private4", "private5", "private6"])
        ]
        
        proofs = await generator.batch_generate_proofs(circuit.circuit_id, inputs_list)
        proof_ids = [p.proof_id for p in proofs]
        
        results = await generator.batch_verify_proofs(proof_ids)
        
        assert len(results) == 2
        assert all(results)
    
    @pytest.mark.asyncio
    async def test_get_circuit(self):
        """Test getting circuit by ID."""
        generator = ProofGenerator()
        
        circuit = await generator.create_circuit(
            name="test_circuit",
            description="Test circuit",
            constraints=100,
            public_inputs_count=2,
            private_inputs_count=3
        )
        
        retrieved = generator.get_circuit(circuit.circuit_id)
        
        assert retrieved is not None
        assert retrieved.circuit_id == circuit.circuit_id
    
    @pytest.mark.asyncio
    async def test_get_circuit_not_found(self):
        """Test getting non-existent circuit."""
        generator = ProofGenerator()
        
        retrieved = generator.get_circuit("nonexistent")
        
        assert retrieved is None
    
    @pytest.mark.asyncio
    async def test_get_proof(self):
        """Test getting proof by ID."""
        generator = ProofGenerator()
        
        circuit = await generator.create_circuit(
            name="test_circuit",
            description="Test circuit",
            constraints=100,
            public_inputs_count=2,
            private_inputs_count=3
        )
        
        proof = await generator.generate_proof(
            circuit_id=circuit.circuit_id,
            public_inputs=["input1", "input2"],
            private_inputs=["private1", "private2", "private3"]
        )
        
        retrieved = generator.get_proof(proof.proof_id)
        
        assert retrieved is not None
        assert retrieved.proof_id == proof.proof_id
    
    @pytest.mark.asyncio
    async def test_get_proof_not_found(self):
        """Test getting non-existent proof."""
        generator = ProofGenerator()
        
        retrieved = generator.get_proof("nonexistent")
        
        assert retrieved is None
    
    @pytest.mark.asyncio
    async def test_list_circuits_all(self):
        """Test listing all circuits."""
        generator = ProofGenerator()
        
        await generator.create_circuit(
            "circuit1", "Test 1", 100, 2, 3, ProofProtocol.GROTH16
        )
        await generator.create_circuit(
            "circuit2", "Test 2", 200, 3, 4, ProofProtocol.PLONK
        )
        
        circuits = generator.list_circuits()
        
        assert len(circuits) == 2
    
    @pytest.mark.asyncio
    async def test_list_circuits_by_protocol(self):
        """Test listing circuits filtered by protocol."""
        generator = ProofGenerator()
        
        await generator.create_circuit(
            "circuit1", "Test 1", 100, 2, 3, ProofProtocol.GROTH16
        )
        await generator.create_circuit(
            "circuit2", "Test 2", 200, 3, 4, ProofProtocol.PLONK
        )
        await generator.create_circuit(
            "circuit3", "Test 3", 150, 2, 3, ProofProtocol.GROTH16
        )
        
        groth16_circuits = generator.list_circuits(ProofProtocol.GROTH16)
        plonk_circuits = generator.list_circuits(ProofProtocol.PLONK)
        
        assert len(groth16_circuits) == 2
        assert len(plonk_circuits) == 1
    
    @pytest.mark.asyncio
    async def test_list_proofs_all(self):
        """Test listing all proofs."""
        generator = ProofGenerator()
        
        circuit = await generator.create_circuit(
            "test_circuit", "Test", 100, 2, 3
        )
        
        await generator.generate_proof(
            circuit.circuit_id,
            ["input1", "input2"],
            ["private1", "private2", "private3"]
        )
        await generator.generate_proof(
            circuit.circuit_id,
            ["input3", "input4"],
            ["private4", "private5", "private6"]
        )
        
        proofs = generator.list_proofs()
        
        assert len(proofs) == 2
    
    @pytest.mark.asyncio
    async def test_list_proofs_by_circuit(self):
        """Test listing proofs filtered by circuit."""
        generator = ProofGenerator()
        
        circuit1 = await generator.create_circuit(
            "circuit1", "Test 1", 100, 2, 3
        )
        circuit2 = await generator.create_circuit(
            "circuit2", "Test 2", 200, 2, 3
        )
        
        await generator.generate_proof(
            circuit1.circuit_id,
            ["input1", "input2"],
            ["private1", "private2", "private3"]
        )
        await generator.generate_proof(
            circuit2.circuit_id,
            ["input3", "input4"],
            ["private4", "private5", "private6"]
        )
        
        circuit1_proofs = generator.list_proofs(circuit_id=circuit1.circuit_id)
        
        assert len(circuit1_proofs) == 1
        assert circuit1_proofs[0].circuit_id == circuit1.circuit_id
    
    @pytest.mark.asyncio
    async def test_list_proofs_by_status(self):
        """Test listing proofs filtered by status."""
        generator = ProofGenerator()
        
        circuit = await generator.create_circuit(
            "test_circuit", "Test", 100, 2, 3
        )
        
        proof1 = await generator.generate_proof(
            circuit.circuit_id,
            ["input1", "input2"],
            ["private1", "private2", "private3"]
        )
        proof2 = await generator.generate_proof(
            circuit.circuit_id,
            ["input3", "input4"],
            ["private4", "private5", "private6"]
        )
        
        # Verify one proof
        await generator.verify_proof(proof1.proof_id)
        
        valid_proofs = generator.list_proofs(status=ProofStatus.VALID)
        pending_proofs = generator.list_proofs(status=ProofStatus.PENDING)
        
        assert len(valid_proofs) == 1
        assert len(pending_proofs) == 1
    
    @pytest.mark.asyncio
    async def test_get_statistics(self):
        """Test getting proof statistics."""
        generator = ProofGenerator()
        
        circuit1 = await generator.create_circuit(
            "circuit1", "Test 1", 100, 2, 3, ProofProtocol.GROTH16
        )
        circuit2 = await generator.create_circuit(
            "circuit2", "Test 2", 200, 2, 3, ProofProtocol.PLONK
        )
        
        proof1 = await generator.generate_proof(
            circuit1.circuit_id,
            ["input1", "input2"],
            ["private1", "private2", "private3"]
        )
        proof2 = await generator.generate_proof(
            circuit2.circuit_id,
            ["input3", "input4"],
            ["private4", "private5", "private6"]
        )
        
        await generator.verify_proof(proof1.proof_id)
        await generator.verify_proof(proof2.proof_id)
        
        stats = generator.get_statistics()
        
        assert stats["total_circuits"] == 2
        assert stats["total_proofs"] == 2
        assert stats["by_protocol"]["groth16"] == 1
        assert stats["by_protocol"]["plonk"] == 1
        assert stats["verification_rate"] == 100.0


class TestProofDataclass:
    """Test suite for Proof dataclass."""
    
    @pytest.mark.asyncio
    async def test_proof_to_dict(self):
        """Test proof serialization to dictionary."""
        generator = ProofGenerator()
        
        circuit = await generator.create_circuit(
            "test_circuit", "Test", 100, 2, 3
        )
        
        proof = await generator.generate_proof(
            circuit.circuit_id,
            ["input1", "input2"],
            ["private1", "private2", "private3"],
            metadata={"capsule": "test"}
        )
        
        proof_dict = proof.to_dict()
        
        assert isinstance(proof_dict, dict)
        assert proof_dict["proof_id"] == proof.proof_id
        assert proof_dict["protocol"] == proof.protocol.value
        assert proof_dict["metadata"]["capsule"] == "test"
    
    @pytest.mark.asyncio
    async def test_proof_from_dict(self):
        """Test proof deserialization from dictionary."""
        from datetime import datetime
        
        data = {
            "proof_id": "test_proof_id",
            "circuit_id": "test_circuit_id",
            "protocol": "groth16",
            "proof_data": "0x1234567890abcdef",
            "public_inputs": ["input1", "input2"],
            "private_inputs_hash": "hash123",
            "created_at": datetime.now().isoformat(),
            "verified": "valid",
            "metadata": {"capsule": "test"}
        }
        
        proof = Proof.from_dict(data)
        
        assert proof.proof_id == "test_proof_id"
        assert proof.protocol == ProofProtocol.GROTH16
        assert proof.verified == ProofStatus.VALID
        assert proof.metadata["capsule"] == "test"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
