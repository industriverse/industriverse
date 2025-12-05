from dataclasses import dataclass
from typing import List, Dict
import time

@dataclass
class DaemonGoal:
    goal_id: str
    target_metric: str
    target_value: float
    current_value: float = 0.0
    period: str = 'DAILY' # 'DAILY', 'WEEKLY'
    status: str = 'ACTIVE' # 'ACTIVE', 'COMPLETED', 'FAILED'
    reward_points: float = 100.0

class GoalSystem:
    """
    Manages Daily and Weekly goals for the Daemon.
    """
    def __init__(self):
        self.active_goals: List[DaemonGoal] = []
        self._initialize_default_goals()

    def _initialize_default_goals(self):
        """
        Set up standard goals.
        """
        self.active_goals.append(DaemonGoal(
            goal_id='daily_fossils',
            target_metric='fossils_processed_count',
            target_value=1000.0,
            period='DAILY',
            reward_points=50.0
        ))
        self.active_goals.append(DaemonGoal(
            goal_id='daily_energy_savings',
            target_metric='energy_saved_mj',
            target_value=50.0,
            period='DAILY',
            reward_points=100.0
        ))

    def update_progress(self, metrics: Dict[str, float]) -> List[DaemonGoal]:
        """
        Update progress towards goals based on new metrics.
        Returns list of completed goals this update.
        """
        completed_goals = []
        
        for goal in self.active_goals:
            if goal.status != 'ACTIVE':
                continue
                
            metric_val = metrics.get(goal.target_metric, 0.0)
            # Assuming metrics are cumulative for the period or we add delta
            # For simplicity, let's assume 'metrics' contains the delta for this tick
            goal.current_value += metric_val
            
            if goal.current_value >= goal.target_value:
                goal.status = 'COMPLETED'
                completed_goals.append(goal)
                print(f"🏆 GOAL COMPLETED: {goal.goal_id} ({goal.current_value}/{goal.target_value})")
                
        return completed_goals

    def reset_period(self, period: str):
        """
        Reset goals for a new period (e.g. new day).
        """
        # In a real system, we'd archive old goals and create new ones.
        # Here we just reset current_value for active goals of that period.
        for goal in self.active_goals:
            if goal.period == period:
                goal.current_value = 0.0
                goal.status = 'ACTIVE'
                print(f"🔄 Goal Reset: {goal.goal_id}")
