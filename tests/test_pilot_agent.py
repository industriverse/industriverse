import pytest
import os
from src.scf.agents.dark_factory_pilot import DarkFactoryPilot

def test_dark_factory_pilot():
    # Create pilot
    pilot = DarkFactoryPilot(atlas_db="test_atlas.db")
    
    # Run short pilot (1 second, which might be 1 or 2 steps depending on timing)
    # We mock the twin bridge inside the class or just rely on its mock mode (default)
    pilot.run_pilot(duration_seconds=2)
    
    # Check log
    assert os.path.exists("pilot_pov_log.jsonl")
    with open("pilot_pov_log.jsonl", "r") as f:
        lines = f.readlines()
        assert len(lines) > 0
        last_line = lines[-1]
        assert "FINANCIAL_AUDIT" in last_line
        
    # Cleanup
    os.remove("pilot_pov_log.jsonl")
    if os.path.exists("test_atlas.db"):
        os.remove("test_atlas.db")
