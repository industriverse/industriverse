import pytest
from src.scf.monitoring.entropy_event_detector import EntropyEventDetector

def test_thermal_runaway():
    detector = EntropyEventDetector(entropy_threshold=0.5, temp_threshold=80.0)
    
    # Normal State
    state = {'temp': 70.0}
    event = detector.detect(state, entropy_rate=0.1)
    assert event is None
    
    # Runaway State
    state = {'temp': 85.0}
    event = detector.detect(state, entropy_rate=0.6)
    assert event is not None
    assert event.event_type == 'THERMAL_RUNAWAY'

def test_waste_period():
    detector = EntropyEventDetector()
    
    # Idle but efficient
    state = {'temp': 30.0}
    event = detector.detect(state, entropy_rate=0.1)
    assert event is None
    
    # Idle but wasteful (high entropy)
    event = detector.detect(state, entropy_rate=0.6)
    assert event is not None
    assert event.event_type == 'WASTE_PERIOD'
