#!/usr/bin/env python3
"""
BigSkyAg Folder Structure Creator
Standalone script to create the complete BigSkyAg folder structure
"""

import os
import sys
from pathlib import Path

# Configuration
BASE_DIR = Path("/Volumes/BigSkyAgSSD/BigSkyAg")

# Complete folder structure
FOLDER_STRUCTURE = {
    "00_Admin": [
        "Backups",
        "Budget", 
        "CRM_Data_Exports",
        "EIN_Articles_DVBE-SDVOSB",
        "Grants"
    ],
    "01_Branding": [
        "Logos",
        "Marketing_Materials"
    ],
    "02_Field_Projects": [
        "Source_Data",
        "GIS_Projects",
        "Drone_Data",
        "Field_Reports"
    ],
    "03_Mapping_QGIS": [
        "QGIS_Projects",
        "Target_Farms_GPKG",
        "Scouting_Notes"
    ],
    "04_Training": [
        "Part107Training",
        "Drone_Operations",
        "Safety_Protocols",
        "Certification_Materials"
    ],
    "05_Automation": [
        "Scripts",
        "Automation_Files",
        "BigSkyAgent",
        "GPT_Save_Sheets",
        "Make.com",
        "VSCode"
    ],
    "06_Business_Strategy": [
        "Business_Models",
        "KyleOps_Master_Files",
        "Pricing_Logic",
        "Market_Research"
    ],
    "BigSkyAgDropZone": [],
    "Z_Archive": [
        "Old_Versions",
        "Duplicate_Files",
        "Temporary_Files"
    ],
    "98_Tests": [],
    "99_Scripts_and_Structure": []
}

def check_ssd_mount():
    """Check if the SSD is mounted and accessible"""
    print("🔍 Checking SSD mount status...")
    
    ssd_volume = BASE_DIR.parent
    if not ssd_volume.exists():
        print(f"❌ SSD volume not found at: {ssd_volume}")
        print("💡 Please ensure the SSD is mounted and try again")
        return False
    
    print(f"✅ SSD volume accessible: {ssd_volume}")
    return True

def create_folder_structure():
    """Create the complete BigSkyAg folder structure"""
    print(f"\n🏗️  Creating BigSkyAg folder structure at: {BASE_DIR}")
    print("=" * 60)
    
    created_folders = []
    existing_folders = []
    failed_folders = []
    
    # Create main directory
    try:
        BASE_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ Main directory: {BASE_DIR}")
    except Exception as e:
        print(f"❌ Failed to create main directory: {e}")
        return False
    
    # Create all subdirectories
    for main_folder, subfolders in FOLDER_STRUCTURE.items():
        main_path = BASE_DIR / main_folder
        
        try:
            # Create main folder
            main_path.mkdir(exist_ok=True)
            if main_path.exists():
                if main_path.stat().st_mtime < os.path.getmtime(__file__):
                    print(f"✅ Created: {main_folder}")
                    created_folders.append(main_folder)
                else:
                    print(f"ℹ️  Exists: {main_folder}")
                    existing_folders.append(main_folder)
            
            # Create subfolders
            for subfolder in subfolders:
                sub_path = main_path / subfolder
                try:
                    sub_path.mkdir(exist_ok=True)
                    if sub_path.exists():
                        print(f"   ✅ {main_folder}/{subfolder}")
                except Exception as e:
                    print(f"   ❌ Failed to create {main_folder}/{subfolder}: {e}")
                    failed_folders.append(f"{main_folder}/{subfolder}")
                    
        except Exception as e:
            print(f"❌ Failed to create {main_folder}: {e}")
            failed_folders.append(main_folder)
    
    # Create special files
    special_files = {
        "README.md": "# BigSkyAg\n\nAgricultural automation and data management system.",
        ".gitignore": "*.DS_Store\n*.tmp\n*.log\n__pycache__/\n*.pyc",
        "folder_structure.md": f"# BigSkyAg Folder Structure\n\nBase directory: {BASE_DIR}\n\nThis document describes the folder structure."
    }
    
    for filename, content in special_files.items():
        file_path = BASE_DIR / filename
        try:
            if not file_path.exists():
                file_path.write_text(content)
                print(f"📄 Created: {filename}")
            else:
                print(f"ℹ️  Exists: {filename}")
        except Exception as e:
            print(f"❌ Failed to create {filename}: {e}")
    
    # Summary report
    print("\n" + "=" * 60)
    print("📊 FOLDER CREATION SUMMARY")
    print("=" * 60)
    print(f"✅ Newly created: {len(created_folders)}")
    print(f"ℹ️  Already existed: {len(existing_folders)}")
    print(f"❌ Failed: {len(failed_folders)}")
    
    if created_folders:
        print(f"\n🆕 Newly created folders:")
        for folder in created_folders:
            print(f"   - {folder}")
    
    if failed_folders:
        print(f"\n💥 Failed to create:")
        for folder in failed_folders:
            print(f"   - {folder}")
    
    print("\n" + "=" * 60)
    
    return len(failed_folders) == 0

def verify_structure():
    """Verify the created folder structure"""
    print(f"\n🔍 Verifying folder structure...")
    
    verification_errors = []
    
    for main_folder, subfolders in FOLDER_STRUCTURE.items():
        main_path = BASE_DIR / main_folder
        
        if not main_path.exists():
            verification_errors.append(f"Main folder missing: {main_folder}")
            continue
            
        if not main_path.is_dir():
            verification_errors.append(f"Not a directory: {main_folder}")
            continue
            
        # Check subfolders
        for subfolder in subfolders:
            sub_path = main_path / subfolder
            if not sub_path.exists():
                verification_errors.append(f"Subfolder missing: {main_folder}/{subfolder}")
            elif not sub_path.is_dir():
                verification_errors.append(f"Not a directory: {main_folder}/{subfolder}")
    
    if verification_errors:
        print(f"❌ Verification found {len(verification_errors)} issues:")
        for error in verification_errors:
            print(f"   - {error}")
        return False
    else:
        print("✅ All folders verified successfully!")
        return True

def main():
    """Main function"""
    print("🚀 BigSkyAg Folder Structure Creator")
    print("=" * 60)
    
    # Check SSD mount
    if not check_ssd_mount():
        return False
    
    # Create folder structure
    if not create_folder_structure():
        print("❌ Folder creation failed")
        return False
    
    # Verify structure
    if not verify_structure():
        print("❌ Structure verification failed")
        return False
    
    print(f"\n🎉 BigSkyAg folder structure created successfully!")
    print(f"📁 Location: {BASE_DIR}")
    print(f"💡 You can now run the automation scripts")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
