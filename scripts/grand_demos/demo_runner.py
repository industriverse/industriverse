import asyncio
import json
import os
import sys
import logging
import time
from datetime import datetime
from typing import Dict, Any, List

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.unified_loop.grand_orchestrator import get_grand_orchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("grand_demo_suite.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GrandDemoRunner")

class GrandDemoRunner:
    def __init__(self, scenarios_dir: str):
        self.scenarios_dir = scenarios_dir
        self.orchestrator = get_grand_orchestrator()
        self.results = []

    async def run_scenario(self, scenario_file: str):
        filepath = os.path.join(self.scenarios_dir, scenario_file)
        with open(filepath, 'r') as f:
            config = json.load(f)
            
        logger.info(f"--- Running Scenario: {config['name']} ---")
        start_time = time.time()
        
        try:
            result = await self.orchestrator.run_grand_loop(
                client_id=f"demo_client_{config['id']}",
                task_description=config['task'],
                domain=config['domain']
            )
            
            duration = time.time() - start_time
            
            summary = {
                "id": config['id'],
                "name": config['name'],
                "domain": config['domain'],
                "status": result['status'],
                "duration": f"{duration:.2f}s",
                "capsule_id": result.get('capsule_id', 'N/A'),
                "reward": result.get('reward', 0),
                "lora": result.get('lora_used', {}).get('domain', 'N/A')
            }
            
            if result['status'] == 'success':
                logger.info(f"✅ Scenario {config['id']} PASSED in {duration:.2f}s")
            else:
                logger.error(f"❌ Scenario {config['id']} FAILED: {result.get('reason')}")
                
            self.results.append(summary)
            
        except Exception as e:
            logger.error(f"❌ Scenario {config['id']} CRASHED: {e}")
            self.results.append({
                "id": config['id'],
                "name": config['name'],
                "status": "crashed",
                "error": str(e)
            })

    async def run_all(self):
        files = sorted([f for f in os.listdir(self.scenarios_dir) if f.endswith('.json')])
        logger.info(f"Found {len(files)} scenarios.")
        
        for f in files:
            await self.run_scenario(f)
            
        self.generate_report()

    def generate_report(self):
        report_path = "docs/reports/grand_demo_report.md"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        passed = sum(1 for r in self.results if r['status'] == 'success')
        total = len(self.results)
        
        with open(report_path, 'w') as f:
            f.write(f"# Grand Demo Suite Report\n")
            f.write(f"**Date:** {datetime.now().isoformat()}\n")
            f.write(f"**Success Rate:** {passed}/{total} ({passed/total*100:.1f}%)\n\n")
            
            f.write("| ID | Scenario | Domain | Status | Duration | Reward | LoRA |\n")
            f.write("|---|---|---|---|---|---|---|\n")
            
            for r in self.results:
                status_icon = "✅" if r['status'] == 'success' else "❌"
                f.write(f"| {r['id']} | {r['name']} | {r['domain']} | {status_icon} {r['status']} | {r.get('duration', '-')} | {r.get('reward', '-')} | {r.get('lora', '-')} |\n")
                
        logger.info(f"Report generated at {report_path}")

if __name__ == "__main__":
    runner = GrandDemoRunner("scripts/grand_demos/scenarios")
    asyncio.run(runner.run_all())
