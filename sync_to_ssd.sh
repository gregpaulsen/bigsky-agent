#!/bin/bash

echo "🔄 BigSkyAg SSD Sync Script"
echo "============================"

# Check if SSD is mounted
if [ ! -d "/Volumes/BigSkyAgSSD" ]; then
    echo "❌ SSD not detected at /Volumes/BigSkyAgSSD"
    echo "💡 Please mount your SSD and try again."
    exit 1
fi

# Source and destination paths
SOURCE="/Users/gregpaulsen/Desktop/BigSkyAg"
TARGET="/Volumes/BigSkyAgSSD/BigSkyAg"

# Check if source exists
if [ ! -d "$SOURCE" ]; then
    echo "❌ Source directory not found: $SOURCE"
    echo "💡 Please ensure the BigSkyAg folder exists on your Desktop."
    exit 1
fi

echo "📁 Source: $SOURCE"
echo "💾 Target: $TARGET"
echo ""

echo "🚀 Starting sync operation..."
echo "📊 This may take a while depending on file sizes..."

# Run rsync with progress and error handling
rsync -av --delete \
    --exclude="*.DS_Store" \
    --exclude="__MACOSX" \
    --exclude=".git" \
    --exclude="*.tmp" \
    "$SOURCE/" "$TARGET/"

# Check if rsync was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SSD sync completed successfully!"
    echo "📁 All files have been synchronized to the SSD."
else
    echo ""
    echo "❌ SSD sync failed!"
    echo "💡 Please check the error messages above and try again."
    exit 1
fi

