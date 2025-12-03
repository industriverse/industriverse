from typing import Any
import asyncio
from src.scf.fertilization.cfr_logger import CFRLogger
from src.integrations.voice_engine import VoiceEngine
from src.security.uzkl_ledger import UnifiedZKLedger
from src.scf.integration.defense_adapter import SovereignDefenseAdapter
from src.orchestration.telos_classifier import TelosClassifier
from src.integrations.energy_api import EnergyAPI
from src.economics.negentropy_ledger import NegentropyLedger
from src.orchestration.chronos import Chronos
from src.orchestration.aletheia import AletheiaTruthLayer
from src.orchestration.factory_persona import FactoryPersonaManager
from src.orchestration.hydrator import ServiceHydrator
from src.research.research_controller import ResearchController
from src.research.entropy_oracle import EntropyOracle
from src.datahub.value_vault import ValueVault
from src.security.emergency_stop import EmergencyStop
from src.scf.fertilization.value_realization_engine import ValueRealizationEngine
from src.operations.dashboard_exporter import DashboardExporter

class TrifectaMasterLoop:
    """
    The Central Conscious Loop of the Sovereign Code Foundry.
    Orchestrates the cycle: Observe -> Orient -> Decide -> Build -> Verify -> Reward -> Store.
    """
    def __init__(self, context_root: Any, intent_engine: Any, builder_engine: Any, reviewer: Any, deployer: Any):
        self.context_root = context_root
        self.intent_engine = intent_engine
        self.builder = builder_engine
        self.reviewer = reviewer
        self.deployer = deployer
        self.cfr = CFRLogger() # The Scribe
        self.voice = VoiceEngine() # The Voice
        self.ledger = UnifiedZKLedger() # The Conscience
        self.defense = SovereignDefenseAdapter() # The Shield
        
        # Grand Challenge Integrations
        self.telos_classifier = TelosClassifier() # Self-Healing
        self.energy_api = EnergyAPI() # Thermo-Scheduling
        self.negentropy_ledger = NegentropyLedger() # Value Accounting
        
        # Dark Factory / Quadrality Integrations
        self.chronos = Chronos() # Timekeeper
        self.aletheia = AletheiaTruthLayer() # Truth Layer
        self.persona_manager = FactoryPersonaManager() # Factory Personality
        self.hydrator = ServiceHydrator() # Capsule Hydrator
        
        # Empeiria Haus / Research Engine Integrations
        self.research_controller = ResearchController() # The Research Brain
        self.research_controller.set_active(True) # Always active for SCF
        self.entropy_oracle = EntropyOracle() # Physics Metrics
        self.value_vault = ValueVault() # Trade Secret Storage
        self.emergency_stop = EmergencyStop() # The Red Button
        self.value_engine = ValueRealizationEngine() # ROI Calculator
        self.dashboard = DashboardExporter() # Metrics Exporter
        
        self.parameters = {}

    def set_parameters(self, params: dict):
        """
        Dynamically updates loop parameters (e.g., from Daemon Level).
        """
        self.parameters.update(params)

    async def cycle(self) -> Any:
        """
        Executes one full iteration of the conscious code generation loop.
        Includes Auto-Heal retry logic.
        """
        max_retries = 3
        attempt = 0
        
        while attempt < max_retries:
            try:
                # -1. Emergency Stop Check (The Red Button)
                if not self.emergency_stop.check_status():
                    print("🛑 [FATAL] EMERGENCY STOP ENGAGED. HALTING CYCLE.")
                    return {"status": "aborted", "reason": "EMERGENCY_STOP"}

                # 0. Defense Check (The Shield)
                integrity = self.defense.check_environment_integrity()
                if not integrity["safe_to_deploy"]:
                    self.voice.speak("Environment unsafe. Defense protocols active.")
                    print(f"🛡️ [DEFENSE] Threats detected: {integrity['threats']}")
                    
                    # Auto-Immune Response: Trigger Counter-Measure Generation
                    # We recursively call cycle() but with a forced intent to fix the threat.
                    # In a real system, we'd have a specific 'Defense Mode' to avoid infinite loops.
                    # For now, we return the threat info so the Daemon can decide.
                    return {
                        "status": "aborted", 
                        "reason": "unsafe_environment", 
                        "threats": integrity["threats"],
                        "recommendation": "TRIGGER_AUTO_IMMUNE_RESPONSE"
                    }

                # 0.5 Thermodynamic Scheduling Check (Challenge #3) & Persona Logic
                persona_config = self.persona_manager.get_config()
                price = self.energy_api.get_current_price()
                
                # Adjust threshold based on Persona
                # Higher bid_multiplier means we tolerate higher prices
                base_threshold = 0.15
                adjusted_threshold = base_threshold * persona_config['bid_multiplier_base']
                
                if price > adjusted_threshold: 
                    self.voice.speak(f"Energy price ${price:.2f} exceeds limit ${adjusted_threshold:.2f} for {self.persona_manager.current_persona}. Pausing.")
                    print(f"⚡ [KAIROS] Price ${price:.2f} > Limit ${adjusted_threshold:.2f}. Stance: {persona_config['emm_bias']}. Pausing.")
                    await asyncio.sleep(1) # Wait a bit
                    continue # Skip this cycle attempt


                # 1. Observe: Get Context Slab (Pulse + Memory)
                context_slab = await self.context_root.get_context_slab()
                
                # 2. Orient: Generate Intent based on Context
                intent = self.intent_engine.generate()
                spec = self.intent_engine.expand(intent)
                
                # Announce Intent
                self.voice.speak(f"I understand. Proceeding to {intent}.")
                
                # 3. Build: Generate Code (GenN)
                code = self.builder.build(spec)
                
                # 4. Verify: Review (PRIN + EBDM) & Simulate (TNN)
                review_result = self.reviewer.review(code)
                
                if review_result["verdict"] == "REJECT":
                    # Record failure to CFR
                    self.cfr.record(intent, code, review_result)
                    
                    # Challenge #2: Self-Healing Diagnosis
                    critique = review_result["critique"]
                    cat, conf, action = self.telos_classifier.classify_failure(critique)
                    print(f"🧠 [TELOS] Diagnosis: {cat} -> Action: {action}")
                    
                    if action == "TRIGGER_ALETHEIA_RECALIBRATION":
                        self.voice.speak("Drift detected. Recalibrating.")
                        # In a real system, we'd trigger the DriftCanceller here
                        
                    self.voice.speak("Optimization rejected. Refining approach.")
                    return {"status": "rejected", "reason": critique, "telos_action": action}

                # 5. Deploy
                result = self.deployer.deploy(code, context=context_slab)
                
                # 5.5 Aletheia Truth Check (The Sensorium)
                # Validate that the deployment didn't break physics
                is_valid, drift, msg = self.aletheia.validate({"name": intent, "id": "current_cycle"}, {"temperature": 500}) # Mock prediction
                if not is_valid:
                     self.voice.speak(f"Physics Violation Detected. {msg}")
                     print(f"👁️ [ALETHEIA] {msg}")
                     # In a real system, we might rollback here.
                     # For now, we just log it.
                
                # 6. Fertilization (Record Fossil & Value)
                # Calculate Realized Value
                deployment_result = {
                    "energy_trace_summary": {"joules_saved": 0.0}, # Will be updated by thermo_metrics later
                    "operational_impact": {"downtime_avoided_sec": 0.0} # Mock for now
                }
                value_metrics = self.value_engine.compute_value(deployment_result)
                
                # Enrich Review Result with Value
                review_result["value_metrics"] = value_metrics
                
                self.cfr.record(intent, code, review_result)
                
                # 7. Update Dashboard
                self.dashboard.update_model_metrics(
                    ebdm_loss=0.1, # Mock
                    tnn_residual=0.05, # Mock
                    gen_n_ppx=12.0 # Mock
                )
                self.dashboard.update_operational_metrics(
                    fossils_added=1,
                    negentropy_added=value_metrics["negentropy_credits"]
                )
                
                # 7. Empeiria Haus Research Loop (The Discovery Engine)
                # Calculate Thermodynamic Value
                # Mocking hardware data for now
                trinity_packet = {
                    "components": {
                        "industriverse": {"capsule_count": 1}, # We deployed 1 "capsule" (code block)
                        "thermodynasty": {"power_draw_w": 150.0, "edcoc_temp_c": 45.0} # Mock hardware stats
                    },
                    "payload": {
                        "safety_score": 0.99, # Assumed safe if deployed
                        "confidence": 0.95
                    },
                    "source": "SCF_Master_Loop",
                    "energy_state": {"entropy": 0.1} # Low entropy (success)
                }
                
                thermo_metrics = self.entropy_oracle.calculate_thermodynamic_value(trinity_packet)
                print(f"🔬 [EMPEIRIA] Negentropy Score: {thermo_metrics['negentropy_score']} {thermo_metrics['unit']}")
                
                # Store High-Value Secret
                insight = {
                    "intent": intent,
                    "code_hash": hash(code),
                    "thermodynamics": thermo_metrics
                }
                if self.value_vault.store_secret(insight):
                    self.voice.speak("High value trade secret archived.")
                
                # Trigger Research Event (Feed the Orchestrator)
                # We enrich the packet with the calculated metrics
                trinity_packet["energy_state"]["entropy"] = 1.0 / (thermo_metrics["negentropy_score"] + 0.1) # Inverse of negentropy
                self.research_controller.analyze_packet(trinity_packet)

                # 8. Conscience (Mint ZK Proof)
                proof = self.ledger.generate_proof(
                    domain="CODE_GENERATION",
                    data={"intent": intent, "code_hash": str(hash(code))},
                    metadata={"verdict": "APPROVE", "score": review_result.get("score")}
                )
                
                # Challenge #10: Negentropy Accounting
                # We assume a successful deployment reduces entropy (adds value)
                entropy_reduction = review_result.get("score", 0.5) * 10 # Mock calculation
                self.negentropy_ledger.record_transaction("SCF_Master_Loop", intent, entropy_reduction)
                
                self.voice.speak("Deployment successful. Optimization active.")
                
                return {
                    "status": "deployed",
                    "result": result,
                    "intent": intent,
                    "review": review_result,
                    "proof_id": proof.id
                }
            except Exception as e:
                attempt += 1
                print(f"⚠️ Cycle Error (Attempt {attempt}/{max_retries}): {e}")
                if attempt >= max_retries:
                    return {"status": "error", "error": str(e)}
                await asyncio.sleep(0.1 * attempt) # Backoff
