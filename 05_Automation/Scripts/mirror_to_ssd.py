"""
BigSkyAg SSD Mirror
Syncs the Desktop BigSkyAg folder to the SSD for backup and performance
"""

import os
import subprocess
import logging
from pathlib import Path
from config import ensure_critical_folders, DESKTOP_SOURCE, get_folder_path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def mirror_to_ssd():
    """Mirror the Desktop BigSkyAg folder to the SSD"""
    
    # Ensure all critical folders exist
    ensure_critical_folders()
    
    # Get target directory (SSD)
    target = get_folder_path("automation").parent  # Go up one level to get base dir
    
    # Check if source exists
    if not DESKTOP_SOURCE.exists():
        print(f"⏭ Skipping sync: Desktop BigSkyAg folder not found at {DESKTOP_SOURCE}")
        return False
    
    # Check if target exists
    if not target.exists():
        print(f"❌ Target directory does not exist: {target}")
        return False
    
    print(f"🔁 Starting sync from {DESKTOP_SOURCE} → {target}")
    print("📊 This may take a while depending on file sizes...")
    
    try:
        # Run rsync with progress and error handling
        result = subprocess.run([
            "rsync", "-av", "--delete",
            "--exclude", "*.DS_Store",
            "--exclude", "__MACOSX",
            "--exclude", ".git",
            "--exclude", "*.tmp",
            f"{DESKTOP_SOURCE}/",
            f"{target}/"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ SSD sync completed successfully")
            
            # Show some stats if available
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                if lines:
                    print(f"📁 Synced {len(lines)} items")
            
            return True
        else:
            logger.error(f"❌ rsync failed with return code {result.returncode}")
            if result.stderr:
                logger.error(f"Error output: {result.stderr}")
            return False
            
    except FileNotFoundError:
        logger.error("❌ 'rsync' command not found. Please install rsync utility.")
        return False
    except Exception as e:
        logger.error(f"❌ Sync failed: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 Starting BigSkyAg SSD mirror operation...")
    
    success = mirror_to_ssd()
    
    if success:
        print("✅ SSD mirror operation completed successfully")
    else:
        print("❌ SSD mirror operation failed")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

