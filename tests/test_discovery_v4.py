import pytest
from src.discovery_loop.pipeline_v4 import IndustriverseDiscoveryV4
from src.rdr.pipeline import PhysicsRDRPipeline

# Mock LLM and Embedding Models (Reuse from test_rdr)
class MockLLM:
    def generate(self, prompt, max_tokens=None):
        return '{"Observable": "B-field", "Phenomenon": "Instability", "Mechanism": "Reconnection", "Scale": "Micro", "Method": "PIC", "Application": "Fusion"}'

class MockEmbedding:
    def encode(self, text):
        import numpy as np
        return np.random.rand(768).astype(np.float32)

def test_discovery_v4_campaign():
    llm = MockLLM()
    embed = MockEmbedding()
    
    discovery = IndustriverseDiscoveryV4(llm_model=llm, embedding_model=embed)
    
    datasets = ["dataset_A", "dataset_B"]
    discoveries = discovery.run_discovery_campaign(datasets)
    
    assert len(discoveries) == 2
    assert discoveries[0]['grounding'] == 'RDR-Validated'
    assert "proof" in discoveries[0]
