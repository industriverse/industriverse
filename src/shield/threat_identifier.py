import sys
import os
import json

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.safety.glyph_safety import GlyphSafetyAnalyzer
from src.safety.bytecode_sanitizer import BytecodeSanitizer
from src.simulation.simulation_oracle import SimulationOracle
from src.vision.vision_delta_detector import VisionDeltaDetector

class ThreatIdentifier:
    """
    AI Shield v3 - Gate 8: Threat Identifier (The Core).
    Fuses all safety gates into a single decision engine.
    """
    def __init__(self):
        self.glyph_analyzer = GlyphSafetyAnalyzer()
        self.bytecode_sanitizer = BytecodeSanitizer()
        self.oracle = SimulationOracle()
        self.delta_detector = VisionDeltaDetector()
        
    def scan_plan(self, glyphs=None, bytecode=None):
        """
        Static/Predictive Scan.
        Input: glyphs (list) OR bytecode (list)
        Output: { safe: bool, risks: [], mitigated_plan: ... }
        """
        risks = []
        mitigated_bytecode = bytecode
        
        # 1. Glyph Layer (Static)
        if glyphs:
            glyph_result = self.glyph_analyzer.analyze(glyphs)
            if not glyph_result['safe']:
                risks.extend(glyph_result['issues'])
                
        # 2. Bytecode Layer (Sanitization)
        if bytecode:
            san_result = self.bytecode_sanitizer.sanitize(bytecode)
            mitigated_bytecode = san_result['sanitized_program']
            if san_result['modifications']:
                risks.append(f"Sanitized {len(san_result['modifications'])} instructions.")
                
        # 3. Simulation Layer (Predictive)
        if mitigated_bytecode:
            sim_result = self.oracle.simulate(mitigated_bytecode)
            # Check for thermodynamic risks
            if sim_result['avg_power_w'] > 200:
                risks.append(f"High Power Warning: {sim_result['avg_power_w']}W exceeds standard safety profile.")
                
        return {
            "safe": len(risks) == 0 or (len(risks) == 1 and "Sanitized" in risks[0]), # Sanitization is considered safe
            "risks": risks,
            "mitigated_bytecode": mitigated_bytecode
        }

    def monitor_runtime(self, visual_state, simulation_state):
        """
        Real-Time Scan.
        Input: Visual State vs Simulation State
        Output: { anomaly: bool, alerts: [] }
        """
        delta_result = self.delta_detector.detect_delta(visual_state, simulation_state)
        return {
            "anomaly": delta_result['delta_detected'],
            "alerts": delta_result['discrepancies']
        }

if __name__ == "__main__":
    shield = ThreatIdentifier()
    
    # Test Plan Scan
    glyphs = ["⊸C", "⊽0.5"]
    bytecode = [{"op": "OP_SPINDLE", "params": {"rpm": 15000}}]
    
    print("--- Scanning Plan ---")
    scan_result = shield.scan_plan(glyphs, bytecode)
    print(json.dumps(scan_result, indent=2))
    
    # Test Runtime Monitor
    print("\n--- Monitoring Runtime ---")
    v_state = {"x": 100, "y": 50, "temp": 210}
    s_state = {"x": 100, "y": 50, "temp": 215}
    monitor_result = shield.monitor_runtime(v_state, s_state)
    print(json.dumps(monitor_result, indent=2))
