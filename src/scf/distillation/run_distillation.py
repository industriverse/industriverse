import os
import sys
import logging

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.scf.distillation.teacher_student import DistillationSession

def main():
    """
    Entry point for the Distillation Job.
    """
    dataset_path = "data/scf/datasets/gen_n_train.jsonl"
    
    if not os.path.exists(dataset_path):
        print(f"⚠️ Dataset not found at {dataset_path}. Please run Data Harvesting first.")
        return

    session = DistillationSession(
        teacher_model_id="Phi-4-GenN-v1",
        student_arch="arm64" # Target architecture for BitNet
    )
    
    session.load_dataset(dataset_path)
    result = session.run(epochs=3)
    
    print("\n🎉 Distillation Summary:")
    print(f"   Teacher: {result['teacher']}")
    print(f"   Student: {result['student']}")
    print(f"   Compression: {result['compression_ratio']}")
    print(f"   Time: {result['duration_seconds']}s")

if __name__ == "__main__":
    main()
