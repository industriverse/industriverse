import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.orchestration.daemon_gears import OrchestrationLevelManager, DaemonLevel
from src.orchestration.discovery_accelerator import DiscoveryAccelerator
from src.orchestration.singularity_features import SingularityFeatures

class DiscoveryScenarioTester:
    """
    Verifies 10 Scenarios for the Discovery Acceleration Pipeline.
    """
    
    def __init__(self):
        self.manager = OrchestrationLevelManager()
        self.accelerator = DiscoveryAccelerator(self.manager)
        self.passed = 0
        self.failed = 0

    def run_scenario(self, name, level, expected_features=None, custom_action=None):
        print(f"\n🧪 SCENARIO: {name}")
        print(f"   Target Level: {level.name}")
        
        try:
            # 1. Set Level
            state = self.manager.set_level(level)
            
            # 2. Verify State
            if state.level != level:
                raise Exception(f"Level Mismatch: Expected {level}, got {state.level}")
            
            # 3. Verify Features
            if expected_features:
                for feature in expected_features:
                    if feature not in state.active_features:
                        raise Exception(f"Missing Feature: {feature}")
            
            # 4. Run Cycle / Custom Action
            if custom_action:
                custom_action()
            else:
                self.accelerator.run_discovery_cycle()
                
            print("   ✅ PASSED")
            self.passed += 1
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            self.failed += 1

    def test_all(self):
        print("🚀 STARTING 10-SCENARIO DISCOVERY TEST SUITE 🚀")
        
        # Scenario 1: Standard Mode (Safe)
        self.run_scenario("Standard Discovery", DaemonLevel.STANDARD, 
                          expected_features=["UserLM_Basic", "RND1_Safe"])
        
        # Scenario 2: Accelerated Mode (Parallel)
        self.run_scenario("Accelerated Discovery", DaemonLevel.ACCELERATED, 
                          expected_features=["Parallel_Hypothesis", "ASAL_Active"])
        
        # Scenario 3: Hyper Mode (Automated)
        self.run_scenario("Hyper Discovery", DaemonLevel.HYPER, 
                          expected_features=["T2L_Auto", "DGM_HighMutation"])
        
        # Scenario 4: Singularity Mode (Unsafe)
        self.run_scenario("Singularity Activation", DaemonLevel.SINGULARITY, 
                          expected_features=["TrifectaOverclock", "SingularityFeed"])
        
        # Scenario 5: Trifecta Overclock
        self.run_scenario("Trifecta Overclock", DaemonLevel.SINGULARITY, 
                          custom_action=SingularityFeatures.trifecta_overclock)
        
        # Scenario 6: DGM Recursive Mutation
        self.run_scenario("DGM Recursive Mutation", DaemonLevel.SINGULARITY, 
                          custom_action=SingularityFeatures.dgm_recursive_mutation)
        
        # Scenario 7: T2L Flash Forge
        self.run_scenario("T2L Flash Forge", DaemonLevel.SINGULARITY, 
                          custom_action=SingularityFeatures.t2l_flash_forge)
        
        # Scenario 8: ASAL Swarm
        self.run_scenario("ASAL Swarm", DaemonLevel.SINGULARITY, 
                          custom_action=SingularityFeatures.asal_swarm)
        
        # Scenario 9: Resource Cannibalism
        self.run_scenario("Resource Cannibalism", DaemonLevel.SINGULARITY, 
                          custom_action=SingularityFeatures.resource_cannibalism)
        
        # Scenario 10: Full Singularity Loop
        self.run_scenario("Full Singularity Loop", DaemonLevel.SINGULARITY)
        
        print(f"\n📊 RESULTS: {self.passed}/10 Passed")
        if self.failed > 0:
            sys.exit(1)

if __name__ == "__main__":
    tester = DiscoveryScenarioTester()
    tester.test_all()
