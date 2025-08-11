#!/usr/bin/env python3
"""
BigSkyAg Simple Backup Upload Script
Simple, reliable upload with basic retry logic
"""

import sys
import logging
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from config import get_storage_provider_config
    from storage_providers import get_storage_provider
    CONFIG_AVAILABLE = True
except ImportError as e:
    CONFIG_AVAILABLE = False
    print(f"❌ Import error: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simple_upload.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def simple_upload():
    """Simple upload with basic retry logic"""
    logger.info("🚀 Starting simple backup upload...")
    
    if not CONFIG_AVAILABLE:
        logger.error("❌ Configuration not available")
        return False
        
    try:
        # Initialize storage
        config = get_storage_provider_config()
        provider = get_storage_provider(config['provider'], config)
        
        if not provider:
            logger.error("❌ Failed to initialize storage provider")
            return False
            
        # Find latest backup
        backup_dir = Path("/Volumes/BigSkyAgSSD/BigSkyAg/00_Admin/Backups")
        if not backup_dir.exists():
            logger.error(f"❌ Backup directory not found: {backup_dir}")
            return False
        
        backup_files = list(backup_dir.glob("*.zip"))
        if not backup_files:
            logger.error("❌ No backup files found")
            return False
        
        latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
        file_size = latest_backup.stat().st_size
        
        logger.info(f"✅ Found backup: {latest_backup.name} ({file_size / (1024**2):.1f} MB)")
        
        # Simple upload with retry
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                logger.info(f"📤 Upload attempt {attempt + 1}/{max_attempts}")
                
                # Authenticate
                if not provider.authenticate():
                    logger.error("❌ Authentication failed")
                    continue
                
                # Upload file
                start_time = time.time()
                file_id = provider.upload_file(latest_backup, "daily")
                upload_time = time.time() - start_time
                
                if file_id:
                    logger.info(f"🎉 Upload successful in {upload_time:.1f} seconds!")
                    logger.info(f"📁 File ID: {file_id}")
                    return True
                else:
                    logger.error("❌ Upload failed - no file ID returned")
                    
            except Exception as e:
                logger.error(f"💥 Upload attempt {attempt + 1} failed: {e}")
                if attempt < max_attempts - 1:
                    logger.info("⏳ Waiting 10 seconds before retry...")
                    time.sleep(10)
                    
        logger.error("❌ All upload attempts failed")
        return False
        
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        return False

def main():
    """Main function"""
    success = simple_upload()
    
    if success:
        print("✅ Backup upload completed successfully!")
        return True
    else:
        print("❌ Backup upload failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
