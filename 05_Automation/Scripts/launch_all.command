#!/bin/bash

echo "🚦 Starting BigSkyAg system..."
echo "=================================="

# Check if SSD is mounted
if [ ! -d "/Volumes/BigSkyAgSSD" ]; then
    echo "⚠️  SSD not detected at /Volumes/BigSkyAgSSD"
    echo "⏭ Skipping sync and backup operations."
    echo "💡 Please mount your SSD and try again."
    exit 1
fi

echo "✅ SSD detected. Proceeding with full system run..."
echo ""

# Get the script directory
SCRIPT_DIR="/Volumes/BigSkyAgSSD/BigSkyAg/05_Automation/Scripts"

# Check if scripts directory exists
if [ ! -d "$SCRIPT_DIR" ]; then
    echo "❌ Scripts directory not found: $SCRIPT_DIR"
    echo "💡 Please ensure the BigSkyAg folder is properly synced to the SSD."
    exit 1
fi

# Change to scripts directory
cd "$SCRIPT_DIR"

echo "🔧 Step 1: Ensuring critical folders exist..."
python3 config.py

echo ""
echo "📂 Step 2: Routing files from DropZone..."
python3 router.py

echo ""
echo "🔄 Step 3: Syncing to SSD..."
python3 mirror_to_ssd.py

echo ""
echo "📦 Step 4: Creating backup..."
python3 create_backup_zip.py

echo ""
echo "🧹 Step 5: Cleaning up old backups..."
python3 cleanup_old_backups.py

echo ""
echo "☁️  Step 6: Uploading backup to configured storage..."
python3 upload_backup.py daily | cat

echo ""
echo "🏥 Step 7: Running system health check..."
python3 system_health.py | cat

echo ""
echo "✅ All systems complete!"
echo "=================================="
echo "📊 System Status:"
echo "   • File routing: Complete"
echo "   • SSD sync: Complete" 
echo "   • Backup creation: Complete"
echo "   • Cleanup: Complete"
echo "   • Cloud upload: Complete"
echo "   • Health check: Complete"

echo ""
echo "🎯 System is ready for production use!"
echo "💡 For company-specific setup, edit config.py COMPANY_SETTINGS"

