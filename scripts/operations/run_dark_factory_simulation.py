import time
import logging
import random
from src.scf.autonomy.industrial_kernel import IndustrialKernel
from src.security.thermodynamic_safety import ThermodynamicSafetyLayer

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DarkFactorySim")

def main():
    """
    Runs a simulation of the Dark Factory.
    1. Initializes the Industrial Kernel (loads from drive if available).
    2. Initializes the Safety Layer.
    3. Runs a continuous loop of optimization and monitoring.
    """
    logger.info("🏭 Starting Dark Factory Simulation...")
    
    kernel = IndustrialKernel(factory_id="DARK_FACTORY_PRIME")
    safety = ThermodynamicSafetyLayer(energy_threshold_joules=8000.0)
    
    try:
        while True:
            # 1. Simulate Telemetry
            current_flux = random.uniform(2000.0, 9000.0) # Occasional spikes
            cpu_temp = random.uniform(40.0, 90.0)
            load = random.uniform(0.1, 1.0)
            
            # 2. Safety Check
            is_safe = safety.monitor_energy_flux(current_flux)
            if not is_safe:
                logger.warning("⚠️ Safety Violation Detected! Halting Optimization.")
            
            intrusion = safety.detect_intrusion({"cpu_temp": cpu_temp, "load": load})
            if intrusion:
                logger.critical("🚨 INTRUSION DETECTED! Initiating Lockdown.")
                break # Stop simulation on critical intrusion
            
            # 3. Optimization Cycle (if safe)
            if is_safe and not intrusion:
                active_lines = kernel.get_status()["active_lines"]
                for line in active_lines:
                    kernel.optimize_production_line(line)
                
                kernel.balance_entropy()
            
            time.sleep(2.0) # Simulate cycle time
            
    except KeyboardInterrupt:
        logger.info("🛑 Simulation Stopped by User.")

if __name__ == "__main__":
    main()
