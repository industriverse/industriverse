from pathlib import Path

class EmergencyStop:
    def __init__(self, lock_file="data/scf/EMERGENCY_LOCK"):
        self.lock_file = Path(lock_file)

    def is_active(self) -> bool:
        return self.lock_file.exists()

    def trigger(self):
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
        self.lock_file.touch()

    def release(self):
        if self.lock_file.exists():
            self.lock_file.unlink()
