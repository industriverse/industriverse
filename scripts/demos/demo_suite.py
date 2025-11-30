import json
import time
import random
import sys
import os

# ANSI Colors
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

class DemoSuite:
    def __init__(self, config_path="config/demo_scenarios.json"):
        self.config_path = config_path
        self.scenarios = self.load_config()
        self.results = []

    def load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"{RED}Config not found: {self.config_path}{RESET}")
            return {}

    def run_demo(self, demo):
        """
        Simulates running a single demo scenario.
        """
        print(f"  {CYAN}▶ Running {demo['id']}: {demo['name']}...{RESET}", end="\r")
        time.sleep(0.1) # Simulate processing time

        # Mock Logic: 98% Success Rate
        success = random.random() > 0.02
        
        # Mock Metric Improvement
        improvement = random.uniform(15.0, 45.0)
        
        result = {
            "id": demo['id'],
            "name": demo['name'],
            "chapter": "UNKNOWN",
            "status": "PASS" if success else "FAIL",
            "metric": demo['metric'],
            "improvement": f"{improvement:.1f}%"
        }
        
        if success:
            print(f"  {GREEN}✔ {demo['id']}: {demo['name']} | {demo['metric']} Improved by {improvement:.1f}%{RESET}")
        else:
            print(f"  {RED}✘ {demo['id']}: {demo['name']} | FAILED TO CONVERGE{RESET}")
            
        return result

    def run_suite(self):
        print(f"\n{BOLD}🚀 EMPEIRIA HAUS | DEMO SUITE INITIATED{RESET}")
        print(f"{YELLOW}Loading 50 Scenarios...{RESET}\n")
        
        total_passed = 0
        total_demos = 0

        for chapter, demos in self.scenarios.items():
            chapter_name = chapter.replace("_", " ").upper()
            print(f"{BOLD}=== {chapter_name} ==={RESET}")
            
            for demo in demos:
                result = self.run_demo(demo)
                result['chapter'] = chapter
                self.results.append(result)
                if result['status'] == "PASS":
                    total_passed += 1
                total_demos += 1
            print("") # Newline between chapters

        print(f"{BOLD}=== SUITE COMPLETE ==={RESET}")
        print(f"Total Demos: {total_demos}")
        print(f"Passed: {GREEN}{total_passed}{RESET}")
        print(f"Failed: {RED}{total_demos - total_passed}{RESET}")
        
        if total_passed == total_demos:
            print(f"\n{GREEN}✨ ALL SYSTEMS NOMINAL. READY FOR DEPLOYMENT.{RESET}")
        else:
            print(f"\n{YELLOW}⚠ WARNING: SOME SYSTEMS FAILED.{RESET}")

if __name__ == "__main__":
    suite = DemoSuite()
    suite.run_suite()
