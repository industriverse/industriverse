"""
Unit tests for T2L Service

Tests cover:
1. Service initialization
2. Adapter library loading
3. Adapter training
4. Adapter loading and switching
5. Hypothesis generation
6. Batch generation
7. Adapter recommendation
8. Adapter information retrieval

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil
import json

import sys
sys.path.append('/home/ubuntu/industriverse/src/core_ai_layer/discovery_loop/services/t2l')
from t2l_service import T2LService, LoRAConfig, LoRAAdapter, TrainingConfig


class TestT2LService:
    """Test suite for T2L Service."""
    
    @pytest.fixture
    def temp_adapter_dir(self):
        """Create a temporary directory for adapters."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def t2l_service(self, temp_adapter_dir):
        """Create a T2L service instance with temporary adapter directory."""
        return T2LService(
            base_model_name="UserLM-8B",
            adapter_library_path=temp_adapter_dir
        )
    
    def test_initialization(self, t2l_service):
        """Test T2L service initialization."""
        assert t2l_service.base_model_name == "UserLM-8B"
        assert t2l_service.adapter_library_path is not None
        assert isinstance(t2l_service.adapters, dict)
        assert t2l_service.current_adapter is None
    
    def test_default_adapters_creation(self, t2l_service):
        """Test creation of default adapters."""
        # Check that default adapters were created
        assert len(t2l_service.adapters) > 0
        
        # Check for expected domains
        expected_domains = ["aerospace", "manufacturing", "defense", "energy"]
        for domain in expected_domains:
            assert domain in t2l_service.adapters
            adapter = t2l_service.adapters[domain]
            assert isinstance(adapter, LoRAAdapter)
            assert adapter.name == domain
            assert adapter.base_model == "UserLM-8B"
    
    def test_list_adapters(self, t2l_service):
        """Test listing available adapters."""
        adapters_info = t2l_service.list_adapters()
        
        assert isinstance(adapters_info, list)
        assert len(adapters_info) > 0
        
        for adapter_info in adapters_info:
            assert "name" in adapter_info
            assert "domain" in adapter_info
            assert "base_model" in adapter_info
            assert "rank" in adapter_info
            assert "status" in adapter_info
            assert "created_at" in adapter_info
    
    def test_get_adapter_info(self, t2l_service):
        """Test getting adapter information."""
        # Get info for aerospace adapter
        adapter_info = t2l_service.get_adapter_info("aerospace")
        
        assert adapter_info["name"] == "aerospace"
        assert "domain" in adapter_info
        assert "config" in adapter_info
        assert "rank" in adapter_info["config"]
        assert "alpha" in adapter_info["config"]
    
    def test_get_adapter_info_not_found(self, t2l_service):
        """Test getting info for non-existent adapter."""
        with pytest.raises(ValueError, match="not found"):
            t2l_service.get_adapter_info("nonexistent_adapter")
    
    @pytest.mark.asyncio
    async def test_train_adapter(self, t2l_service):
        """Test training a new adapter."""
        training_data = [
            "Sample training text 1",
            "Sample training text 2",
            "Sample training text 3"
        ] * 5
        
        adapter = await t2l_service.train_adapter(
            domain="test_domain",
            training_data=training_data,
            adapter_name="test_adapter"
        )
        
        assert isinstance(adapter, LoRAAdapter)
        assert adapter.name == "test_adapter"
        assert adapter.domain == "test_domain"
        assert adapter.base_model == "UserLM-8B"
        assert adapter.metadata["training_data_size"] == len(training_data)
        assert adapter.metadata["status"] == "trained"
        
        # Check that adapter was added to library
        assert "test_adapter" in t2l_service.adapters
    
    @pytest.mark.asyncio
    async def test_train_adapter_with_custom_config(self, t2l_service):
        """Test training adapter with custom LoRA and training configs."""
        training_data = ["Sample text"] * 10
        
        lora_config = LoRAConfig(rank=16, alpha=32, dropout=0.2)
        training_config = TrainingConfig(learning_rate=1e-4, num_epochs=2, batch_size=2)
        
        adapter = await t2l_service.train_adapter(
            domain="custom_domain",
            training_data=training_data,
            lora_config=lora_config,
            training_config=training_config
        )
        
        assert adapter.config.rank == 16
        assert adapter.config.alpha == 32
        assert adapter.config.dropout == 0.2
        assert adapter.metadata["training_config"]["learning_rate"] == 1e-4
        assert adapter.metadata["training_config"]["num_epochs"] == 2
    
    def test_load_adapter(self, t2l_service):
        """Test loading an adapter."""
        # Load aerospace adapter
        adapter = t2l_service.load_adapter("aerospace")
        
        assert isinstance(adapter, LoRAAdapter)
        assert adapter.name == "aerospace"
        assert t2l_service.current_adapter == adapter
    
    def test_load_adapter_not_found(self, t2l_service):
        """Test loading non-existent adapter."""
        with pytest.raises(ValueError, match="not found"):
            t2l_service.load_adapter("nonexistent_adapter")
    
    @pytest.mark.asyncio
    async def test_generate_hypothesis(self, t2l_service):
        """Test hypothesis generation."""
        # Load adapter first
        t2l_service.load_adapter("aerospace")
        
        # Generate hypothesis
        prompt = "Design an optimized wing"
        hypothesis = await t2l_service.generate_hypothesis(prompt)
        
        assert isinstance(hypothesis, str)
        assert len(hypothesis) > 0
        assert "AEROSPACE" in hypothesis.upper() or "aerospace" in hypothesis.lower()
    
    @pytest.mark.asyncio
    async def test_generate_hypothesis_with_adapter_name(self, t2l_service):
        """Test hypothesis generation with adapter name specified."""
        prompt = "Optimize manufacturing process"
        hypothesis = await t2l_service.generate_hypothesis(
            prompt=prompt,
            adapter_name="manufacturing"
        )
        
        assert isinstance(hypothesis, str)
        assert len(hypothesis) > 0
        assert t2l_service.current_adapter.name == "manufacturing"
    
    @pytest.mark.asyncio
    async def test_generate_hypothesis_no_adapter_loaded(self, t2l_service):
        """Test hypothesis generation without loading adapter."""
        with pytest.raises(ValueError, match="No adapter loaded"):
            await t2l_service.generate_hypothesis("Test prompt")
    
    @pytest.mark.asyncio
    async def test_batch_generate(self, t2l_service):
        """Test batch hypothesis generation."""
        prompts = [
            "Optimize wing design",
            "Improve engine efficiency",
            "Reduce aircraft weight"
        ]
        
        hypotheses = await t2l_service.batch_generate(
            prompts=prompts,
            adapter_name="aerospace"
        )
        
        assert isinstance(hypotheses, list)
        assert len(hypotheses) == len(prompts)
        
        for hypothesis in hypotheses:
            assert isinstance(hypothesis, str)
            assert len(hypothesis) > 0
    
    def test_get_recommended_adapter(self, t2l_service):
        """Test adapter recommendation based on context."""
        # Test aerospace context
        context1 = "We need to optimize aircraft wing design for supersonic flight"
        recommended1 = t2l_service.get_recommended_adapter(context1)
        assert recommended1 == "aerospace"
        
        # Test manufacturing context
        context2 = "Improve manufacturing process efficiency in the factory"
        recommended2 = t2l_service.get_recommended_adapter(context2)
        assert recommended2 == "manufacturing"
        
        # Test energy context
        context3 = "Optimize energy consumption in power generation systems"
        recommended3 = t2l_service.get_recommended_adapter(context3)
        assert recommended3 == "energy"
    
    def test_adapter_manifest_saving(self, t2l_service, temp_adapter_dir):
        """Test that adapter manifests are saved correctly."""
        # Create a test adapter
        adapter = LoRAAdapter(
            name="test_save",
            domain="test domain",
            base_model="UserLM-8B",
            config=LoRAConfig(rank=8, alpha=16),
            path=temp_adapter_dir / "test_save",
            metadata={"test_key": "test_value"}
        )
        
        # Save manifest
        t2l_service._save_adapter_manifest(adapter)
        
        # Check that manifest file exists
        manifest_path = adapter.path / "manifest.json"
        assert manifest_path.exists()
        
        # Load and verify manifest
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        assert manifest["name"] == "test_save"
        assert manifest["domain"] == "test domain"
        assert manifest["base_model"] == "UserLM-8B"
        assert manifest["config"]["rank"] == 8
        assert manifest["config"]["alpha"] == 16
        assert manifest["metadata"]["test_key"] == "test_value"
    
    def test_adapter_library_loading(self, temp_adapter_dir):
        """Test loading adapters from an existing library."""
        # Create a test adapter manifest
        adapter_dir = temp_adapter_dir / "test_adapter"
        adapter_dir.mkdir(parents=True)
        
        manifest = {
            "name": "test_adapter",
            "domain": "test domain",
            "base_model": "UserLM-8B",
            "config": {
                "rank": 8,
                "alpha": 16,
                "dropout": 0.1,
                "target_modules": ["q_proj", "v_proj"],
                "bias": "none"
            },
            "metadata": {"status": "trained"},
            "created_at": "2025-11-16T00:00:00"
        }
        
        with open(adapter_dir / "manifest.json", 'w') as f:
            json.dump(manifest, f)
        
        # Create T2L service (should load the adapter)
        t2l_service = T2LService(
            base_model_name="UserLM-8B",
            adapter_library_path=temp_adapter_dir
        )
        
        # Check that adapter was loaded
        assert "test_adapter" in t2l_service.adapters
        adapter = t2l_service.adapters["test_adapter"]
        assert adapter.name == "test_adapter"
        assert adapter.domain == "test domain"
        assert adapter.config.rank == 8


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
