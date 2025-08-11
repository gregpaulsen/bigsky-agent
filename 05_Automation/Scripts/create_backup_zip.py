"""
BigSkyAg Backup Creator
Creates timestamped backup zips of the entire BigSkyAg directory
"""

import os
import subprocess
import time
import logging
from pathlib import Path
from config import ensure_critical_folders, get_folder_path, BACKUP_CONFIG

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_zip(source, dest):
    """Create a zip archive of the source directory"""
    print(f"🌀 Creating backup zip...")
    
    # Build exclude patterns for zip command
    exclude_args = []
    for pattern in BACKUP_CONFIG["exclude_patterns"]:
        exclude_args.extend(["-x", pattern])
    
    try:
        result = subprocess.run([
            "zip", "-r", dest, ".", 
            *exclude_args
        ], cwd=source, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Zip command failed: {result.stderr}")
            return False
            
        return True
        
    except FileNotFoundError:
        logger.error("❌ 'zip' command not found. Please install zip utility.")
        return False
    except Exception as e:
        logger.error(f"❌ Zip creation failed: {str(e)}")
        return False

def check_size(path):
    """Check the size of the zip file and return in GB"""
    try:
        size_bytes = os.path.getsize(path)
        size_gb = round(size_bytes / (1024**3), 2)
        print(f"🗜️  Zip file size: {size_gb} GB")
        return size_gb
    except OSError as e:
        logger.error(f"❌ Failed to check file size: {str(e)}")
        return 0

def main():
    """Main backup creation function"""
    
    # Ensure all critical folders exist
    ensure_critical_folders()
    
    # Get paths from config
    source_folder = get_folder_path("automation").parent  # Go up one level to get base dir
    backup_folder = get_folder_path("backups")
    
    if not source_folder.exists():
        logger.error(f"❌ Source folder does not exist: {source_folder}")
        return False
    
    # Create backup folder if it doesn't exist
    if not backup_folder.exists():
        backup_folder.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created backup folder: {backup_folder}")
    
    # Generate backup filename with timestamp
    date = time.strftime("%Y-%m-%d_%H%M")
    # Use backup prefix from config for white-labeling
    from config import STORAGE_CONFIG
    zip_name = f"{STORAGE_CONFIG['backup_prefix']}_{date}.zip"
    zip_path = backup_folder / zip_name
    
    print(f"📦 Creating backup: {zip_name}")
    print(f"📁 Source: {source_folder}")
    print(f"💾 Destination: {zip_path}")
    
    # Create the backup
    start_time = time.time()
    success = create_zip(source_folder, zip_path)
    duration = round(time.time() - start_time, 2)
    
    if success and zip_path.exists():
        size_gb = check_size(zip_path)
        
        if size_gb < BACKUP_CONFIG["min_size_gb"]:
            print(f"⚠️  WARNING: Zip size ({size_gb} GB) is smaller than expected minimum ({BACKUP_CONFIG['min_size_gb']} GB)")
            print("   This may indicate an incomplete backup!")
        else:
            print(f"✅ Backup completed successfully in {duration} seconds")
            print(f"📁 Backup location: {zip_path}")
            
        return True
    else:
        logger.error("❌ Backup creation failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

