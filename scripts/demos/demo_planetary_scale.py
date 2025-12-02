import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.scale.planetary_resource_manager import PlanetaryResourceManager
from src.scale.global_load_balancer import GlobalLoadBalancer

def print_header(text):
    print(f"\n{'='*60}")
    print(f"   {text}")
    print(f"{'='*60}")

def demo_planetary_scale():
    print_header("DEMO: THE PLANETARY SCALE-OUT")
    print("Scenario: 'Follow the Sun' Workload Distribution")
    
    # 1. Initialize The Planet
    mgr = PlanetaryResourceManager()
    mgr.register_region("ASIA_PACIFIC", 5000.0, 20000.0) # Morning
    mgr.register_region("EU_CENTRAL", 5000.0, 20000.0)   # Mid-day
    mgr.register_region("US_EAST", 5000.0, 20000.0)      # Evening
    
    lb = GlobalLoadBalancer(mgr)
    
    # 2. Phase 1: Tokyo Morning Trading Spike
    print_header("PHASE 1: ASIA MARKET OPEN (09:00 JST)")
    tasks = ["HFT_Algo_1", "HFT_Algo_2", "Risk_Analysis_Asia"]
    for t in tasks:
        lb.route_task(t, 0.3) # Heavy tasks
        time.sleep(0.2)
    mgr.get_status()
    
    # 3. Phase 2: London Market Open (Spillover)
    print_header("PHASE 2: LONDON MARKET OPEN (08:00 GMT)")
    print(">> Asia is saturated. Routing overflow to EU...")
    tasks = ["Forex_Bridge", "Euro_Settlement"]
    for t in tasks:
        lb.route_task(t, 0.4)
        time.sleep(0.2)
    mgr.get_status()
    
    # 4. Phase 3: NY Market Open (Global Load)
    print_header("PHASE 3: NEW YORK MARKET OPEN (09:30 EST)")
    print(">> Global capacity testing...")
    tasks = ["NYSE_Data_Feed", "Fed_Compute_Job", "Global_Sync"]
    for t in tasks:
        lb.route_task(t, 0.3)
        time.sleep(0.2)
    mgr.get_status()
    
    print_header("DEMO COMPLETE: PLANETARY OPTIMIZATION ACHIEVED")

if __name__ == "__main__":
    demo_planetary_scale()
