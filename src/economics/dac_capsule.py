import time
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.economics.negentropy_ledger import NegentropyLedger

class DACCapsule:
    """
    The Revenue Engine.
    Wraps any service/object and meters its usage, charging the Ledger.
    Turns a static script into a rent-seeking Autonomous Agent.
    """
    def __init__(self, service_instance, name="Unknown_DAC", price_per_call=0.01):
        self.service = service_instance
        self.name = name
        self.price_per_call = price_per_call
        self.ledger = NegentropyLedger()
        self.total_revenue = 0.0
        print(f"💎 DAC Initialized: {self.name} (Price: ${self.price_per_call}/op)")

    def __getattr__(self, name):
        """
        Intercepts method calls to the wrapped service.
        """
        attr = getattr(self.service, name)
        
        if callable(attr):
            def wrapper(*args, **kwargs):
                print(f"\n🤖 [DAC: {self.name}] Intercepting call to '{name}'...")
                
                # 1. Calculate Cost
                cost = self.price_per_call
                # Dynamic pricing example: if downloading, charge more
                if "download" in name or "rehydrate" in name:
                    cost *= 5.0 # Data transfer premium
                
                # 2. Charge Ledger
                print(f"   💳 Charging Client: ${cost:.4f}...")
                # record_transaction(agent_id, task_id, entropy_reduction)
                # We treat the 'cost' (Price) as the 'Value Created' (Entropy Reduction) for this demo
                self.ledger.record_transaction(self.name, f"Call:{name}", cost)
                self.total_revenue += cost
                
                # 3. Execute Service
                start_time = time.time()
                result = attr(*args, **kwargs)
                duration = time.time() - start_time
                
                print(f"   ✅ Execution Complete ({duration:.2f}s). Revenue: ${self.total_revenue:.4f}")
                return result
            return wrapper
        return attr

if __name__ == "__main__":
    # Test with a Mock Service
    class MockService:
        def do_work(self):
            print("   (Service is doing work...)")
            time.sleep(0.2)
            
    service = MockService()
    dac = DACCapsule(service, name="Worker_Bot_01")
    
    dac.do_work()
    dac.do_work()
