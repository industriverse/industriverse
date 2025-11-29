import sys
import os
import asyncio
import json
import shutil

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rdr.ingestion import PhysicsDataPreparation
from src.core_ai_layer.monitoring_service.alerting_service import AlertingService
from src.core_ai_layer.monitoring_service.monitoring_schemas import AlertEvent, AlertSeverity, AlertChannel, AlertRecipientConfig
from datetime import datetime

async def test_ingestion_and_alerting():
    print("\n--- Testing Real Ingestion & Alerting ---")
    
    # 1. Test Local File Ingestion
    print("\n[1] Testing Local File Ingestion...")
    ingest_dir = os.path.join(os.getcwd(), "data", "ingest")
    os.makedirs(ingest_dir, exist_ok=True)
    
    # Create dummy file
    test_file = os.path.join(ingest_dir, "test_paper.txt")
    with open(test_file, "w") as f:
        f.write("Title: Test Physics Paper\nAbstract: This paper discusses quantum entropy and plasma dynamics.")
        
    ingester = PhysicsDataPreparation()
    papers = ingester.collect_papers()
    
    found = False
    for p in papers:
        if p['title'] == "Test Physics Paper":
            found = True
            print(f"  Found Paper: {p['title']}")
            break
            
    if found:
        print("✅ Local Ingestion Verified.")
    else:
        print("❌ Local Ingestion Failed.")
        
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)

    # 2. Test Persistent Alerting
    print("\n[2] Testing Persistent Alerting...")
    log_dir = os.path.join(os.getcwd(), "logs")
    alert_file = os.path.join(log_dir, "alerts.json")
    
    # Clear previous logs
    if os.path.exists(alert_file):
        os.remove(alert_file)
        
    service = AlertingService()
    import uuid
    alert_id = str(uuid.uuid4())
    event = AlertEvent(
        alert_id=alert_id,
        timestamp=datetime.utcnow(),
        severity=AlertSeverity.CRITICAL,
        title="Test Critical Alert",
        description="This is a test alert for hardening verification."
    )
    recipient = AlertRecipientConfig(
        target="admin@industriverse.com",
        channel=AlertChannel.EMAIL,
        min_severity=AlertSeverity.INFO
    )
    
    await service.dispatch_alert(event, [recipient])
    
    # Check file
    print(f"Checking alert file: {alert_file}")
    if os.path.exists(alert_file):
        print(f"File size: {os.path.getsize(alert_file)} bytes")
        with open(alert_file, "r") as f:
            lines = f.readlines()
            print(f"Lines in file: {len(lines)}")
            if not lines:
                print("❌ File exists but is empty.")
                return
            last_line = lines[-1]
            data = json.loads(last_line)
            
            if data['id'] == alert_id and data['title'] == "Test Critical Alert":
                print("✅ Alert Persistence Verified.")
            else:
                print(f"❌ Alert Content Mismatch: {data}")
    else:
        print("❌ Alert File Not Created.")

if __name__ == "__main__":
    asyncio.run(test_ingestion_and_alerting())
