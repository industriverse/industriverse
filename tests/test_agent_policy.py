import pytest
from src.scf.agents.sovereign_agent import SovereignAgent
from src.security_compliance_layer.thermo_checks import ThermodynamicSafetyGuard
from src.scf.dataloading.feature_normalizer import FeatureNormalizer

def test_agent_decision_safe():
    # Setup
    guard = ThermodynamicSafetyGuard(max_temp_c=100.0)
    ranges = {'temp': (0, 100), 'pressure': (0, 10)}
    normalizer = FeatureNormalizer(ranges)
    model = None # Mock
    
    agent = SovereignAgent(model, guard, normalizer)
    
    # Safe State
    state = {'temp': 50.0, 'pressure': 1.0}
    action = agent.decide(state)
    
    # Policy reduces temp by 5% (50 * 0.95 = 47.5)
    assert 47.0 < action['temp'] < 48.0
    assert action['pressure'] == 1.0

def test_agent_decision_unsafe():
    # Setup
    guard = ThermodynamicSafetyGuard(max_temp_c=100.0)
    ranges = {'temp': (0, 200), 'pressure': (0, 10)} # Range allows unsafe values
    normalizer = FeatureNormalizer(ranges)
    model = None
    
    agent = SovereignAgent(model, guard, normalizer)
    
    # Unsafe State (150C)
    state = {'temp': 150.0, 'pressure': 1.0}
    
    # Policy reduces 150 -> 142.5 (Still > 100 max_temp)
    # Should trigger fallback
    action = agent.decide(state)
    
    assert action['temp'] == 25.0 # Fallback
