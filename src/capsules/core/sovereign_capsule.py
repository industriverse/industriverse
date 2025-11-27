"""
Sovereign Capsule Base Class.
Enforces the 12 Genesis Directives for the 27 Sovereign Capsules.
"""

import os
import yaml
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from .manifest import CapsuleManifest, PRINConfig, SafetyBudget, MeshRouting, UTIDPattern

logger = logging.getLogger(__name__)

class SovereignCapsule(ABC):
    """
    Base class for all Sovereign Capsules.
    Acts as a 'thermodynamic organ' with standardized lifecycle and interfaces.
    """

    def __init__(self, capsule_dir: str):
        self.capsule_dir = capsule_dir
        self.capsule_id = os.path.basename(capsule_dir)
        self.manifest: Optional[CapsuleManifest] = None
        self.topology: Dict[str, Any] = {}
        self.energy_prior: Dict[str, Any] = {}
        self.proof_schema: Dict[str, Any] = {}
        
        # Load all configurations on init (Directive 01-09)
        self._load_configurations()

    def _load_configurations(self):
        """Load YAML/JSON configs from standard paths."""
        try:
            # Load PRIN (Directive 04)
            with open(os.path.join(self.capsule_dir, "prin.yaml")) as f:
                prin_data = yaml.safe_load(f)
            
            # Load Safety (Directive 06)
            with open(os.path.join(self.capsule_dir, "runtime", "safety.json")) as f:
                safety_data = json.load(f)
                
            # Load Routing (Directive 09)
            with open(os.path.join(self.capsule_dir, "mesh", "routing.json")) as f:
                routing_data = json.load(f)
                
            # Load UTID Patterns (Directive 08)
            with open(os.path.join(self.capsule_dir, "identity", "utid_patterns.yaml")) as f:
                utid_data = yaml.safe_load(f)

            self.manifest = CapsuleManifest(
                capsule_id=self.capsule_id,
                version="v1", # TODO: load from file
                prin=PRINConfig(**prin_data),
                safety=SafetyBudget(**safety_data),
                routing=MeshRouting(**routing_data),
                utid=UTIDPattern(**utid_data)
            )

            # Load Topology (Directive 01)
            with open(os.path.join(self.capsule_dir, "topology.yaml")) as f:
                self.topology = yaml.safe_load(f)

            # Load Energy Prior (Directive 03)
            with open(os.path.join(self.capsule_dir, "priors", "energy_prior.json")) as f:
                self.energy_prior = json.load(f)

            # Load Proof Schema (Directive 07)
            with open(os.path.join(self.capsule_dir, "proof", "schema.json")) as f:
                self.proof_schema = json.load(f)

            logger.info(f"Capsule {self.capsule_id} loaded successfully.")

        except Exception as e:
            logger.error(f"Failed to load capsule {self.capsule_id}: {e}")
            raise

    # --- Lifecycle Methods (Directive 10) ---

    def ignite(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Step 1: Ignition - Initialize state from params."""
        logger.info(f"Igniting {self.capsule_id}...")
        return {"status": "ignited", "capsule_id": self.capsule_id}

    def materialize(self):
        """Step 2: Materialize - Instantiate resources."""
        pass

    def phase_lock(self):
        """Step 3: Phase Lock - Connect to Energy Atlas."""
        pass

    def thermo_loop(self, steps: int = 10):
        """Step 4: Thermodynamic Search (Directive 03)."""
        logger.info(f"Running thermo loop for {self.capsule_id}...")
        
        # Determine mode from manifest or params
        mode = self.manifest.prin.mode if hasattr(self.manifest.prin, 'mode') else "sampling"
        
        if mode == "sampling":
            from ebm_runtime.service import sample
            # Create initial state (placeholder)
            initial_state = {"state_vector": [0.0] * 8} # Should be loaded or random
            
            result = sample(
                prior_name=self.manifest.energy_prior,
                initial_state=initial_state,
                sampler={"type": "langevin", "steps": steps}
            )
            return result
            
        elif mode == "simulation":
            # Load TNN class dynamically
            import importlib
            module_name, class_name = self.manifest.tnn_class.rsplit(".", 1)
            module = importlib.import_module(module_name)
            TNNClass = getattr(module, class_name)
            tnn = TNNClass()
            
            # Placeholder state
            state = {"B": None, "v": None, "rho": 1.0} # Needs proper init
            control = {}
            
            result = tnn.simulate(state, control, dt=0.01, steps=steps)
            return result
            
        else:
            logger.warning(f"Unknown mode {mode} for {self.capsule_id}")
            return {}

    def run_policy(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Step 6: Agent Policy Execution (Directive 05)."""
        # Dynamically load agent if not already loaded
        if not hasattr(self, 'agent'):
            import importlib.util
            agent_path = os.path.join(self.capsule_dir, "agent", "behavior.py")
            spec = importlib.util.spec_from_file_location("behavior", agent_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Heuristic to find agent class
            for attr_name in dir(module):
                if attr_name.endswith("Agent") and attr_name != "Agent":
                    AgentClass = getattr(module, attr_name)
                    self.agent = AgentClass(self.manifest)
                    break
            else:
                raise ValueError(f"No Agent class found in {agent_path}")

        return self.agent.policy(observation)

    def emit_proof(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Step 7: Proof Generation (Directive 07)."""
        # Placeholder for proof generation logic
        return {
            "proof_hash": "mock_hash_" + self.capsule_id,
            "schema": self.proof_schema.get("proof_type", "generic"),
            "timestamp": 1234567890
        }

    def get_ui_packet(self) -> Dict[str, Any]:
        """Directive 11: Feed Dyson Sphere UI."""
        return {
            "capsule_id": self.capsule_id,
            "entropy": 0.1, # Placeholder
            "status": "active"
        }
