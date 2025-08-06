from pathlib import Path

BACKUP_FOLDER = Path("/Volumes/BigSkySSD/BigSkyAg/07_Backups")
zips = sorted(BACKUP_FOLDER.glob("BigSkyAg_Backup_*.zip"), key=lambda f: f.stat().st_mtime, reverse=True)

for old_zip in zips[2:]:
    print(f"🗑 Deleting old backup: {old_zip.name}")
    old_zip.unlink()

print("✅ Kept most recent 2 backups.")

