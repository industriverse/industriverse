import pytest
from src.security_compliance_layer.thermo_checks import ThermodynamicSafetyGuard

def test_first_law():
    guard = ThermodynamicSafetyGuard()
    # 100 in, 100 out -> OK
    assert guard.check_energy_conservation(100.0, 100.0) == True
    # 100 in, 110 out -> Fail (Creation of energy)
    assert guard.check_energy_conservation(100.0, 110.0) == False

def test_second_law():
    guard = ThermodynamicSafetyGuard()
    # Positive entropy production -> OK
    assert guard.check_entropy_increase(0.1) == True
    # Negative entropy production (impossible in isolation) -> Fail
    assert guard.check_entropy_increase(-1.0) == False

def test_safety_limits():
    guard = ThermodynamicSafetyGuard(max_temp_c=50.0)
    assert guard.check_safety_limits(40.0, 1.0) == True
    assert guard.check_safety_limits(60.0, 1.0) == False
