import asyncio
import logging
from typing import List, Dict
from src.unified_loop.orchestrator import UnifiedLoopOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GrandDemoSuite")

SCENARIOS = {
    "Energy": [
        {"id": "E1", "dataset": "fusion_v1", "goal": "Stabilize Plasma", "guardrails": {"max_energy": 10.0}},
        {"id": "E2", "dataset": "grid_v1", "goal": "Balance Frequency", "guardrails": {"max_energy": 5.0}},
        {"id": "E3", "dataset": "battery_v1", "goal": "Prevent Runaway", "guardrails": {"max_energy": 8.0}},
        {"id": "E4", "dataset": "solar_v1", "goal": "Maximize Yield", "guardrails": {"max_energy": 12.0}},
        {"id": "E5", "dataset": "wind_v1", "goal": "Optimize Pitch", "guardrails": {"max_energy": 7.0}},
    ],
    "Manufacturing": [
        {"id": "M1", "dataset": "casting_v1", "goal": "Reduce Cracks", "guardrails": {"max_energy": 15.0}},
        {"id": "M2", "dataset": "welding_v1", "goal": "Uniform Seam", "guardrails": {"max_energy": 6.0}},
        {"id": "M3", "dataset": "assembly_v1", "goal": "Minimize Cycle Time", "guardrails": {"max_energy": 4.0}},
        {"id": "M4", "dataset": "qa_v1", "goal": "Detect Defects", "guardrails": {"max_energy": 3.0}},
        {"id": "M5", "dataset": "logistics_v1", "goal": "Route Opt", "guardrails": {"max_energy": 2.0}},
    ],
    "Robotics": [
        {"id": "R1", "dataset": "arm_v1", "goal": "Smooth Trajectory", "guardrails": {"max_energy": 5.0}},
        {"id": "R2", "dataset": "drone_v1", "goal": "Stable Hover", "guardrails": {"max_energy": 8.0}},
        {"id": "R3", "dataset": "rover_v1", "goal": "Path Planning", "guardrails": {"max_energy": 6.0}},
        {"id": "R4", "dataset": "humanoid_v1", "goal": "Balance", "guardrails": {"max_energy": 9.0}},
        {"id": "R5", "dataset": "swarm_v1", "goal": "Cohesion", "guardrails": {"max_energy": 7.0}},
    ],
    "Compute": [
        {"id": "C1", "dataset": "datacenter_v1", "goal": "Cooling Opt", "guardrails": {"max_energy": 10.0}},
        {"id": "C2", "dataset": "chip_v1", "goal": "Leakage Reduction", "guardrails": {"max_energy": 4.0}},
        {"id": "C3", "dataset": "network_v1", "goal": "Latency Min", "guardrails": {"max_energy": 3.0}},
        {"id": "C4", "dataset": "storage_v1", "goal": "Data Integrity", "guardrails": {"max_energy": 2.0}},
        {"id": "C5", "dataset": "crypto_v1", "goal": "Hash Efficiency", "guardrails": {"max_energy": 11.0}},
    ],
    "Physics": [
        {"id": "P1", "dataset": "plasma_v1", "goal": "Confinement", "guardrails": {"max_energy": 20.0}},
        {"id": "P2", "dataset": "fluid_v1", "goal": "Laminar Flow", "guardrails": {"max_energy": 5.0}},
        {"id": "P3", "dataset": "quantum_v1", "goal": "Coherence", "guardrails": {"max_energy": 1.0}},
        {"id": "P4", "dataset": "material_v1", "goal": "Superconductivity", "guardrails": {"max_energy": 2.0}},
        {"id": "P5", "dataset": "astro_v1", "goal": "Orbit Stability", "guardrails": {"max_energy": 0.5}},
    ]
}

async def run_suite():
    orchestrator = UnifiedLoopOrchestrator()
    results = []
    
    print("==================================================")
    print("       THE GRAND DEMO SUITE (25 SCENARIOS)        ")
    print("==================================================")
    
    for category, scenarios in SCENARIOS.items():
        print(f"\n>>> CATEGORY: {category}")
        for s in scenarios:
            print(f"  Running Scenario {s['id']}: {s['goal']} ({s['dataset']})...")
            
            config = {
                "client_id": f"demo_{s['id']}",
                "targets": [s['goal']],
                "guardrails": s['guardrails']
            }
            
            try:
                capsules = await orchestrator.run_campaign(s['id'], [s['dataset']], config)
                if capsules:
                    c = capsules[0]
                    print(f"    [SUCCESS] Minted {c.uri}")
                    results.append({"id": s['id'], "status": "PASS", "uri": str(c.uri)})
                else:
                    print(f"    [WARN] No capsule produced.")
                    results.append({"id": s['id'], "status": "EMPTY", "uri": "N/A"})
            except Exception as e:
                print(f"    [FAIL] Error: {e}")
                results.append({"id": s['id'], "status": "FAIL", "uri": "N/A"})
                
    print("\n==================================================")
    print("                 SUITE SUMMARY                    ")
    print("==================================================")
    passed = len([r for r in results if r['status'] == 'PASS'])
    print(f"Total Scenarios: 25")
    print(f"Passed: {passed}")
    print(f"Failed: {25 - passed}")
    
    if passed == 25:
        print("\nALL SYSTEMS NOMINAL. READY FOR DEPLOYMENT.")
    else:
        print("\nWARNING: SOME SYSTEMS FAILED.")

if __name__ == "__main__":
    asyncio.run(run_suite())
