import torch
import argparse
import os
import sys

# Ensure src is in path
sys.path.append(os.getcwd())

from src.scf.models.bitnet import BitNet_Student

def export_to_onnx(model_path, output_path):
    print(f"📦 Exporting Model to ONNX...")
    print(f"   Input: {model_path}")
    print(f"   Output: {output_path}")
    
    # 1. Load Model
    model = BitNet_Student(input_dim=4, hidden_dim=16, output_dim=4)
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path))
        print("   ✅ Loaded weights from checkpoint.")
    else:
        print("   ⚠️  Checkpoint not found. Using random weights (for testing export).")
        
    model.eval()
    
    # 2. Create Dummy Input
    # Shape: [Batch, Features] -> [1, 4]
    dummy_input = torch.randn(1, 4)
    
    # 3. Export
    # Opset 12 might be more stable
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=12,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output']
    )
    
    print(f"✅ Export Successful: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="model_zoo/student_latest.pt", help="Path to PyTorch model")
    parser.add_argument("--output", type=str, default="model_zoo/student.onnx", help="Path to output ONNX file")
    args = parser.parse_args()
    
    export_to_onnx(args.input, args.output)
