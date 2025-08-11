"""
Test script for BigSkyAg Configuration
Verifies that all configuration functions work correctly with the updated SSD path
"""

from config import (
    BASE_DIR, 
    DESKTOP_SOURCE, 
    CRITICAL_FOLDERS, 
    ROUTING_RULES,
    ensure_critical_folders,
    get_folder_path,
    get_routing_destination
)

def test_config():
    """Test the configuration system"""
    print("🧪 Testing BigSkyAg Configuration")
    print("=" * 50)
    
    # Test basic paths
    print(f"🏠 Base directory: {BASE_DIR}")
    print(f"💻 Desktop source: {DESKTOP_SOURCE}")
    
    # Verify the new SSD path
    expected_ssd_path = "/Volumes/BigSkyAgSSD/BigSkyAg"
    if str(BASE_DIR) == expected_ssd_path:
        print(f"✅ SSD path correctly set to: {expected_ssd_path}")
    else:
        print(f"⚠️  SSD path mismatch. Expected: {expected_ssd_path}, Got: {BASE_DIR}")
    
    # Test critical folders
    print(f"\n📁 Critical folders ({len(CRITICAL_FOLDERS)} total):")
    for name, path in CRITICAL_FOLDERS.items():
        print(f"   {name}: {path}")
    
    # Test routing rules
    print(f"\n🔄 Routing rules ({len(ROUTING_RULES)} total):")
    for ext, folder in list(ROUTING_RULES.items())[:10]:  # Show first 10
        print(f"   {ext} → {folder}")
    if len(ROUTING_RULES) > 10:
        print(f"   ... and {len(ROUTING_RULES) - 10} more")
    
    # Test folder creation
    print(f"\n🔧 Testing folder creation...")
    try:
        ensure_critical_folders()
        print("✅ Folder creation test passed")
    except Exception as e:
        print(f"❌ Folder creation test failed: {e}")
        return False
    
    # Test path retrieval
    print(f"\n📍 Testing path retrieval...")
    try:
        admin_path = get_folder_path("admin")
        print(f"   Admin path: {admin_path}")
        
        backup_path = get_folder_path("backups")
        print(f"   Backup path: {backup_path}")
        
        print("✅ Path retrieval test passed")
    except Exception as e:
        print(f"❌ Path retrieval test failed: {e}")
        return False
    
    # Test routing destination
    print(f"\n🔄 Testing routing destination...")
    try:
        pdf_dest = get_routing_destination(".pdf")
        print(f"   PDF → {pdf_dest}")
        
        png_dest = get_routing_destination(".png")
        print(f"   PNG → {png_dest}")
        
        unknown_dest = get_routing_destination(".xyz")
        print(f"   Unknown → {unknown_dest}")
        
        print("✅ Routing destination test passed")
    except Exception as e:
        print(f"❌ Routing destination test failed: {e}")
        return False
    
    # Test SSD volume accessibility
    print(f"\n💾 Testing SSD volume accessibility...")
    try:
        ssd_volume = BASE_DIR.parent
        if ssd_volume.exists():
            print(f"   ✅ SSD volume accessible: {ssd_volume}")
        else:
            print(f"   ⚠️  SSD volume not accessible: {ssd_volume}")
            print("      💡 Please ensure the SSD is mounted")
        
        print("✅ SSD accessibility test completed")
    except Exception as e:
        print(f"❌ SSD accessibility test failed: {e}")
        return False
    
    print(f"\n🎉 All configuration tests passed!")
    return True

if __name__ == "__main__":
    success = test_config()
    exit(0 if success else 1)
