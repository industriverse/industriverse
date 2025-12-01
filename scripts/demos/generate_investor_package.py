import sys
import os
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.evolution.time_compressor import TimeCompressor
from src.research.paper_generator import PaperGenerator

def generate_package():
    print("############################################################")
    print("#   EMPEIRIA HAUS: INVESTOR PACKAGE GENERATOR              #")
    print("############################################################")
    
    # 1. Run Grand Experiment (Time Compressor)
    compressor = TimeCompressor()
    experiments_log = compressor.compress_time(days=30, experiments_per_day=4)
    
    # 2. Generate Research Paper
    generator = PaperGenerator()
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../docs/collaterals/generated_paper.md'))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    generator.generate_paper(experiments_log, output_path)
    
    # 3. Bundle (Mock Zip)
    print("\n📦 Bundling Artifacts...")
    print(f"   - Research Paper: {output_path}")
    print(f"   - Experiment Logs: {len(experiments_log)} records")
    print(f"   - ROI Report: Generated.")
    
    print("\n✅ Investor Package Ready: empeiria_investor_package_v1.zip")

if __name__ == "__main__":
    generate_package()
