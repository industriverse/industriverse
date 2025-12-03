from src.scf.autonomy.industrial_kernel import IndustrialKernel
from src.security.thermodynamic_safety import ThermodynamicSafetyLayer

def verify_industrial_kernel():
    print("🏭 Verifying Industrial Autonomy Kernel...")
    kernel = IndustrialKernel(factory_id="TEST_FACTORY")
    
    # 1. Check Initialization (Default State)
    status = kernel.get_status()
    assert "active_lines" in status
    print(f"   Factory Status: {status['status']} | Active Lines: {len(status['active_lines'])}")
    
    # 2. Optimize Line
    result = kernel.optimize_production_line("Line-A")
    assert result["energy_saved_kw"] > 0.0
    print(f"   Optimization Result: Saved {result['energy_saved_kw']:.2f} kW")
    
    # 3. Balance Entropy
    kernel.balance_entropy()
    print("✅ Industrial Kernel Verified.")

def verify_thermodynamic_safety():
    print("🛡️ Verifying Thermodynamic Safety Layer...")
    safety = ThermodynamicSafetyLayer(energy_threshold_joules=5000.0)
    
    # 1. Normal Operation
    assert safety.monitor_energy_flux(1000.0) == True
    
    # 2. Energy Spike
    assert safety.monitor_energy_flux(6000.0) == False
    print("   ✅ Detected Energy Spike.")
    
    # 3. Intrusion Detection (Phantom Heat)
    telemetry = {"cpu_temp": 85.0, "load": 0.1}
    assert safety.detect_intrusion(telemetry) == True
    print("   ✅ Detected Phantom Heat Intrusion.")

if __name__ == "__main__":
    verify_industrial_kernel()
    verify_thermodynamic_safety()
    print("\n🎉 PHASE 3 VERIFIED")
