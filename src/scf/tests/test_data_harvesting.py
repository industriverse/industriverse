import sys
import os
import json
import shutil
from unittest.mock import MagicMock, patch

# Mock dependencies
sys.modules["numpy"] = MagicMock()
sys.modules["pydantic"] = MagicMock()
sys.modules["fastapi"] = MagicMock()

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.scf.fertilization.data_harvester import DataHarvester

def test_data_harvesting():
    print("🧪 Testing Data Harvesting Pipeline...")
    
    # Setup Mock ValueVault
    mock_fossils = [
        # Valid Sample
        {
            "type": "CODE_EVOLUTION",
            "verdict": "APPROVE",
            "intent": "Optimize Grid",
            "code_snippet": "def optimize(): pass",
            "feedback": {"score": 0.95},
            "timestamp": 1234567890
        },
        # Invalid: Rejected
        {
            "type": "CODE_EVOLUTION",
            "verdict": "REJECT",
            "intent": "Bad Code",
            "code_snippet": "while True: pass",
            "feedback": {"score": 0.1},
            "timestamp": 1234567891
        },
        # Invalid: Low Score
        {
            "type": "CODE_EVOLUTION",
            "verdict": "APPROVE", # Technically approved but low score (edge case)
            "intent": "Mediocre Code",
            "code_snippet": "print('ok')",
            "feedback": {"score": 0.5},
            "timestamp": 1234567892
        },
        # Invalid: Wrong Type
        {
            "type": "SYSTEM_LOG",
            "content": "System started"
        }
    ]
    
    with patch("src.scf.fertilization.data_harvester.ValueVault") as MockVault:
        MockVault.return_value.retrieve_all_secrets.return_value = mock_fossils
        
        harvester = DataHarvester()
        
        # Run Harvest
        count = harvester.harvest("test_dataset.jsonl")
        
        # Verify Count
        assert count == 1
        print(f"✅ Harvested {count} valid sample(s) (Expected 1)")
        
        # Verify Output File
        output_path = os.path.join(harvester.dataset_dir, "test_dataset.jsonl")
        assert os.path.exists(output_path)
        
        with open(output_path, 'r') as f:
            line = f.readline()
            entry = json.loads(line)
            
        assert entry["instruction"] == "Optimize Grid"
        assert entry["output"] == "def optimize(): pass"
        print("✅ Dataset Content Verified")
        
        # Cleanup
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == "__main__":
    test_data_harvesting()
