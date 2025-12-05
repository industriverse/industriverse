import time
import csv
import random
import numpy as np
from pathlib import Path
from src.scf.ingestion.energy_signature import EnergySignature
from src.scf.evaluation.roi_calculator import ROICalculator

def run_pilot():
    print("🚀 Starting Baseline Energy Accounting Pilot...")
    
    # Setup
    sig_extractor = EnergySignature()
    roi_calc = ROICalculator(kwh_price=0.15) # Industrial rate
    
    output_file = Path("baseline_energy_report.csv")
    
    # Simulation Parameters
    duration_seconds = 60
    sample_rate = 10 # Hz
    
    print(f"   Simulating {duration_seconds} seconds of industrial load...")
    
    results = []
    
    # Simulate a "Baseline" vs "Optimized" scenario
    # Baseline: High variance, higher power draw
    # Optimized: Lower variance (entropy), lower power draw
    
    total_baseline_kwh = 0.0
    total_optimized_kwh = 0.0
    
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['timestamp', 'baseline_power_w', 'optimized_power_w', 'entropy_rate', 'kwh_saved', 'cost_saved_usd']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for t in range(duration_seconds):
            # Generate synthetic data
            # Baseline: Noisy sine wave + random spikes
            baseline_signal = np.sin(np.linspace(0, 10, 100)) + np.random.normal(0, 0.5, 100)
            baseline_power = 500.0 + np.random.normal(0, 50) # Watts
            
            # Optimized: Smoother signal
            optimized_signal = np.sin(np.linspace(0, 10, 100)) + np.random.normal(0, 0.1, 100)
            optimized_power = 450.0 + np.random.normal(0, 10) # Watts
            
            # Extract Signatures
            base_sig = sig_extractor.extract(baseline_signal)
            opt_sig = sig_extractor.extract(optimized_signal)
            
            # Calculate ROI for this second (Power * Time / 1000 / 3600)
            # 1 second = 1/3600 hours
            base_kwh_step = baseline_power / 1000.0 / 3600.0
            opt_kwh_step = optimized_power / 1000.0 / 3600.0
            
            savings = roi_calc.calculate_savings(base_kwh_step, opt_kwh_step)
            
            total_baseline_kwh += base_kwh_step
            total_optimized_kwh += opt_kwh_step
            
            row = {
                'timestamp': time.time(),
                'baseline_power_w': round(baseline_power, 2),
                'optimized_power_w': round(optimized_power, 2),
                'entropy_rate': round(base_sig.get('entropy_rate', 0), 4),
                'kwh_saved': round(savings['kwh_saved'], 8),
                'cost_saved_usd': round(savings['cost_saved_usd'], 8)
            }
            writer.writerow(row)
            results.append(row)
            
            if t % 10 == 0:
                print(f"   T+{t}s | Baseline: {row['baseline_power_w']}W | Saved: ${row['cost_saved_usd']}")
                
    # Summary
    total_savings = roi_calc.calculate_savings(total_baseline_kwh, total_optimized_kwh)
    
    print("\n📊 Pilot Complete. Summary:")
    print(f"   Total Duration: {duration_seconds}s")
    print(f"   Baseline Energy: {total_baseline_kwh:.6f} kWh")
    print(f"   Optimized Energy: {total_optimized_kwh:.6f} kWh")
    print(f"   Total Saved: {total_savings['kwh_saved']:.6f} kWh")
    print(f"   Value Created: ${total_savings['cost_saved_usd']:.6f}")
    print(f"   Report generated: {output_file.absolute()}")

if __name__ == "__main__":
    run_pilot()
