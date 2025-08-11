#!/usr/bin/env python3
"""
BigSkyAg Company Setup Script
Easy setup for deploying the automation system to any company
"""

import sys
from pathlib import Path
from config import setup_company, get_system_info, COMPANY_TEMPLATES

def show_company_templates():
    """Show available company templates"""
    print("🏢 Available Company Templates:")
    print("=" * 50)
    
    for company_name, template in COMPANY_TEMPLATES.items():
        print(f"\n📋 {company_name}:")
        print(f"   Storage Provider: {template['storage_provider']}")
        print(f"   Description: {template['description']}")
        print(f"   Backup Prefix: {template['backup_prefix']}")

def get_user_input():
    """Get company setup information from user"""
    print("\n🚀 Company Setup Configuration")
    print("=" * 50)
    
    # Company name
    company_name = input("Enter your company name: ").strip()
    if not company_name:
        print("❌ Company name is required")
        return None
    
    # Storage provider
    print(f"\nAvailable storage providers:")
    providers = ["google_drive", "dropbox", "s3", "local"]
    for i, provider in enumerate(providers, 1):
        print(f"   {i}. {provider}")
    
    while True:
        try:
            choice = int(input(f"\nSelect storage provider (1-{len(providers)}): "))
            if 1 <= choice <= len(providers):
                storage_provider = providers[choice - 1]
                break
            else:
                print("❌ Invalid choice. Please select 1-4.")
        except ValueError:
            print("❌ Please enter a number.")
    
    # Custom settings
    print(f"\n📊 Custom Settings (press Enter to use defaults):")
    
    max_working = input(f"Max working backups (default: 1): ").strip()
    max_archive = input(f"Max archive backups (default: 4): ").strip()
    min_size = input(f"Minimum backup size in GB (default: 3.0): ").strip()
    
    custom_settings = {}
    if max_working:
        try:
            custom_settings["max_working_backups"] = int(max_working)
        except ValueError:
            print("⚠️  Invalid max working backups, using default")
    
    if max_archive:
        try:
            custom_settings["max_archive_backups"] = int(max_archive)
        except ValueError:
            print("⚠️  Invalid max archive backups, using default")
    
    if min_size:
        try:
            custom_settings["min_backup_size_gb"] = float(min_size)
        except ValueError:
            print("⚠️  Invalid minimum size, using default")
    
    return {
        "company_name": company_name,
        "storage_provider": storage_provider,
        "custom_settings": custom_settings
    }

def setup_storage_provider(storage_provider, company_name):
    """Guide user through storage provider setup"""
    print(f"\n🔐 Setting up {storage_provider} for {company_name}...")
    print("=" * 50)
    
    if storage_provider == "google_drive":
        print("📋 Google Drive Setup Steps:")
        print("1. Go to Google Cloud Console (https://console.cloud.google.com/)")
        print("2. Create a new project or select existing one")
        print("3. Enable Google Drive API")
        print("4. Create OAuth 2.0 credentials")
        print("5. Download credentials.json")
        print("6. Place credentials.json in the Scripts folder")
        print("\nThen run: python3 authenticate_storage.py google_drive")
        
    elif storage_provider == "dropbox":
        print("📋 Dropbox Setup Steps:")
        print("1. Go to Dropbox App Console (https://www.dropbox.com/developers/apps)")
        print("2. Create a new app")
        print("3. Generate access token")
        print("4. Update config.py with your token")
        print("\nThen run: python3 authenticate_storage.py dropbox")
        
    elif storage_provider == "s3":
        print("📋 AWS S3 Setup Steps:")
        print("1. Create AWS IAM user with S3 access")
        print("2. Generate access key and secret key")
        print("3. Set environment variables:")
        print("   export AWS_ACCESS_KEY_ID=your_key")
        print("   export AWS_SECRET_ACCESS_KEY=your_secret")
        print("4. Update config.py with bucket name and region")
        print("\nThen run: python3 authenticate_storage.py s3")
        
    elif storage_provider == "local":
        print("📋 Local Storage Setup:")
        print("✅ No setup required - local storage works immediately!")
        print("\nThen run: python3 authenticate_storage.py local")

def main():
    """Main company setup function"""
    print("🎯 BigSkyAg Company Setup")
    print("=" * 60)
    print("This script will help you configure the automation system")
    print("for your company with your preferred storage provider.")
    
    # Show available templates
    show_company_templates()
    
    # Get user input
    setup_info = get_user_input()
    if not setup_info:
        return False
    
    # Setup company configuration
    try:
        setup_company(
            setup_info["company_name"],
            setup_info["storage_provider"],
            setup_info["custom_settings"]
        )
        
        # Show final configuration
        print(f"\n✅ Company setup complete!")
        print("=" * 50)
        info = get_system_info()
        for key, value in info.items():
            if key != "critical_folders":
                print(f"   {key}: {value}")
        
        # Guide through storage setup
        setup_storage_provider(setup_info["storage_provider"], setup_info["company_name"])
        
        print(f"\n🎉 {setup_info['company_name']} is now configured!")
        print("💡 Next steps:")
        print("   1. Complete storage provider authentication")
        print("   2. Test the system with: python3 system_health.py")
        print("   3. Run the full system with: ./launch_all.command")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
