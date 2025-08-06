#!/bin/bash
echo "🚦 Starting BigSkyAg system..."

# Check if SSD is mounted
if [ ! -d "/Volumes/BigSkySSD" ]; then
    echo "⚠️  SSD not detected at /Volumes/BigSkySSD"
    echo "⏭ Skipping sync and backup."
else
    echo "✅ SSD detected. Proceeding with full system run..."
    python3 /Volumes/BigSkySSD/BigSkyAg/05_Automation/Scripts/router.py
    python3 /Volumes/BigSkySSD/BigSkyAg/05_Automation/Scripts/mirror_to_ssd.py
    python3 /Volumes/BigSkySSD/BigSkyAg/05_Automation/Scripts/create_backup_zip.py
    python3 /Volumes/BigSkySSD/BigSkyAg/05_Automation/Scripts/cleanup_old_backups.py
fi

echo "✅ All systems complete."

