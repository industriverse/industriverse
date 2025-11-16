"""System Metrics Collector for TTF Agent"""
import psutil

class SystemMetricsCollector:
    """Collects system-level metrics like CPU, memory, and network"""
    
    def collect(self) -> dict:
        """Collect all system metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'net_io_counters': psutil.net_io_counters()._asdict()
        }
