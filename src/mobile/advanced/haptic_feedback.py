import time

class HapticImmuneResponse:
    """
    Tactile Warnings: The phone 'shivers' when it detects a threat.
    """
    def __init__(self):
        pass
        
    def trigger_heartbeat_warning(self):
        """
        Simulates a 'Thump-Thump' vibration pattern.
        """
        print("💓 [Haptic] TRIGGERING HEARTBEAT WARNING")
        print("   📳 *Thump* (100ms)")
        time.sleep(0.1)
        print("   📳 *Thump* (100ms)")
        time.sleep(0.1)
        print("   ... (Pause)")
        time.sleep(0.5)
        print("   📳 *Thump* (100ms)")
        print("   📳 *Thump* (100ms)")
        
    def trigger_stingray_alert(self):
        """
        Sharp, high-frequency buzz for critical network threats.
        """
        print("⚡ [Haptic] TRIGGERING STINGRAY ALERT")
        print("   📳 *BZZZZZZT* (500ms High Intensity)")
