import torch
import torch.onnx
from src.scf.models.bitnet import BitNet_Student
from pathlib import Path

def export_dac():
    print("📦 Exporting DAC (Deploy Anywhere Capsule)...")
    
    # 1. Initialize Model
    # In a real pipeline, we would load weights: model.load_state_dict(torch.load("student.pt"))
    model = BitNet_Student(input_dim=4, hidden_dim=16, output_dim=4)
    model.eval()
    
    # 2. Create Dummy Input
    # [Batch=1, Features=4] -> (Temp, Power, Entropy, Time)
    dummy_input = torch.randn(1, 4)
    
    # 3. Export to ONNX
    output_path = Path("ebdm_bitnet.onnx")
    
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    
    print(f"✅ DAC Exported: {output_path}")
    print(f"   Size: {output_path.stat().st_size / 1024:.2f} KB")
    
    # 4. Verify with ONNX Runtime (Simulating Edge Inference)
    try:
        import onnxruntime as ort
        import numpy as np
        
        print("   Verifying with ONNX Runtime...")
        ort_session = ort.InferenceSession(str(output_path))
        
        ort_inputs = {ort_session.get_inputs()[0].name: dummy_input.numpy()}
        ort_outs = ort_session.run(None, ort_inputs)
        
        print("   ✨ Inference Successful!")
        print(f"   Input: {dummy_input.numpy()}")
        print(f"   Output: {ort_outs[0]}")
        
    except ImportError:
        print("   ⚠️ onnxruntime not installed. Skipping verification.")

if __name__ == "__main__":
    export_dac()
