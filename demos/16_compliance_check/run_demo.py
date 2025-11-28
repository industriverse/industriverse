import json
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class ComplianceEngine:
    def __init__(self):
        self.rules = [
            {
                "id": "REG-EU-2025-001",
                "name": "EU Battery Passport",
                "condition": lambda op: op["destination"] == "EU" and op.get("recycled_content", 0) < 0.15,
                "message": "Export to EU requires minimum 15% recycled content."
            },
            {
                "id": "REG-US-ITAR-99",
                "name": "ITAR Restricted Destination",
                "condition": lambda op: op["destination"] in ["CN", "RU", "KP"] and op["product_category"] == "defense_critical",
                "message": "Export to restricted destination prohibited by ITAR."
            }
        ]

    def check_operation(self, operation):
        logger.info(f"Checking operation: {operation['id']} -> {operation['destination']}")
        
        violations = []
        for rule in self.rules:
            if rule["condition"](operation):
                violations.append({
                    "rule_id": rule["id"],
                    "violation": rule["message"]
                })
        
        if violations:
            return {"status": "BLOCKED", "violations": violations}
        return {"status": "APPROVED"}

def run():
    print("\n" + "="*60)
    print(" DEMO 16: EXECUTABLE COMPLIANCE CHECK")
    print("="*60 + "\n")

    engine = ComplianceEngine()

    operations = [
        {
            "id": "OP-101",
            "destination": "US",
            "product_category": "consumer_electronics",
            "recycled_content": 0.05
        },
        {
            "id": "OP-102",
            "destination": "EU",
            "product_category": "ev_battery",
            "recycled_content": 0.10 # Violation: < 15%
        },
        {
            "id": "OP-103",
            "destination": "CN",
            "product_category": "defense_critical", # Violation: ITAR
            "recycled_content": 0.50
        },
        {
            "id": "OP-104",
            "destination": "EU",
            "product_category": "ev_battery",
            "recycled_content": 0.20 # Compliant
        }
    ]

    for op in operations:
        print(f"--- Processing Operation {op['id']} ---")
        print(json.dumps(op, indent=2))
        
        result = engine.check_operation(op)
        
        if result["status"] == "APPROVED":
            print(f"\n✅ STATUS: {result['status']}")
        else:
            print(f"\n❌ STATUS: {result['status']}")
            for v in result["violations"]:
                print(f"   [!] {v['rule_id']}: {v['violation']}")
        
        print("\n")
        time.sleep(1)

    print("\n" + "="*60)
    print(" DEMO COMPLETE: COMPLIANCE ENFORCED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
