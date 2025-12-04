import sys
import random
import time
from dataclasses import dataclass
from typing import List, Dict

# Mock Ledger for Simulation Speed
class SimLedger:
    def __init__(self):
        self.total_revenue = 0.0
        self.transaction_count = 0
        self.hourly_revenue = [0.0] * 24

    def record(self, amount: float, hour: int):
        self.total_revenue += amount
        self.transaction_count += 1
        self.hourly_revenue[hour] += amount

@dataclass
class DACProfile:
    type: str
    count: int
    price: float
    ops_per_hour_mean: float

PROFILES = [
    DACProfile("Archive", 400, 0.10, 100),      # High volume, low cost
    DACProfile("Compute", 300, 0.50, 20),       # Medium volume
    DACProfile("Optimization", 200, 5.00, 5),   # Low volume, high value
    DACProfile("Sovereign", 100, 100.00, 0.5)   # Rare, massive value
]

def run_simulation():
    print("🚀 Starting 1000-DAC Economic Simulation (Phase 14)...")
    print("=======================================================")
    
    ledger = SimLedger()
    
    # Simulation Loop: 24 Hours
    for hour in range(24):
        print(f"🕒 Hour {hour:02d}:00...", end="\r")
        
        # Simulate "Burst" events (e.g., Energy Spike at 14:00)
        burst_multiplier = 1.0
        if 13 <= hour <= 15:
            burst_multiplier = 3.0 # High demand afternoon
        
        for profile in PROFILES:
            # Calculate total ops for this profile type in this hour
            # Poisson-ish distribution
            base_ops = profile.count * profile.ops_per_hour_mean
            actual_ops = int(random.gauss(base_ops, base_ops * 0.1) * burst_multiplier)
            
            revenue = actual_ops * profile.price
            ledger.record(revenue, hour)
            
        time.sleep(0.05) # Fast forward

    print("\n\n📊 Simulation Complete. Generating Financial Report...")
    print("=======================================================")
    
    total_rev = ledger.total_revenue
    total_tx = ledger.transaction_count
    avg_tps = total_tx / (24 * 3600)
    
    print(f"💰 Total Daily Revenue (Negentropy): ${total_rev:,.2f}")
    print(f"📈 Total Transactions: {total_tx:,}")
    print(f"⚡ Average Throughput: {avg_tps:.2f} TPS")
    print("\n--- Hourly Breakdown ---")
    print(f"Peak Hour Revenue: ${max(ledger.hourly_revenue):,.2f}")
    print(f"Low Hour Revenue:  ${min(ledger.hourly_revenue):,.2f}")
    
    # Projection
    annual_rev = total_rev * 365
    print("\n🔮 Annual Projection (1000 DACs):")
    print(f"   ${annual_rev:,.2f}")
    
    # Write Report to File
    report_path = "docs/reports/PHASE_14_FINANCIAL_REPORT.md"
    with open(report_path, "w") as f:
        f.write(f"# Phase 14 Financial Report: The 1000-DAC Economy\n\n")
        f.write(f"**Date:** 2025-12-04\n")
        f.write(f"**Simulation:** 24-Hour Market Day\n\n")
        f.write(f"## Executive Summary\n")
        f.write(f"Scaling the Infinite Service Mesh to 1,000 active DACs generates a projected annual revenue of **${annual_rev:,.2f}**.\n\n")
        f.write(f"## Key Metrics\n")
        f.write(f"*   **Daily Revenue:** ${total_rev:,.2f}\n")
        f.write(f"*   **Daily Transactions:** {total_tx:,}\n")
        f.write(f"*   **System Throughput:** {avg_tps:.2f} TPS\n\n")
        f.write(f"## Agent Composition\n")
        for p in PROFILES:
            f.write(f"*   **{p.type}**: {p.count} agents @ ${p.price:.2f}/op\n")
            
    print(f"\n✅ Report saved to {report_path}")

if __name__ == "__main__":
    run_simulation()
