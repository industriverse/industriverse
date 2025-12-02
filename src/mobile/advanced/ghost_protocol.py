import random
import time

class GhostProtocol:
    """
    Active Defense: Generates 'Thermodynamic Chaff' (Fake Data) to poison surveillance.
    """
    def __init__(self):
        self.is_active = False
        
    def activate(self):
        self.is_active = True
        print("👻 [Ghost] PROTOCOL ACTIVE. Generating Chaff...")
        
    def generate_fake_gps(self) -> tuple:
        """
        Returns a plausible but fake GPS coordinate.
        """
        if not self.is_active:
            return None
            
        # Random walk logic
        lat = 37.7749 + random.uniform(-0.01, 0.01)
        lon = -122.4194 + random.uniform(-0.01, 0.01)
        print(f"   📍 [Ghost] Injecting Fake GPS: {lat}, {lon}")
        return (lat, lon)
        
    def generate_fake_contact(self) -> dict:
        """
        Returns a fake contact to pollute the address book.
        """
        if not self.is_active:
            return None
            
        fake_names = ["John Doe", "Jane Smith", "Agent Smith", "Neo"]
        name = random.choice(fake_names)
        phone = f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        print(f"   👤 [Ghost] Injecting Fake Contact: {name} ({phone})")
        return {"name": name, "phone": phone}
