import sys
import os
import json
import time
import random

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.shield.threat_identifier import ThreatIdentifier
from src.simulation.simulation_oracle import SimulationOracle

class ShadowRuntime:
    """
    AI Shield v3 - Gate 9: Shadow Twin Runtime.
    Executes the 'Ideal' simulation in lockstep with the 'Real' machine.
    """
    def __init__(self):
        self.shield = ThreatIdentifier()
        self.oracle = SimulationOracle()
        self.is_running = False

    def run_shadow_loop(self, bytecode_program, machine_id="Test_Machine_001"):
        """
        Simulates a real-time monitoring loop.
        In production, this would subscribe to TelemetryHub via WebSocket/ZeroMQ.
        Here, we mock the telemetry stream.
        """
        print(f"Starting Shadow Twin for {machine_id}...")
        self.is_running = True
        
        # 1. Pre-Calculate Ideal Trajectory
        print("Calculating Ideal Trajectory...")
        sim_result = self.oracle.simulate(bytecode_program)
        expected_energy = sim_result['energy_j']
        print(f"Expected Energy: {expected_energy}J")
        
        # 2. Real-Time Loop
        step = 0
        max_steps = 10
        
        while self.is_running and step < max_steps:
            time.sleep(0.1) # Simulate tick
            step += 1
            
            # Mock Real Telemetry (Drifting over time)
            real_temp = 210.0 + (step * 2.0) # Deterministic Drift: +2C per step
            real_x = 100.0
            real_y = 50.0
            
            visual_state = {
                "x": real_x,
                "y": real_y,
                "temp": real_temp,
                "timestamp": time.time()
            }
            
            # Mock Ideal State (Constant for this simple test)
            simulation_state = {
                "x": 100.0,
                "y": 50.0,
                "temp": 210.0
            }
            
            # 3. Monitor
            monitor_result = self.shield.monitor_runtime(visual_state, simulation_state)
            
            if monitor_result['anomaly']:
                print(f"[STEP {step}] 🚨 ANOMALY DETECTED: {monitor_result['alerts']}")
                # In production: Trigger E-STOP
                # self.trigger_estop()
            else:
                print(f"[STEP {step}] ✅ System Nominal. Temp: {real_temp:.1f}C")

        print("Shadow Twin Loop Complete.")

    def run_predictive_loop(self, initial_state, duration_s=10):
        """
        Runs a predictive monitoring session.
        Input: initial_state { temp, power }
        """
        print(f"Starting Predictive Twin (Duration: {duration_s}s)...")
        self.is_running = True
        start_time = time.time()
        
        horizons = [1, 5, 15, 60, 300, 900, 3600] # 1s to 1h
        
        while self.is_running and (time.time() - start_time) < duration_s:
            current_state = initial_state.copy()
            # Simulate slight fluctuation in current state
            current_state['temp'] += random.uniform(-0.1, 0.1)
            
            print(f"\n[T+{int(time.time() - start_time)}s] Current Temp: {current_state['temp']:.2f}C")
            
            predictions = {}
            for h in horizons:
                pred = self.oracle.predict_horizon(current_state, h)
                predictions[f"{h}s"] = pred
                print(f"  -> +{h}s: {pred['predicted_temp']}C (Conf: {pred['confidence']})")
                
            time.sleep(1.0) # 1Hz update rate

        print("Predictive Loop Complete.")

if __name__ == "__main__":
    runtime = ShadowRuntime()
    program = [{"op": "OP_MOVE", "params": {"x": 100, "y": 50}}]
    runtime.run_shadow_loop(program)
