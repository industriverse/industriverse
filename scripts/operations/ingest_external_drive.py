import os
import sys
import logging
from src.datahub.ingestion.primordial_soup import PrimordialSoupIngestor

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DriveIngestor")

def main():
    """
    Triggers the Primordial Soup Ingestor to scan the external drive.
    """
    drive_path = "/Volumes/Expansion"
    
    if not os.path.exists(drive_path):
        logger.error(f"❌ External Drive not found at: {drive_path}")
        logger.info("👉 Please ensure your drive is mounted and named 'Expansion'.")
        sys.exit(1)
        
    logger.info(f"🚀 Starting Ingestion from: {drive_path}")
    logger.info("   This may take a while depending on the dataset size...")
    
    ingestor = PrimordialSoupIngestor(source_drive=drive_path)
    ingestor.run_ingestion_cycle()
    
    logger.info("✅ Ingestion Complete. The Energy Atlas has been fed.")

if __name__ == "__main__":
    main()
