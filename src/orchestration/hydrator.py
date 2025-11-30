import time
import os

class ServiceHydrator:
    """
    Manages B2 downloads and local caching (The "Sleeping Army" Manager).
    """
    def __init__(self, cache_dir="runtime/services"):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def hydrate(self, b2_path):
        """
        Downloads service from B2 if not already cached.
        """
        filename = b2_path.split("/")[-1]
        local_path = os.path.join(self.cache_dir, filename)

        if os.path.exists(local_path):
            print(f"[Hydrator] ⚡ Cache Hit: {filename}")
            return local_path

        print(f"[Hydrator] 🌧️ Hydrating from B2: {b2_path}...")
        # Simulate Download Latency
        time.sleep(1.0) 
        
        # Create dummy file
        with open(local_path, 'w') as f:
            f.write("MOCK BINARY CONTENT")
            
        print(f"[Hydrator] ✅ Hydration Complete: {local_path}")
        return local_path

    def estimate_cost(self, b2_path):
        """
        Returns estimated hydration cost (Bandwidth + Time).
        """
        # Mock logic: longer names = bigger files = more cost
        size_mb = len(b2_path) * 10 
        cost_usd = size_mb * 0.00001 # Cheap bandwidth
        return cost_usd
