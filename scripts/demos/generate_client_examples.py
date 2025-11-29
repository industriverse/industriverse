import sys
import os
import json
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))

from models.tge_core import ThermodynamicGenerativeExecutor
from models.pssm_core import PhysicsSovereignSkillModel
from models.zkmm_core import ZeroKnowledgeManufacturingModel
from models.pem_core import PredictiveEntropyModel
from models.eapm_core import EgocentricActionProjector
from models.dce_core import DistributedCapsuleEconomy
from models.mfem_core import MultiModalFusionEncoder
from models.pop_core import PhysicsOverlayPerception
# HRAE is JS, so we will simulate its output here for the Python report

class ClientExampleGenerator:
    def __init__(self):
        self.output_dir = "examples/client_deliverables"
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"🚀 Generating Client Examples in {self.output_dir}...")

    def save_deliverable(self, client_name, model_name, data):
        filename = f"{client_name}_{model_name}.json"
        path = os.path.join(self.output_dir, filename)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"   ✅ Generated: {filename}")

    def generate_all(self):
        # 1. TGE: Aerospace (Turbine Blade)
        tge = ThermodynamicGenerativeExecutor()
        tge_out = tge.generate_toolpath({"part": "Turbine_Blade_X9", "material": "Titanium-6Al-4V"})
        self.save_deliverable("AerospaceCorp", "TGE_Toolpath", tge_out)

        # 2. PSSM: Automotive (High-Speed Welding)
        pssm = PhysicsSovereignSkillModel()
        pssm_out = pssm.evolve_skill("SpotWeld_v4", 0.99)
        self.save_deliverable("AutoGiant", "PSSM_SkillCert", pssm_out)

        # 3. ZKMM: Pharma (Catalyst Mix)
        zkmm = ZeroKnowledgeManufacturingModel()
        zkmm_out = zkmm.generate_proof({"recipe": "Secret_Catalyst_Formula_7"})
        self.save_deliverable("PharmaInc", "ZKMM_Proof", zkmm_out)

        # 4. PEM: Energy Grid (Transformer Load)
        pem = PredictiveEntropyModel()
        for val in [0.1, 0.2, 0.3, 0.5, 0.8]:
            pem.update(val)
        pem_out = pem.predict_horizon(60) # Predict 60s out
        self.save_deliverable("GridCo", "PEM_Forecast", pem_out)

        # 5. EAPM: Logistics (Box Lifting)
        eapm = EgocentricActionProjector()
        eapm_out = eapm.predict_operator_action("video_chunk_logistics_001.mp4")
        self.save_deliverable("LogisticsGlobal", "EAPM_SafetyReport", eapm_out)

        # 6. DCE: Semiconductor (Wafer Etch)
        dce = DistributedCapsuleEconomy()
        bids = dce.request_bid("Wafer_Etch_Lot_404")
        best_bid = bids[0] # Simplification
        dce_out = dce.execute_transaction(best_bid)
        self.save_deliverable("SemiFab", "DCE_BidTransaction", dce_out)

        # 7. MFEM: Heavy Machinery (Excavator)
        mfem = MultiModalFusionEncoder()
        mfem_out = mfem.encode({"state_vector": {"x": 10, "y": 20, "temp": 80}}, {"rpm": 2000, "load": 0.8, "vibration": 0.05})
        self.save_deliverable("HeavyMachines", "MFEM_StateEmbedding", mfem_out)

        # 8. HRAE: Consumer Electronics (Phone Case) - Simulated
        hrae_out = {
            "client": "PhoneMaker",
            "task": "CNC_Phone_Case_Unibody",
            "status": "LOOP_CLOSED",
            "profit_verified": True,
            "cycle_time": 14.2
        }
        self.save_deliverable("PhoneMaker", "HRAE_AutopilotLog", hrae_out)

        # 9. POP: Structural Health (Bridge Monitor)
        pop = PhysicsOverlayPerception()
        # Mock vector field: [{"x": 10, "y": 10, "mag": 15}, ...]
        field = [{"x": 10, "y": 10, "mag": 15}, {"x": 20, "y": 50, "mag": 60}] # High stress
        pop_out = pop.analyze_field(field)
        self.save_deliverable("InfraStruct", "POP_AnomalyMap", pop_out)

if __name__ == "__main__":
    gen = ClientExampleGenerator()
    gen.generate_all()
