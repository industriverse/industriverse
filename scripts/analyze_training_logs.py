import json
import matplotlib.pyplot as plt
import argparse
from pathlib import Path

def analyze_logs(log_path: str, output_image: str = "training_analysis.png"):
    print(f"📊 Analyzing logs from: {log_path}")
    
    epochs = []
    losses = []
    energies = []
    entropies = []
    
    try:
        with open(log_path, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    epochs.append(entry.get('epoch', 0))
                    losses.append(entry.get('loss', 0))
                    energies.append(entry.get('kwh_used', 0)) # Energy per epoch
                    entropies.append(entry.get('entropy_penalty', 0)) # Physics violation
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        print(f"❌ Log file not found: {log_path}")
        return

    if not epochs:
        print("⚠️ No valid log entries found.")
        return

    # Cumulative Energy
    cumulative_energy = [sum(energies[:i+1]) for i in range(len(energies))]

    # Plotting
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), sharex=True)
    
    # Plot 1: Loss & Entropy
    ax1.plot(epochs, losses, label='Total Loss', color='blue', marker='o')
    ax1.plot(epochs, entropies, label='Entropy Penalty', color='orange', linestyle='--')
    ax1.set_ylabel('Loss')
    ax1.set_title('Training Dynamics: Physics Compliance')
    ax1.legend()
    ax1.grid(True)
    
    # Plot 2: Energy Consumption
    ax2.plot(epochs, cumulative_energy, label='Cumulative Energy (kWh)', color='green', linewidth=2)
    ax2.set_ylabel('Energy (kWh)')
    ax2.set_xlabel('Epoch')
    ax2.set_title('Thermodynamic Cost of Intelligence')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(output_image)
    print(f"✅ Analysis complete. Chart saved to: {output_image}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("log_file", help="Path to training_log.jsonl")
    args = parser.parse_args()
    
    analyze_logs(args.log_file)
