import torch
import sys
import os

# Ensure src is in path
sys.path.append(os.getcwd())

from src.scf.models.bitnet import BitNet_Student, weight_quant

def verify_quantization():
    print("⚖️  Verifying BitNet Quantization (1.58-bit)...")
    
    # 1. Initialize Model
    model = BitNet_Student(4, 16, 4)
    print("   Model Initialized.")
    
    # 2. Inspect Layers
    for name, module in model.named_modules():
        if "BitLinear" in str(type(module)):
            print(f"\n   Checking Layer: {name}")
            
            # Original Weights (Float)
            w = module.weight.data
            print(f"   Original Weights (First 5): {w.view(-1)[:5].tolist()}")
            
            # Quantized Weights (Ternary)
            w_quant = weight_quant(w)
            print(f"   Quantized Weights (First 5): {w_quant.view(-1)[:5].tolist()}")
            
            # Verify Unique Values
            # Note: The values are scaled, so they won't be exactly -1, 0, 1, but {-scale, 0, scale}
            # We check if they cluster around 3 values.
            scale = 1.0 / w.abs().mean().clamp_(min=1e-5)
            normalized = (w_quant * scale).round()
            unique_vals = torch.unique(normalized)
            
            print(f"   Unique Normalized Values: {unique_vals.tolist()}")
            
            if len(unique_vals) <= 3:
                print("   ✅ Quantization Successful (Ternary Structure Preserved)")
            else:
                print(f"   ❌ Quantization Failed. Found {len(unique_vals)} unique values.")
                exit(1)

    print("\n✅ All BitLinear layers verified.")

if __name__ == "__main__":
    verify_quantization()
