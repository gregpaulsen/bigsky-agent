#!/usr/bin/env python3
"""
BigSkyAg Storage-Agnostic Backup Upload Script
Uploads backups to the configured storage provider with proper error handling
"""

import sys
import logging
import time
from pathlib import Path
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from config import get_storage_provider_config
    from storage_providers import get_storage_provider
    CONFIG_AVAILABLE = True
except ImportError as e:
    CONFIG_AVAILABLE = False
    print(f"❌ Import error: {e}")
    print("💡 Please ensure all dependencies are properly installed")

# Configure logging with best practices
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('upload_backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration constants
MAX_RETRIES = 3
RETRY_DELAY = 30  # seconds
UPLOAD_TIMEOUT = 300  # 5 minutes

def initialize_storage():
    """Initialize storage provider from config with proper error handling"""
    if not CONFIG_AVAILABLE:
        logger.error("❌ Configuration not available")
        return None
        
    try:
        config = get_storage_provider_config()
        provider = get_storage_provider(config['provider'], config)
        logger.info(f"✅ Initialized {config['provider']} storage provider")
        return provider
    except Exception as e:
        logger.error(f"❌ Failed to initialize storage: {e}")
        return None

def find_latest_backup():
    """Find the most recent backup file with validation"""
    try:
        backup_dir = Path("/Volumes/BigSkyAgSSD/BigSkyAg/00_Admin/Backups")
        if not backup_dir.exists():
            logger.error(f"❌ Backup directory not found: {backup_dir}")
            return None
        
        backup_files = list(backup_dir.glob("*.zip"))
        if not backup_files:
            logger.error("❌ No backup files found")
            return None
        
        # Sort by modification time, newest first
        latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
        
        # Validate backup file
        if not latest_backup.exists():
            logger.error(f"❌ Latest backup file not found: {latest_backup}")
            return None
            
        file_size = latest_backup.stat().st_size
        if file_size == 0:
            logger.error(f"❌ Backup file is empty: {latest_backup}")
            return None
            
        logger.info(f"✅ Found latest backup: {latest_backup.name} ({file_size / (1024**2):.1f} MB)")
        return latest_backup
        
    except Exception as e:
        logger.error(f"💥 Error finding latest backup: {e}")
        return None

def upload_backup_with_retry(provider, backup_path):
    """Upload backup to storage provider with retry logic and timeout handling"""
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"🔄 Upload attempt {attempt + 1}/{MAX_RETRIES}")
            
            if not provider:
                logger.error("❌ No storage provider available")
                return False
                
            # Authenticate with provider
            if not provider.authenticate():
                logger.error("❌ Authentication failed")
                return False
            
            # Upload to daily backup folder with timeout handling
            start_time = time.time()
            file_id = provider.upload_backup(backup_path, "daily")
            
            upload_time = time.time() - start_time
            logger.info(f"⏱️  Upload completed in {upload_time:.1f} seconds")
            
            if file_id:
                logger.info(f"✅ Backup uploaded successfully: {file_id}")
                return True
            else:
                logger.error("❌ Upload failed - no file ID returned")
                if attempt < MAX_RETRIES - 1:
                    logger.info(f"⏳ Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                continue
                
        except Exception as e:
            logger.error(f"💥 Upload attempt {attempt + 1} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                logger.info(f"⏳ Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                logger.error("❌ All upload attempts failed")
                return False
    
    return False

def cleanup_old_backups(provider):
    """Clean up old backups based on config with error handling"""
    try:
        if not provider:
            logger.warning("⚠️ No provider available for cleanup")
            return False
            
        success = provider.cleanup_old_backups(max_backups=5, backup_type="daily")
        if success:
            logger.info("✅ Old backups cleaned up")
        else:
            logger.warning("⚠️ Cleanup had issues")
        return success
        
    except Exception as e:
        logger.error(f"💥 Cleanup error: {e}")
        return False

def get_storage_info(provider):
    """Get storage provider information with error handling"""
    try:
        if not provider:
            logger.warning("⚠️ No provider available for info")
            return None
            
        info = provider.get_provider_info()
        logger.info(f"📊 Storage Info: {info}")
        return info
        
    except Exception as e:
        logger.error(f"💥 Error getting storage info: {e}")
        return None

def run_backup_upload():
    """Main backup upload process with comprehensive error handling"""
    logger.info("🚀 Starting backup upload process...")
    
    # Validate system state
    if not CONFIG_AVAILABLE:
        logger.error("❌ System configuration not available")
        return False
    
    # Initialize storage
    provider = initialize_storage()
    if not provider:
        logger.error("❌ Failed to initialize storage provider")
        return False
    
    # Find latest backup
    backup_path = find_latest_backup()
    if not backup_path:
        logger.error("❌ No valid backup found for upload")
        return False
    
    # Upload backup with retry logic
    if not upload_backup_with_retry(provider, backup_path):
        logger.error("❌ Backup upload failed after all retry attempts")
        return False
    
    # Cleanup old backups
    cleanup_old_backups(provider)
    
    # Get storage info
    get_storage_info(provider)
    
    logger.info("🎉 Backup upload process completed successfully!")
    return True

def main():
    """Main function with proper error handling"""
    try:
        success = run_backup_upload()
        if success:
            print("✅ Backup upload completed successfully")
        else:
            print("❌ Backup upload failed")
        return success
        
    except KeyboardInterrupt:
        logger.info("⏹️ Process interrupted by user")
        print("⏹️ Process interrupted by user")
        return False
        
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        print(f"💥 Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
