import asyncio
import sys
import os
import json
from decimal import Decimal
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.white_label.credit_protocol.utid_marketplace import (
    get_utid_marketplace,
    UTIDMarketplace,
    ListingType
)
from src.bridge_api.event_bus import GlobalEventBus

async def verify_marketplace():
    print("🏪 Starting Marketplace Verification...")
    
    # Clean up previous test data
    if os.path.exists("data/marketplace_storage.json"):
        os.remove("data/marketplace_storage.json")
    
    # 1. Initialize Marketplace
    print("\n1. Initializing Marketplace...")
    marketplace = UTIDMarketplace() # Create fresh instance
    
    # 2. Create Listing
    print("\n2. Creating Listing...")
    listing = marketplace.create_sale_listing(
        utid="UTID-TEST-123",
        insight_id="INSIGHT-123",
        seller_id="user_test_001",
        seller_name="Test Seller",
        price=Decimal("50.0"),
        title="Test Insight",
        description="A test insight for verification"
    )
    print(f"✅ Listing Created: {listing.listing_id}")
    
    # 3. Verify Persistence (File check)
    print("\n3. Verifying Persistence (File Check)...")
    if os.path.exists(marketplace.persistence_path):
        print(f"✅ Storage file exists: {marketplace.persistence_path}")
        with open(marketplace.persistence_path, 'r') as f:
            data = json.load(f)
            if len(data["listings"]) == 1:
                print("✅ Data persisted correctly")
            else:
                print("❌ Data mismatch in file")
    else:
        print("❌ Storage file NOT found")
        
    # 4. Verify Reload
    print("\n4. Verifying Reload...")
    marketplace2 = UTIDMarketplace() # Should load from disk
    if len(marketplace2.listings) == 1:
        print("✅ Listings reloaded successfully")
        loaded_listing = list(marketplace2.listings.values())[0]
        print(f"   Loaded: {loaded_listing.title}")
    else:
        print(f"❌ Reload failed. Listings: {len(marketplace2.listings)}")
        
    # 5. Verify Event Auto-Listing
    print("\n5. Verifying Event Auto-Listing...")
    
    # Simulate high quality proof event
    event = {
        "type": "proof_generated",
        "proof": {
            "proof_id": "PROOF-AUTO-999",
            "utid": "UTID-AUTO-999",
            "domain": "thermodynamics",
            "metadata": {
                "proof_score": 0.98,
                "energy_joules": 500
            }
        }
    }
    
    print("   Publishing event...")
    await GlobalEventBus.publish(event)
    
    # Allow some time for async processing if needed (though our handler is async called by publish)
    # But GlobalEventBus.publish awaits subscribers, so it should be done.
    
    # Check if listed
    listings = marketplace.search_listings(tags=["auto-listed"])
    if len(listings) > 0:
        print(f"✅ Auto-listing successful: {listings[0].listing_id}")
        print(f"   Price: {listings[0].price} (Score: {listings[0].proof_score})")
    else:
        print("❌ Auto-listing FAILED")

    print("\n🎉 Marketplace Verification Complete!")

if __name__ == "__main__":
    asyncio.run(verify_marketplace())
