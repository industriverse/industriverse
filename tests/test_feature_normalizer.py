import pytest
import torch
from src.scf.dataloading.feature_normalizer import FeatureNormalizer

def test_normalization_dict():
    ranges = {'temp': (0, 100), 'power': (0, 1000)}
    normalizer = FeatureNormalizer(ranges)
    
    inputs = {'temp': 50.0, 'power': 100.0, 'unknown': 5.0}
    normalized = normalizer.normalize(inputs)
    
    assert normalized['temp'] == 0.5
    assert normalized['power'] == 0.1
    assert normalized['unknown'] == 5.0 # Pass through

def test_denormalization_dict():
    ranges = {'temp': (0, 100)}
    normalizer = FeatureNormalizer(ranges)
    
    inputs = {'temp': 0.5}
    denormalized = normalizer.denormalize(inputs)
    
    assert denormalized['temp'] == 50.0

def test_normalization_tensor():
    ranges = {'a': (0, 10), 'b': (0, 20)}
    normalizer = FeatureNormalizer(ranges)
    
    # Batch of 2, features [a, b]
    x = torch.tensor([[5.0, 10.0], [0.0, 20.0]])
    feature_order = ['a', 'b']
    
    norm_x = normalizer.normalize_tensor(x, feature_order)
    
    expected = torch.tensor([[0.5, 0.5], [0.0, 1.0]])
    assert torch.allclose(norm_x, expected, atol=1e-5)
