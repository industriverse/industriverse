import time
import random

class PocketScanner:
    """
    The Production Bridge: Allows users to 'Scan Reality' and send it to the Visual Twin.
    """
    def __init__(self, device_id: str):
        self.device_id = device_id
        
    def scan_object(self, object_name: str) -> dict:
        """
        Simulates a Lidar/Photogrammetry scan of a physical object.
        """
        print(f"📸 [Scanner] Scanning '{object_name}'...")
        time.sleep(1.0) # Simulate scanning time
        
        # Mock Point Cloud Data
        point_cloud_size = random.randint(10000, 50000)
        scan_id = f"SCAN_{random.randint(1000, 9999)}"
        
        print(f"   ☁️ Captured {point_cloud_size} points.")
        print(f"   ⬆️ Uploading to Visual Twin...")
        
        return {
            "scan_id": scan_id,
            "object_name": object_name,
            "points": point_cloud_size,
            "timestamp": time.time(),
            "status": "UPLOADED"
        }
        
    def request_fabrication(self, scan_id: str, wallet):
        """
        Orders the Dark Factory to manufacture the scanned object.
        """
        cost = 50.0
        print(f"🏭 [Scanner] Requesting Fabrication for {scan_id}...")
        
        if wallet.purchase_capsule(f"Fabrication: {scan_id}", cost):
            print("   ✅ Order Sent to Dark Factory. Drone Dispatch Pending.")
            return True
        return False
