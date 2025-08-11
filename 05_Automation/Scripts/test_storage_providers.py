#!/usr/bin/env python3
"""
Test script for storage providers
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_storage_providers():
    """Test the storage provider system"""
    print("🧪 Testing Storage Provider System")
    print("=" * 50)
    
    try:
        # Test 1: Import storage providers
        print("1. Testing storage_providers import...")
        from storage_providers import get_storage_provider
        print("   ✅ storage_providers imported successfully")
        
        # Test 2: Test local provider with minimal config
        print("\n2. Testing local provider...")
        local_config = {
            "provider": "local",
            "company_name": "TestCompany",
            "backup_prefix": "Test_Backup",
            "storage_path": Path("/tmp/test_storage")
        }
        
        local_provider = get_storage_provider("local", local_config)
        print(f"   ✅ Local provider created: {type(local_provider).__name__}")
        
        # Test 3: Test provider methods
        print("\n3. Testing provider methods...")
        info = local_provider.get_provider_info()
        print(f"   ✅ Provider info: {info}")
        
        # Test 4: Test authentication
        print("\n4. Testing authentication...")
        auth_result = local_provider.authenticate()
        print(f"   ✅ Authentication: {auth_result}")
        
        # Test 5: Test connection
        print("\n5. Testing connection...")
        conn_result = local_provider.test_connection()
        print(f"   ✅ Connection test: {conn_result}")
        
        print("\n🎉 All tests passed! Storage provider system is working.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_storage_providers()
    sys.exit(0 if success else 1)
