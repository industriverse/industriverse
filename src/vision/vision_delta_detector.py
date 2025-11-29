class VisionDeltaDetector:
    """
    AI Shield v3 - Gate 7: Vision Delta Detector.
    Compares 'What I See' (Visual Twin) vs 'What I Expect' (Simulation Oracle).
    """
    def __init__(self, tolerance=5.0):
        self.tolerance_mm = tolerance
        self.tolerance_temp = 10.0

    def detect_delta(self, visual_state, simulation_state):
        """
        Input: 
            visual_state: { x: 100, y: 50, temp: 210 }
            simulation_state: { x: 100, y: 50, temp: 215 }
        Output: { delta_detected: bool, discrepancies: [] }
        """
        discrepancies = []
        
        # 1. Position Check
        dx = abs(visual_state.get('x', 0) - simulation_state.get('x', 0))
        dy = abs(visual_state.get('y', 0) - simulation_state.get('y', 0))
        
        if dx > self.tolerance_mm:
            discrepancies.append(f"Position X Mismatch: Saw {visual_state['x']}, Expected {simulation_state['x']}")
        if dy > self.tolerance_mm:
            discrepancies.append(f"Position Y Mismatch: Saw {visual_state['y']}, Expected {simulation_state['y']}")
            
        # 2. Thermal Check
        d_temp = abs(visual_state.get('temp', 0) - simulation_state.get('temp', 0))
        if d_temp > self.tolerance_temp:
            discrepancies.append(f"Thermal Mismatch: Saw {visual_state['temp']}C, Expected {simulation_state['temp']}C")
            
        # 3. Visual Anomalies (Spaghetti)
        if visual_state.get('spaghetti_detected'):
            discrepancies.append("CRITICAL: Spaghetti Failure Detected visually.")

        return {
            "delta_detected": len(discrepancies) > 0,
            "discrepancies": discrepancies
        }

if __name__ == "__main__":
    detector = VisionDeltaDetector()
    v_state = {"x": 100, "y": 50, "temp": 210, "spaghetti_detected": False}
    s_state = {"x": 100, "y": 50, "temp": 215} # Match
    print(detector.detect_delta(v_state, s_state))
    
    v_state_bad = {"x": 120, "y": 50, "temp": 210, "spaghetti_detected": True}
    print(detector.detect_delta(v_state_bad, s_state))
