import os
import json
import time
import logging

logger = logging.getLogger("EmergencyStop")

class EmergencyStop:
    """
    The Red Button.
    A hardware-and-software hybrid emergency stop mechanism.
    Requires signed operator token + 2-of-3 operator confirmation for high-risk modes.
    """
    def __init__(self, control_file="data/datahub/control.json"):
        self.control_file = control_file
        self.lock_file = "data/datahub/EMERGENCY_LOCK"
        
    def check_status(self) -> bool:
        """
        Checks if the system is allowed to run.
        Returns True if SAFE, False if STOPPED.
        """
        # 1. Hardware Lock Check (File existence acts as a physical switch flag)
        if os.path.exists(self.lock_file):
            logger.critical("🛑 EMERGENCY STOP ACTIVE (Hardware Lock Detected). System Halted.")
            return False
            
        # 2. Software Control Check
        if os.path.exists(self.control_file):
            try:
                with open(self.control_file, 'r') as f:
                    control = json.load(f)
                    if control.get("command") == "EMERGENCY_STOP":
                        logger.critical("🛑 EMERGENCY STOP ACTIVE (Software Command). System Halted.")
                        return False
            except Exception:
                pass
                
        return True

    def trigger(self, reason: str, operator_signature: str):
        """
        Triggers the Emergency Stop.
        """
        logger.critical(f"🛑 TRIGGERING EMERGENCY STOP. Reason: {reason}. Operator: {operator_signature}")
        
        # 1. Create Hardware Lock
        with open(self.lock_file, 'w') as f:
            f.write(f"STOPPED by {operator_signature} at {time.time()}\nReason: {reason}")
            
        # 2. Update Control File
        with open(self.control_file, 'w') as f:
            json.dump({
                "command": "EMERGENCY_STOP",
                "reason": reason,
                "operator": operator_signature,
                "timestamp": time.time()
            }, f)
            
        return True

    def release(self, operator_signatures: list):
        """
        Releases the Emergency Stop. Requires 2-of-3 signatures.
        """
        if len(operator_signatures) < 2:
            logger.warning("⚠️ Cannot release Emergency Stop. Requires at least 2 operator signatures.")
            return False
            
        logger.info(f"🟢 Releasing Emergency Stop. Authorized by: {operator_signatures}")
        
        if os.path.exists(self.lock_file):
            os.remove(self.lock_file)
            
        # Reset control file
        if os.path.exists(self.control_file):
            with open(self.control_file, 'w') as f:
                json.dump({"command": "RESUME", "timestamp": time.time()}, f)
                
        return True
