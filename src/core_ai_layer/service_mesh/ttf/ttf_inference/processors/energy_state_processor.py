"""Energy State Processor for TTF Agent"""
import numpy as np

class EnergyStateProcessor:
    """Processes raw metrics into a scalar energy state value"""
    
    def __init__(self, weights: dict = None):
        """
        Initialize the processor with metric weights
        
        Args:
            weights: Dictionary of weights for each metric
        """
        self.weights = weights or {
            'cpu_percent': 0.4,
            'memory_percent': 0.3,
            'disk_percent': 0.1,
            'net_io_rate': 0.2
        }
        self.last_net_io = None

    def process(self, metrics: dict) -> float:
        """Process metrics into a single energy state value"""
        if self.last_net_io is None:
            self.last_net_io = metrics.get('net_io_counters', {})
            return 0.5 # Default initial state
        
        # Calculate net I/O rate
        current_net_io = metrics.get('net_io_counters', {})
        bytes_sent_rate = current_net_io.get('bytes_sent', 0) - self.last_net_io.get('bytes_sent', 0)
        bytes_recv_rate = current_net_io.get('bytes_recv', 0) - self.last_net_io.get('bytes_recv', 0)
        net_io_rate = (bytes_sent_rate + bytes_recv_rate) / 1e6 # Normalize to MB
        
        self.last_net_io = current_net_io
        
        # Normalize and weight metrics
        cpu_norm = metrics.get('cpu_percent', 50) / 100.0
        mem_norm = metrics.get('memory_percent', 50) / 100.0
        disk_norm = metrics.get('disk_percent', 50) / 100.0
        net_norm = min(net_io_rate / 10.0, 1.0) # Cap at 10 MB/s
        
        # Calculate weighted energy state
        energy_state = (
            cpu_norm * self.weights['cpu_percent'] +
            mem_norm * self.weights['memory_percent'] +
            disk_norm * self.weights['disk_percent'] +
            net_norm * self.weights['net_io_rate']
        )
        
        return np.clip(energy_state, 0.0, 1.0)
