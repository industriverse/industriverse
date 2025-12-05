import pytest
from src.scf.daemon.incentive_engine import IncentiveEngine
from src.scf.daemon.goal_system import GoalSystem

def test_incentive_calculation():
    engine = IncentiveEngine()
    metrics = {
        'fossils_processed_count': 100,
        'energy_saved_mj': 10.0,
        'inference_efficiency_kwh': 0.005 # Better than 0.01 baseline
    }
    
    rewards = engine.calculate_rewards(metrics)
    
    # Check Fossil Bonus (100 * 0.1 = 10)
    assert any(r.reward_type == 'FOSSIL_BONUS' and r.amount == 10.0 for r in rewards)
    
    # Check Entropy Bonus (10 * 1.0 = 10)
    assert any(r.reward_type == 'ENTROPY_BONUS' and r.amount == 10.0 for r in rewards)
    
    # Check Efficiency Bonus
    assert any(r.reward_type == 'EFFICIENCY_BONUS' for r in rewards)
    
    assert engine.get_score() > 20.0

def test_goal_progression():
    goals = GoalSystem()
    
    # Initial state
    assert goals.active_goals[0].current_value == 0.0
    
    # Update progress (Delta)
    metrics = {'fossils_processed_count': 500}
    completed = goals.update_progress(metrics)
    assert len(completed) == 0
    assert goals.active_goals[0].current_value == 500.0
    
    # Complete the goal (Target 1000)
    metrics = {'fossils_processed_count': 600}
    completed = goals.update_progress(metrics)
    assert len(completed) == 1
    assert completed[0].goal_id == 'daily_fossils'
    assert completed[0].status == 'COMPLETED'
