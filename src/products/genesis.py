from src.meta.genesis import GenesisEngine

class GenesisArchitect:
    """
    Product 8: Genesis Architect
    Self-Coding Infrastructure.
    """
    def __init__(self):
        self.name = "Genesis Architect"
        self.engine = GenesisEngine()

    def get_status(self):
        return {
            "product": self.name,
            "status": "CREATING",
            "mode": "Self-Coding"
        }

    def generate_code(self, spec):
        print(f"[{self.name}] Generating Infrastructure from Spec...")
        return self.engine.generate_script(spec)
