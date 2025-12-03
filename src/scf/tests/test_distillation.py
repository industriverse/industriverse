import sys
import os
import json
from unittest.mock import MagicMock, patch

# Mock dependencies
sys.modules["numpy"] = MagicMock()
sys.modules["pydantic"] = MagicMock()
sys.modules["fastapi"] = MagicMock()

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.scf.distillation.teacher_student import DistillationSession

def test_distillation_session():
    print("🧪 Testing Distillation Session...")
    
    # Create a dummy dataset
    dummy_path = "test_distill.jsonl"
    with open(dummy_path, 'w') as f:
        f.write(json.dumps({"instruction": "test", "output": "code"}) + '\n')
        
    try:
        session = DistillationSession("Teacher_Mock", "arm64")
        session.load_dataset(dummy_path)
        
        assert len(session.dataset) == 1
        print("✅ Dataset Loaded")
        
        result = session.run(epochs=1)
        
        assert result["status"] == "success"
        assert result["teacher"] == "Teacher_Mock"
        assert "BitNet" in result["student"]
        assert result["compression_ratio"] == "8.0x"
        print("✅ Distillation Run Verified")
        
    finally:
        if os.path.exists(dummy_path):
            os.remove(dummy_path)

if __name__ == "__main__":
    test_distillation_session()
