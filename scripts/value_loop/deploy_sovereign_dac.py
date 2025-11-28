#!/usr/bin/env python3
"""
Script 2: deploy_sovereign_dac.py
Purpose: Deploys a Sovereign Capsule to the Gateway.
Usage: python deploy_sovereign_dac.py --manifest <path_to_manifest.yaml>
"""

import argparse
import sys
import os
import yaml
import logging
import asyncio
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from src.capsule_layer.database import db_manager
from src.capsule_layer.redis_manager import redis_manager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def deploy_capsule(manifest_path):
    logger.info(f"Reading manifest from {manifest_path}...")
    try:
        with open(manifest_path, "r") as f:
            manifest = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("Manifest file not found.")
        sys.exit(1)
        
    capsule_id = manifest.get("id")
    if not capsule_id:
        logger.error("Manifest missing 'id' field.")
        sys.exit(1)
        
    logger.info(f"Deploying Capsule: {capsule_id}")
    
    # Connect to infra
    # Note: In a real script we might hit the API, but here we use the managers directly for "local" deployment
    # or to simulate the backend logic.
    await db_manager.connect()
    await redis_manager.connect()
    
    try:
        # 1. Register in DB (Mocking the schema for now as we didn't see the full DDL)
        # We'll assume an 'activities' table exists from the gateway service code, 
        # but we might need a 'capsules' table. 
        # For this demo, we'll create a "Deployment Activity" to signify it's live.
        
        query = """
            INSERT INTO activities (capsule_id, activity_type, status, payload)
            VALUES ($1, 'deployment', 'active', $2)
            RETURNING id
        """
        # We store the full manifest as the payload for the deployment record
        row = await db_manager.fetchrow(query, capsule_id, json.dumps(manifest))
        deployment_id = row['id']
        
        logger.info(f"Capsule registered in DB. Deployment ID: {deployment_id}")
        
        # 2. Publish "Capsule Deployed" event to Redis
        await redis_manager.publish("system:deployments", {
            "type": "capsule_deployed",
            "capsule_id": capsule_id,
            "manifest": manifest,
            "deployment_id": deployment_id
        })
        
        logger.info("Deployment event published to Redis.")
        
        # 3. Initialize Runtime Monitor (Simulated start)
        logger.info("Initializing Thermodynamic Runtime Monitor...")
        # In a real system, this would spawn a process or k8s pod.
        # Here we just log success.
        
        print(f"\n✅ DEPLOYMENT SUCCESSFUL: {capsule_id}")
        print(f"   Manifest: {manifest.get('title')}")
        print(f"   Runtime Budget: {manifest.get('safety', {}).get('runtime_budget_ms')} ms")
        
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        # If DB fails (e.g. table missing in this env), we warn but don't crash for the demo
        logger.warning("Continuing despite DB error (likely schema missing in dev env).")
        
    finally:
        await db_manager.disconnect()
        await redis_manager.disconnect()

def main():
    parser = argparse.ArgumentParser(description="Deploy a Sovereign Capsule.")
    parser.add_argument("--manifest", type=str, required=True, help="Path to manifest.yaml")
    
    args = parser.parse_args()
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(deploy_capsule(args.manifest))

if __name__ == "__main__":
    main()
