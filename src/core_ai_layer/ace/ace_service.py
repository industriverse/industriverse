import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .schema import ACERequest, ACEResponse, ReflectionResult
from .reflection_engine import ReflectionEngine
from .playbook_manager import PlaybookManager
from .memory_logger import ACEMemoryLogger
from src.proof_core.integrity_layer import record_reasoning_edge

# Thermodynamic Integration
from src.core.energy_atlas.atlas_core import EnergyAtlas

class ACEService:
    """
    Agentic Context Engineering (ACE) Service.
    Orchestrates Reflection, Playbooks, and Memory for the Trifecta loop.
    Now instrumented with Thermodynamic Telemetry.
    """
    
    def __init__(self):
        self.playbook_manager = PlaybookManager()
        self.reflection_engine = ReflectionEngine(self.playbook_manager)
        self.memory_logger = ACEMemoryLogger()
        
        # Initialize Energy Atlas (Mocked for now)
        self.energy_atlas = EnergyAtlas(use_mock=True)
        try:
            self.energy_atlas.load_manifest("src/core/energy_atlas/sample_manifest.json")
        except Exception as e:
            logging.warning(f"Could not load sample manifest: {e}")

    async def process_request(self, request: ACERequest) -> ACEResponse:
        """
        Process an ACE request: Reflect -> Plan -> Log -> Telemetry.
        """
        start_time = datetime.now()
        
        # 1. Playbook Selection (Directly from intent)
        playbook = self.playbook_manager.get_playbook(request.intent)
        
        # 2. Pre-computation Reflection (Mocked for now)
        reflection = ReflectionResult(
            intent=request.intent,
            context_analysis=f"Analyzed {len(request.context)} context items.",
            suggested_strategies=playbook.strategies if playbook else []
        )
        
        # 3. Memory Logging
        # self.memory_logger.log_interaction(request, reflection)
        
        # 4. Thermodynamic Telemetry + Proof/UTID lineage
        # Estimate energy cost based on complexity
        # E = base + complexity * factor
        complexity = len(request.context) / 1000.0 # normalized
        energy_cost = 0.001 + complexity * 0.005 # Joules (mocked)
        
        self._report_thermodynamic_cost("ace_planning", energy_cost)

        utid = getattr(request, "utid", "UTID:REAL:unknown")
        await record_reasoning_edge(
            utid=utid,
            domain="ace_planning",
            node_id="ace_service",
            inputs={"context": request.context},
            outputs={"reflection": reflection.dict(), "playbook": getattr(playbook, "playbook_id", None)},
            metadata={"energy_joules": energy_cost, "status": "completed"},
        )
        
        return ACEResponse(
            request_id=request.request_id,
            reflection=reflection,
            selected_playbook=playbook,
            timestamp=datetime.now()
        )

    def _report_thermodynamic_cost(self, action_type: str, energy_joules: float):
        """
        Report energy cost to the Energy Atlas.
        In a real system, this would update the 'Heat Map' of the running node.
        """
        # For now, we just log it. In Phase 7 Task W, this will stream to "The Pulse".
        logging.info(f"THERMODYNAMIC_TELEMETRY: Action={action_type} Energy={energy_joules:.6f}J")
        
        # Update a mock node in the Atlas to simulate heating up
        # We'll pick a random node to attribute this work to
        target_node = "gpu_h100_01" # Hardcoded for demo
        
        # TODO: Update Atlas state (e.g., increase temperature)
        # self.energy_atlas.update_node_state(target_node, energy_joules)

def create_ace_service() -> ACEService:
    return ACEService()
