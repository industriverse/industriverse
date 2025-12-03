from src.scf.models.gen_n_2 import GenN2, torch
from src.resource_clusters.volumetric_field import VolumetricEnergyField

def verify_gen_n_2():
    print("🧠 Verifying GenN-2 (Multi-Scale Model)...")
    model = GenN2()
    
    # Mock Data for 3 Scales
    micro = torch.randn(1, 64)
    meso = torch.randn(1, 128)
    macro = torch.randn(1, 256)
    
    # Forward Pass
    discovery, energy = model(micro, meso, macro)
    
    assert discovery is not None
    assert energy is not None
    print("✅ GenN-2 Forward Pass Successful.")

def verify_volumetric_field():
    print("🧊 Verifying Volumetric Energy Field...")
    field = VolumetricEnergyField(dimensions=(5, 5, 5))
    
    # 1. Scan for Zones
    zones = field.find_opportunity_zones(threshold=0.3)
    print(f"   Found {len(zones)} Opportunity Zones (Low Entropy).")
    
    # 2. Inject Energy (Optimize)
    target = (2, 2, 2)
    initial_entropy = field.get_entropy_at(*target)
    field.inject_energy(*target, amount=0.5)
    final_entropy = field.get_entropy_at(*target)
    
    assert final_entropy < initial_entropy, "Energy injection failed to reduce entropy"
    print(f"✅ Energy Injection Successful: {initial_entropy:.2f} -> {final_entropy:.2f}")

if __name__ == "__main__":
    verify_gen_n_2()
    verify_volumetric_field()
    print("\n🎉 PHASE 2 VERIFIED")
