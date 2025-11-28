import pytest
from src.ai_safety.shield_v3 import AIShieldV3

def test_space_prior():
    shield = AIShieldV3()
    prior = shield.priors['space_v1']
    
    # Test Plasma Pressure Law (P ~ 1/r^2)
    # Case 1: Consistent (Low Energy)
    state_safe = {"radius": 2.0, "pressure": 25.0} # 100 * (1/4) = 25
    energy_safe = prior.calculate_energy(state_safe)
    assert energy_safe < 1.0
    
    # Case 2: Violation (High Energy)
    state_unsafe = {"radius": 2.0, "pressure": 100.0} # Should be 25
    energy_unsafe = prior.calculate_energy(state_unsafe)
    assert energy_unsafe > 10.0

def test_bio_prior():
    shield = AIShieldV3()
    prior = shield.priors['bio_v1']
    
    # Test Folding Stability
    state_stable = {"folding_score": 0.1}
    energy_stable = prior.calculate_energy(state_stable)
    assert energy_stable < 1.0
    
    state_unstable = {"folding_score": 5.0}
    energy_unstable = prior.calculate_energy(state_unstable)
    assert energy_unstable > 5.0

if __name__ == "__main__":
    test_space_prior()
    test_bio_prior()
    print("Batch 3 Iteration 2 Verified.")
