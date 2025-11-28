import asyncio
import logging
from src.demo_framework.runner import DemoRunner
from src.demo_framework.scenarios.physics import PHYSICS_SCENARIOS
from src.demo_framework.scenarios.bio import BIO_SCENARIOS
from src.demo_framework.scenarios.space import SPACE_SCENARIOS
from src.demo_framework.scenarios.hardware import HARDWARE_SCENARIOS
from src.demo_framework.scenarios.econ_life import ECON_LIFE_SCENARIOS

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MegaSuite")

async def run_mega_suite():
    logger.info("Starting Phase 38: The 50-Demo Mega-Suite...")
    
    runner = DemoRunner()
    all_scenarios = (
        PHYSICS_SCENARIOS + 
        BIO_SCENARIOS + 
        SPACE_SCENARIOS + 
        HARDWARE_SCENARIOS + 
        ECON_LIFE_SCENARIOS
    )
    
    logger.info(f"Loaded {len(all_scenarios)} scenarios.")
    
    results = await runner.run_suite(all_scenarios)
    
    # Generate Report
    success_count = sum(1 for r in results if r['success'])
    logger.info("--- Mega-Suite Execution Complete ---")
    logger.info(f"Total Scenarios: {len(all_scenarios)}")
    logger.info(f"Successful: {success_count}")
    logger.info(f"Failed: {len(all_scenarios) - success_count}")
    
    if success_count == len(all_scenarios):
        logger.info("RESULT: ALL SYSTEMS NOMINAL. READY FOR INVESTOR SHOWCASE.")
    else:
        logger.warning("RESULT: SOME SCENARIOS FAILED. CHECK LOGS.")

if __name__ == "__main__":
    asyncio.run(run_mega_suite())
