import pytest
import os
import torch
from src.scf.training.resume_engine import ResumeEngine

def test_save_load_checkpoint():
    engine = ResumeEngine(checkpoint_dir="test_checkpoints")
    
    # Mock states
    model_state = {'weights': [1, 2, 3]}
    optimizer_state = {'lr': 0.01}
    
    engine.save_checkpoint(model_state, optimizer_state, epoch=5, step=100, metrics={'loss': 0.5})
    
    checkpoint = engine.load_checkpoint()
    
    assert checkpoint is not None
    assert checkpoint['epoch'] == 5
    assert checkpoint['step'] == 100
    assert checkpoint['model_state'] == model_state
    
    # Cleanup
    os.remove(os.path.join("test_checkpoints", "latest_checkpoint.pt"))
    os.rmdir("test_checkpoints")

def test_no_checkpoint():
    engine = ResumeEngine(checkpoint_dir="empty_checkpoints")
    checkpoint = engine.load_checkpoint()
    assert checkpoint is None
    os.rmdir("empty_checkpoints")
