"""
BigSkyAg Backup Cleanup
Keeps only the most recent backups and removes old ones
"""

import logging
from pathlib import Path
from config import ensure_critical_folders, get_folder_path, BACKUP_CONFIG, STORAGE_CONFIG

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def cleanup_old_backups():
    """Remove old backup files, keeping only the most recent ones"""
    
    # Ensure all critical folders exist
    ensure_critical_folders()
    
    # Get backup folder path
    backup_folder = get_folder_path("backups")
    
    if not backup_folder.exists():
        print(f"ℹ️  Backup folder does not exist: {backup_folder}")
        return True
    
    # Find all backup zip files (white-label prefix)
    backup_pattern = f"{STORAGE_CONFIG['backup_prefix']}_*.zip"
    zips = sorted(
        backup_folder.glob(backup_pattern), 
        key=lambda f: f.stat().st_mtime, 
        reverse=True
    )
    
    if not zips:
        print("ℹ️  No backup files found")
        return True
    
    print(f"📦 Found {len(zips)} backup files")
    
    # Rotation strategy:
    # - Keep 1 latest backup in Backups (working)
    # - Move older ones to Backups/Archive
    # - Keep only N in Archive
    working_keep = BACKUP_CONFIG.get("max_working_backups", 1)
    archive_keep = BACKUP_CONFIG.get("max_archive_backups", 4)

    archive_folder = backup_folder / "Archive"
    archive_folder.mkdir(parents=True, exist_ok=True)

    # Move older backups to Archive
    to_archive = zips[working_keep:]
    for old_zip in to_archive:
        target = archive_folder / old_zip.name
        if not target.exists():
            try:
                old_zip.rename(target)
                print(f"📦 Moved to Archive: {old_zip.name}")
            except Exception as e:
                logger.error(f"Failed to move {old_zip.name} to Archive: {e}")

    # Prune archive
    archives = sorted(
        archive_folder.glob(backup_pattern),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )
    to_delete = archives[archive_keep:]
    for old in to_delete:
        try:
            size_mb = round(old.stat().st_size / (1024**2), 1)
            print(f"   🗑️  Deleting from Archive: {old.name} ({size_mb} MB)")
            old.unlink()
        except Exception as e:
            logger.error(f"Failed to delete {old.name} from Archive: {e}")

    print("✅ Backup rotation complete")
    return True

if __name__ == "__main__":
    success = cleanup_old_backups()
    exit(0 if success else 1)

