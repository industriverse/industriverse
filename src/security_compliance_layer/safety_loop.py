import time
import logging
from src.overseer.nanochat.swarm import NanochatSwarm
from src.core_ai_layer.swi_reasoning.engine import SwiReasoningEngine
from src.overseer.ace.memory_cortex import MemoryCortex

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SafetyLoop")

class MultiAgentSafetyLoop:
    def __init__(self):
        self.swarm = NanochatSwarm(size=5)
        self.reasoning = SwiReasoningEngine()
        self.memory = MemoryCortex()
        self.running = False

    def start(self):
        self.running = True
        logger.info("🛡️  Multi-Agent Safety Loop Started")
        try:
            while self.running:
                self.tick()
                time.sleep(1) # 1Hz loop
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.running = False
        logger.info("🛑 Safety Loop Stopped")

    def tick(self):
        # 1. Heartbeat Sync
        if not self.swarm.heartbeat_sync():
            logger.warning("⚠️  Swarm desync detected! Initiating recovery...")
        
        # 2. Mock Context (In reality, this comes from Event Bus)
        context = {"system_load": "normal", "network_traffic": "low"}
        
        # 3. Swarm Consensus
        threat_level = self.swarm.consensus_check(context)
        
        if threat_level > 0.5:
            logger.warning(f"🚨 Elevated Threat Level: {threat_level}")
            
            # 4. SwiReasoning Analysis
            analysis = self.reasoning.reason(context)
            logger.info(f"🧠 Reasoning Result: {analysis['decision']} ({analysis['method']})")
            
            # 5. ACE Response
            if analysis['decision'] != "safe":
                playbook = self.memory.get_playbook("general_threat")
                logger.info(f"📚 Executing Playbook: {playbook}")
                self.memory.add_episode({"context": context, "analysis": analysis, "response": playbook})

if __name__ == "__main__":
    loop = MultiAgentSafetyLoop()
    # Run for a few seconds for demonstration
    import threading
    t = threading.Thread(target=loop.start)
    t.start()
    time.sleep(5)
    loop.stop()
    t.join()
