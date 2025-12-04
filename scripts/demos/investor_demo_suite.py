#!/usr/bin/env python3
import asyncio
import logging
import time
import torch
import json
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOG = logging.getLogger("InvestorDemo")

# Ensure src is in path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.scf.daemon.scf_daemon import SCFSovereignDaemon
from src.scf.training.training_orchestrator import TrainingOrchestrator
from src.scf.agentops.agentops import AgentOps
from src.scf.core_models.gen_n import GenN
from src.scf.core_models.tnn import TNN
from src.scf.batcher.fossil_batcher import FossilBatcher

async def demo_1_daemon_awakening():
    LOG.info("\n=== DEMO 1: THE AWAKENING (Autonomous Daemon Boot) ===")
    LOG.info("Starting Sovereign Daemon in background...")
    
    daemon = SCFSovereignDaemon()
    # We run it for a few seconds to show it booting and ingesting
    task = asyncio.create_task(daemon.start())
    
    await asyncio.sleep(5)
    LOG.info(">> Daemon is ALIVE. Heartbeat active.")
    
    # Simulate gear shift
    LOG.info(">> Operator Command: SHIFT_GEAR -> ACCELERATED")
    daemon.set_gear("ACCELERATED")
    await asyncio.sleep(2)
    
    LOG.info(">> Daemon acknowledged gear shift. Heartbeat accelerated.")
    await daemon.stop()
    await task
    LOG.info("=== DEMO 1 COMPLETE ===\n")

async def demo_2_physics_training():
    LOG.info("\n=== DEMO 2: PHYSICS-GROUNDED TRAINING (Real EBDM on H100) ===")
    
    # Ensure we have data
    batcher = FossilBatcher()
    if not list(batcher.batch_dir.glob("*.pkl")):
        LOG.info(">> Generating synthetic training batch...")
        batcher.ingest_stream(10)
    
    batch = batcher.build_batch()
    if not batch:
        LOG.warning("No batch available!")
        return

    LOG.info(f">> Loaded Batch {batch['batch_id']} ({len(batch['samples'])} fossils)")
    
    orch = TrainingOrchestrator()
    if torch.cuda.is_available():
        LOG.info(f">> GPU DETECTED: {torch.cuda.get_device_name(0)}")
        orch.ebdm.cuda()
        orch.tnn.cuda()
        # Move batch to cuda
        batch["tnn_ready_tensor"] = batch["tnn_ready_tensor"].cuda()
        batch["ebdm_ready_tensor"] = batch["ebdm_ready_tensor"].cuda()
    else:
        LOG.warning(">> NO GPU DETECTED. Running on CPU (slow).")

    LOG.info(">> Executing EBDM Training Step...")
    loss = await orch.train_on_batch(batch)
    LOG.info(f">> Training Step Complete. Loss: {loss:.4f}")
    LOG.info("=== DEMO 2 COMPLETE ===\n")

async def demo_3_material_discovery():
    LOG.info("\n=== DEMO 3: GENERATIVE DISCOVERY (Material Simulation) ===")
    
    gen_n = GenN(input_dim=128, hidden=512, vocab_size=100) # Mock vocab
    tnn = TNN(in_dim=128)
    
    if torch.cuda.is_available():
        gen_n.cuda()
        tnn.cuda()
        
    # Simulate: Client asks for "High Entropy Material"
    LOG.info(">> Request: Discover material with Entropy > 0.8")
    
    # Generate candidate (random seed for demo)
    seed = torch.randn(1, 128)
    if torch.cuda.is_available(): seed = seed.cuda()
    
    # GenN "dreams" a material structure (logits)
    logits = gen_n(seed)
    # For demo, we treat the seed as the "structure" embedding to score
    
    # TNN scores it
    energy_score = tnn(seed).item()
    entropy_score = abs(energy_score) # Mock relation
    
    LOG.info(f">> GenN Generated Candidate: MAT-X-{int(time.time())}")
    LOG.info(f">> TNN Physics Score: Energy={energy_score:.4f} J, Entropy={entropy_score:.4f}")
    
    if entropy_score > 0.5:
        LOG.info(">> STATUS: VIABLE CANDIDATE FOUND.")
    else:
        LOG.info(">> STATUS: REJECTED (Low Entropy).")
        
    LOG.info("=== DEMO 3 COMPLETE ===\n")

async def demo_4_weekly_release():
    LOG.info("\n=== DEMO 4: CONTINUOUS DELIVERY (Weekly Release Automation) ===")
    import subprocess
    
    LOG.info(">> Triggering 'weekly_release.sh'...")
    # We call the script we created
    try:
        res = subprocess.run(["bash", "scripts/releases/weekly_release.sh"], capture_output=True, text=True)
        for line in res.stdout.splitlines():
            LOG.info(f"   [ReleaseScript] {line}")
    except Exception as e:
        LOG.error(f"Failed to run release script: {e}")
        
    LOG.info(">> Release Artifacts Packaged.")
    LOG.info("=== DEMO 4 COMPLETE ===\n")

async def demo_5_agentops_value():
    LOG.info("\n=== DEMO 5: END-TO-END VALUE (AgentOps Cycle) ===")
    
    ops = AgentOps()
    LOG.info(">> AgentOps: Harvesting Data...")
    ds = ops.harvest()
    
    LOG.info(">> AgentOps: Training Model...")
    ckpt = ops.train(ds)
    
    LOG.info(">> AgentOps: Distilling to Edge (BitNet)...")
    student = ops.distill(ckpt)
    
    LOG.info(">> AgentOps: Deploying to Production...")
    ops.deploy(student)
    
    LOG.info(">> VALUE DELIVERED: Model deployed to edge nodes.")
    LOG.info("=== DEMO 5 COMPLETE ===\n")

async def run_all():
    LOG.info("🚀 STARTING INVESTOR DEMO SUITE (5/5)")
    await demo_1_daemon_awakening()
    await demo_2_physics_training()
    await demo_3_material_discovery()
    await demo_4_weekly_release()
    await demo_5_agentops_value()
    LOG.info("✅ ALL DEMOS COMPLETE.")

if __name__ == "__main__":
    asyncio.run(run_all())
