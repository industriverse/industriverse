import pytest
import os
import yaml
from scripts.preflight.verify_integrity import scan_vault, verify_fossil
from scripts.run_big_burn import load_config

def test_integrity_verifier():
    # Create dummy vault
    os.makedirs("test_vault", exist_ok=True)
    
    # Valid file
    with open("test_vault/valid.ndjson", "w") as f:
        f.write('{"id": 1}\n{"id": 2}')
        
    # Corrupt file (empty)
    with open("test_vault/corrupt.ndjson", "w") as f:
        pass
        
    stats = scan_vault("test_vault")
    
    assert stats["valid"] == 1
    assert stats["corrupt"] == 1
    
    # Cleanup
    os.remove("test_vault/valid.ndjson")
    os.remove("test_vault/corrupt.ndjson")
    os.rmdir("test_vault")

def test_config_loader():
    # Create dummy config
    config_data = {"test_key": "test_value"}
    with open("test_config.yaml", "w") as f:
        yaml.dump(config_data, f)
        
    config = load_config("test_config.yaml")
    assert config["test_key"] == "test_value"
    
    os.remove("test_config.yaml")
