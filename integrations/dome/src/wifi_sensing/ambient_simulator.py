import numpy as np
import time
from typing import List, Dict

class DomeAmbientSimulator:
    def __init__(self, num_subcarriers: int = 64, num_antennas: int = 2):
        self.num_subcarriers = num_subcarriers
        self.num_antennas = num_antennas
        self.sampling_rate = 1000.0

    def simulate_industrial_environment(self, duration: float = 10.0):
        print(f"🏭 Simulating {duration}s of industrial WiFi sensing...")
        
        num_samples = int(duration * self.sampling_rate)
        frames = []
        
        for i in range(num_samples):
            t = i / self.sampling_rate
            
            worker_motion = 0.3 * np.sin(2 * np.pi * 1.5 * t)
            machinery_vibration = 0.1 * np.sin(2 * np.pi * 50 * t)
            safety_event = 0.5 * np.exp(-((t - 5.0) ** 2) / 0.1) if 4.5 < t < 5.5 else 0
            
            amplitude = np.ones((self.num_subcarriers, self.num_antennas))
            amplitude += 0.1 * np.random.randn(self.num_subcarriers, self.num_antennas)
            amplitude += worker_motion + machinery_vibration + safety_event
            
            frames.append({
                "timestamp": int(t * 1e6),
                "amplitude": amplitude.flatten(),
                "motion_level": abs(worker_motion + machinery_vibration + safety_event)
            })
            
        print(f"✅ Generated {len(frames)} CSI frames")
        return frames

def test_dome_simulation():
    print("🧪 DOME AMBIENT INTELLIGENCE SIMULATION TEST")
    print("=" * 60)
    
    simulator = DomeAmbientSimulator()
    frames = simulator.simulate_industrial_environment(duration=5.0)
    
    events = []
    for i, frame in enumerate(frames):
        if frame["motion_level"] > 0.2:
            events.append({
                "timestamp": frame["timestamp"] / 1e6,
                "type": "motion_detected",
                "confidence": min(frame["motion_level"], 1.0)
            })
    
    print(f"📊 RESULTS:")
    print(f"   CSI frames: {len(frames)}")
    print(f"   Events detected: {len(events)}")
    print(f"   Processing rate: {len(frames)/5.0:.1f} frames/s")
    
    print(f"\n🎯 SAMPLE EVENTS:")
    for i, event in enumerate(events[:3]):
        print(f"   Event {i+1}: {event['type']} at t={event['timestamp']:.2f}s")
    
    return frames, events

if __name__ == "__main__":
    frames, events = test_dome_simulation()
    print("\n✅ Dome Ambient Intelligence Simulation Complete!")
