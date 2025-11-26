import time
import json
import threading
import queue
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class MockNetwork:
    def __init__(self):
        self.nodes = {} # id -> queue

    def register(self, node_id, q):
        self.nodes[node_id] = q
        logger.info(f"[Network] Registered node: {node_id}")

    def send(self, sender_id, target_id, message):
        if target_id in self.nodes:
            logger.info(f"[Network] Routing: {sender_id} -> {target_id} | Msg: {message['type']}")
            time.sleep(0.2) # Network latency
            self.nodes[target_id].put((sender_id, message))
        else:
            logger.error(f"[Network] Target {target_id} not found!")

network = MockNetwork()

class CapsuleNode:
    def __init__(self, node_id, role):
        self.node_id = node_id
        self.role = role
        self.inbox = queue.Queue()
        network.register(node_id, self.inbox)
        self.running = True

    def run(self):
        while self.running:
            try:
                sender_id, msg = self.inbox.get(timeout=1.0)
                self.handle_message(sender_id, msg)
            except queue.Empty:
                continue

    def handle_message(self, sender_id, msg):
        logger.info(f"[{self.node_id}] Received {msg['type']} from {sender_id}")
        
        if self.role == "Refiner" and msg['type'] == "MATERIAL_READY":
            logger.info(f"[{self.node_id}] Acknowledging receipt. Starting refinement process...")
            time.sleep(1)
            response = {"type": "ACK_START", "status": "OK"}
            network.send(self.node_id, sender_id, response)

        elif self.role == "Miner" and msg['type'] == "ACK_START":
            logger.info(f"[{self.node_id}] Transfer confirmed. Batch {msg['status']}.")
            self.running = False # End demo for miner

    def send_material(self, target_id):
        logger.info(f"[{self.node_id}] Batch complete. Signaling {target_id}...")
        msg = {"type": "MATERIAL_READY", "batch_id": "BATCH-99", "quantity": 500}
        network.send(self.node_id, target_id, msg)

def run():
    print("\n" + "="*60)
    print(" DEMO 5: CAPSULE-TO-CAPSULE COMMUNICATION")
    print("="*60 + "\n")

    miner = CapsuleNode("miner_v1", "Miner")
    refiner = CapsuleNode("refiner_v1", "Refiner")

    t1 = threading.Thread(target=miner.run)
    t2 = threading.Thread(target=refiner.run)
    
    t1.start()
    t2.start()

    time.sleep(1)
    
    print("\n--- Step 1: Miner Initiates Handshake ---")
    miner.send_material("refiner_v1")
    
    time.sleep(3)
    
    print("\n--- Step 2: Shutdown ---")
    miner.running = False
    refiner.running = False
    t1.join()
    t2.join()

    print("\n" + "="*60)
    print(" DEMO COMPLETE: P2P HANDSHAKE VERIFIED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
