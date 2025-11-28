import pytest
import numpy as np
from src.rdr.pipeline import PhysicsRDRPipeline

# Mock LLM and Embedding Models
class MockLLM:
    def generate(self, prompt, max_tokens=None):
        return '{"Observable": "B-field", "Phenomenon": "Instability", "Mechanism": "Reconnection", "Scale": "Micro", "Method": "PIC", "Application": "Fusion"}'

class MockEmbedding:
    def encode(self, text):
        return np.random.rand(768).astype(np.float32)

def test_rdr_pipeline_end_to_end():
    llm = MockLLM()
    embed = MockEmbedding()
    pipeline = PhysicsRDRPipeline(llm_model=llm, embedding_model=embed)
    
    results = pipeline.run_full_cycle()
    
    assert "survey" in results
    assert "trends" in results
    assert len(results["papers"]) > 0
    assert "embedding" in results["papers"][0]
    assert "perspectives" in results["papers"][0]

def test_semantic_search():
    llm = MockLLM()
    embed = MockEmbedding()
    pipeline = PhysicsRDRPipeline(llm_model=llm, embedding_model=embed)
    
    # Populate db
    pipeline.run_full_cycle()
    
    query = "MHD stability"
    results = pipeline.semantic_search(query, top_k=1)
    
    assert len(results) == 1
    assert "title" in results[0]
