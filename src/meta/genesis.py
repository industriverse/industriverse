import os
import sys
import uuid
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.marketing.solution_architect import SolutionArchitect

class GenesisEngine:
    """
    The Self-Coding Architect.
    Takes a natural language request, uses SolutionArchitect to identify modules,
    and dynamically generates an executable Python script to solve the problem.
    """
    def __init__(self):
        self.architect = SolutionArchitect()
        self.generated_scripts_dir = os.path.join(os.path.dirname(__file__), '../../scripts/generated')
        os.makedirs(self.generated_scripts_dir, exist_ok=True)

    def generate_solution(self, user_request):
        """
        Generates a Python script for the given request.
        """
        print(f"🔵 Genesis: Analyzing request '{user_request}'...")
        solution = self.architect.map_request_to_solution(user_request)
        
        if not solution or "Consultation_Required" in solution['modules']:
            print("❌ Genesis: Could not map request to a standard solution.")
            return None

        print(f"✅ Genesis: Mapped to modules: {solution['modules']}")
        
        # Generate Code
        script_content = self._create_script_template(user_request, solution)
        
        # Save File
        filename = f"solution_{int(time.time())}_{uuid.uuid4().hex[:8]}.py"
        filepath = os.path.join(self.generated_scripts_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(script_content)
            
        print(f"🚀 Genesis: Solution generated at {filepath}")
        return filepath

    def _create_script_template(self, request, solution):
        modules = solution['modules']
        imports = []
        init_lines = []
        loop_lines = []
        
        # Dynamic Import Logic
        if "DriftCanceller" in modules:
            imports.append("from src.orchestration.drift_canceller import DriftCanceller")
            init_lines.append("    canceller = DriftCanceller()")
            loop_lines.append("        # DriftCanceller Logic")
            loop_lines.append("        correction, drift = canceller.apply_correction([100, 50, 25], {'temperature': 35.0})")
            loop_lines.append("        print(f'[DriftCanceller] Applied Correction: {correction}')")
            
        if "VisualTwin" in modules:
            imports.append("from src.vision.visual_twin import VisualTwin")
            init_lines.append("    twin = VisualTwin()")
            loop_lines.append("        # VisualTwin Logic")
            loop_lines.append("        twin.ingest_multimodal({'temperature': 35.0, 'vibration': 0.02})")
            
        if "EBDMForecaster" in modules:
            imports.append("from src.models.ebdm_forecaster import EBDMForecaster")
            init_lines.append("    forecaster = EBDMForecaster()")
            loop_lines.append("        # EBDM Logic")
            loop_lines.append("        forecast = forecaster.analyze({'temperature': 35.0, 'vibration': 0.02})")
            loop_lines.append("        print(f'[EBDM] Forecast: {forecast}')")

        if "RoboCOIN" in modules:
            imports.append("from src.robotics.robocoin_client import RoboCOINClient")
            init_lines.append("    robocoin = RoboCOINClient()")
            loop_lines.append("        # RoboCOIN Logic")
            loop_lines.append("        robocoin.load_dataset('worker_001')")

        # Construct Script
        script = f"""import sys
import os
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

{chr(10).join(imports)}

def run_solution():
    print("############################################################")
    print("#   GENESIS GENERATED SOLUTION                             #")
    print("#   Request: {request}")
    print("############################################################")

    # Initialize Modules
{chr(10).join(init_lines)}

    print("🔵 Starting Execution Loop...")
    for i in range(3):
        print(f"\\n[Step {{i+1}}]")
{chr(10).join(loop_lines)}
        time.sleep(0.5)

    print("\\n✅ Execution Complete.")

if __name__ == "__main__":
    run_solution()
"""
        return script

if __name__ == "__main__":
    genesis = GenesisEngine()
    genesis.generate_solution("fix thermal drift")
