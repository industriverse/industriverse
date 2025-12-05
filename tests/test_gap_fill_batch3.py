import pytest
import os
import shutil
from src.scf.infra.sovereign_compute import SovereignCompute
from src.zkp.model_card_prover import ModelCardProver
from src.scf.investor.data_room_builder import DataRoomBuilder

def test_sovereign_compute():
    sov = SovereignCompute()
    assert sov.is_sovereign() == False
    assert sov.check_connection_policy("google.com") == True
    
    sov.enable_sovereign_mode()
    assert sov.is_sovereign() == True
    assert sov.check_connection_policy("google.com") == False
    assert sov.check_connection_policy("localhost") == True
    
    sov.disable_sovereign_mode()

def test_model_card_prover():
    prover = ModelCardProver()
    proof = prover.generate_proof("model_v1", {"accuracy": 0.95})
    
    assert proof["model_id"] == "model_v1"
    assert proof["verified"] == True
    assert prover.verify_proof(proof) == True

def test_data_room_builder():
    builder = DataRoomBuilder(output_dir="test_data_room")
    path = builder.build_data_room()
    
    assert os.path.exists(path)
    assert os.path.exists(os.path.join(path, "INDEX.md"))
    assert os.path.exists(os.path.join(path, "financials"))
    
    # Cleanup
    shutil.rmtree("test_data_room")
