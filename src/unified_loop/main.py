import asyncio
import random
from src.unified_loop.orchestrator import UnifiedLoopOrchestrator

async def main():
    print("=== INITIALIZING INDUSTRIVERSE SINGULARITY LOOP ===")
    orchestrator = UnifiedLoopOrchestrator()
    
    # Simulate a DOME Signal (Vibration Anomaly)
    mock_signal = {
        "source_id": "turbine_alpha_001",
        "type": "vibration",
        "value": 55.4, # Hz, abnormal
        "timestamp": "2025-11-27T10:00:00Z"
    }
    
    print("\n--- STARTING SIMULATION ---")
    await orchestrator.run_loop(mock_signal)
    print("\n--- SIMULATION COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(main())
