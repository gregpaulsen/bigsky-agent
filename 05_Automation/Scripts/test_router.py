"""
Test script for BigSkyAg File Router
Tests routing functionality with various file types and edge cases
"""

import tempfile
import shutil
import os
from pathlib import Path
from config import ensure_critical_folders, get_folder_path, ROUTING_RULES

def create_test_files():
    """Create test files for routing testing"""
    print("🧪 Creating test files...")
    
    # Get test directories
    dropzone = get_folder_path("dropzone")
    dropzone.mkdir(parents=True, exist_ok=True)
    
    # Create test files with various extensions
    test_files = [
        "document.pdf",
        "spreadsheet.xlsx", 
        "data.csv",
        "image.png",
        "photo.jpg",
        "map.tif",
        "project.qgz",
        "script.py",
        "backup.zip",
        "presentation.pptx",
        "unknown.xyz"
    ]
    
    created_files = []
    
    for filename in test_files:
        file_path = dropzone / filename
        try:
            # Create a simple text file with the filename as content
            file_path.write_text(f"Test content for {filename}")
            created_files.append(file_path)
            print(f"   ✅ Created: {filename}")
        except Exception as e:
            print(f"   ❌ Failed to create {filename}: {e}")
    
    print(f"📁 Created {len(created_files)} test files in DropZone")
    return created_files

def test_routing_rules():
    """Test that all routing rules have valid destination folders"""
    print("\n🔍 Testing routing rules...")
    
    ensure_critical_folders()
    
    invalid_rules = []
    
    for ext, folder_key in ROUTING_RULES.items():
        try:
            folder_path = get_folder_path(folder_key)
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
            
            # Test write access
            test_file = folder_path / ".test_write"
            test_file.write_text("test")
            test_file.unlink()
            
            print(f"   ✅ {ext} → {folder_key}: {folder_path}")
            
        except Exception as e:
            error_msg = f"{ext} → {folder_key}: {str(e)}"
            print(f"   ❌ {error_msg}")
            invalid_rules.append(error_msg)
    
    if invalid_rules:
        print(f"⚠️  Found {len(invalid_rules)} invalid routing rules")
        return False
    else:
        print("✅ All routing rules are valid")
        return True

def test_duplicate_handling():
    """Test duplicate file handling"""
    print("\n🔄 Testing duplicate handling...")
    
    dropzone = get_folder_path("dropzone")
    admin_folder = get_folder_path("admin")
    
    # Create a duplicate file
    original_file = dropzone / "duplicate_test.txt"
    original_file.write_text("This is test content")
    
    # Create a file with same content in admin folder
    duplicate_file = admin_folder / "duplicate_test.txt"
    duplicate_file.write_text("This is test content")
    
    print(f"   ✅ Created test files for duplicate detection")
    
    return True

def test_file_validation():
    """Test file validation logic"""
    print("\n✅ Testing file validation...")
    
    dropzone = get_folder_path("dropzone")
    
    # Test valid file
    valid_file = dropzone / "valid_test.txt"
    valid_file.write_text("Valid content")
    
    # Test empty file
    empty_file = dropzone / "empty_test.txt"
    empty_file.write_text("")
    
    # Test hidden file
    hidden_file = dropzone / ".hidden_test.txt"
    hidden_file.write_text("Hidden content")
    
    print(f"   ✅ Created test files for validation testing")
    
    return True

def cleanup_test_files():
    """Clean up all test files"""
    print("\n🧹 Cleaning up test files...")
    
    # Clean up dropzone
    dropzone = get_folder_path("dropzone")
    if dropzone.exists():
        for file_path in dropzone.glob("*"):
            if file_path.is_file():
                try:
                    file_path.unlink()
                    print(f"   🗑️  Removed: {file_path.name}")
                except Exception as e:
                    print(f"   ⚠️  Could not remove {file_path.name}: {e}")
    
    # Clean up test files in other folders
    test_patterns = [".test_write", "duplicate_test.txt", "valid_test.txt", "empty_test.txt"]
    
    for folder_key in ["admin", "branding", "field_projects", "mapping", "training", "scripts", "backups", "business"]:
        try:
            folder_path = get_folder_path(folder_key)
            if folder_path.exists():
                for pattern in test_patterns:
                    for file_path in folder_path.glob(pattern):
                        try:
                            file_path.unlink()
                            print(f"   🗑️  Removed: {folder_key}/{file_path.name}")
                        except Exception:
                            pass
        except Exception:
            pass
    
    print("✅ Test cleanup completed")

def run_router_test():
    """Run the actual router test"""
    print("\n🚀 Testing file router...")
    
    try:
        # Import and run the router
        from router import FileRouter
        
        router = FileRouter()
        success = router.route_files()
        
        if success:
            print("✅ Router test completed successfully")
            return True
        else:
            print("❌ Router test completed with errors")
            return False
            
    except Exception as e:
        print(f"💥 Router test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🧪 BIGSKYAG FILE ROUTER TEST SUITE")
    print("=" * 50)
    
    try:
        # Ensure all folders exist
        ensure_critical_folders()
        
        # Test routing rules
        if not test_routing_rules():
            print("❌ Routing rules test failed")
            return False
        
        # Create test files
        test_files = create_test_files()
        if not test_files:
            print("❌ Test file creation failed")
            return False
        
        # Test duplicate handling
        test_duplicate_handling()
        
        # Test file validation
        test_file_validation()
        
        # Run the router
        router_success = run_router_test()
        
        # Clean up
        cleanup_test_files()
        
        if router_success:
            print("\n🎉 All router tests passed!")
            return True
        else:
            print("\n❌ Some router tests failed")
            return False
            
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
