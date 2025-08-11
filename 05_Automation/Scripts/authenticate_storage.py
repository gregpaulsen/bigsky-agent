#!/usr/bin/env python3
"""
BigSkyAg Storage-Agnostic Authentication
Sets up authentication for any configured storage provider
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any

from config import STORAGE_CONFIG, get_storage_provider_config
from storage_providers import get_storage_provider

# Set up logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('authenticate_storage.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StorageAuthenticator:
    """Storage-agnostic authentication manager"""
    
    def __init__(self):
        self.storage_config = STORAGE_CONFIG
        self.current_provider = self.storage_config["provider"]
        
    def list_available_providers(self) -> list:
        """List all available storage providers"""
        return list(self.storage_config["providers"].keys())
    
    def get_provider_requirements(self, provider_name: str) -> Dict[str, Any]:
        """Get authentication requirements for a specific provider"""
        if provider_name not in self.storage_config["providers"]:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        requirements = {
            "google_drive": {
                "description": "Google Drive OAuth2 Authentication",
                "steps": [
                    "1. Go to Google Cloud Console",
                    "2. Create a project and enable Drive API",
                    "3. Create OAuth2 credentials",
                    "4. Download credentials.json",
                    "5. Place in Scripts folder"
                ],
                "files_needed": ["credentials.json"],
                "setup_command": "python3 authenticate_storage.py google_drive"
            },
            "dropbox": {
                "description": "Dropbox Access Token Authentication",
                "steps": [
                    "1. Go to Dropbox App Console",
                    "2. Create a new app",
                    "3. Generate access token",
                    "4. Save token to dropbox_token.json"
                ],
                "files_needed": ["dropbox_token.json"],
                "setup_command": "python3 authenticate_storage.py dropbox"
            },
            "s3": {
                "description": "AWS S3 Credentials Authentication",
                "steps": [
                    "1. Create AWS IAM user with S3 access",
                    "2. Generate access key and secret key",
                    "3. Set environment variables:",
                    "   export AWS_ACCESS_KEY_ID=your_key",
                    "   export AWS_SECRET_ACCESS_KEY=your_secret"
                ],
                "files_needed": [],
                "setup_command": "python3 authenticate_storage.py s3"
            },
            "local": {
                "description": "Local Storage (No Authentication Required)",
                "steps": [
                    "1. No authentication required",
                    "2. Files stored locally on disk"
                ],
                "files_needed": [],
                "setup_command": "python3 authenticate_storage.py local"
            }
        }
        
        return requirements.get(provider_name, {})
    
    def authenticate_google_drive(self) -> bool:
        """Authenticate with Google Drive"""
        try:
            logger.info("🔐 Setting up Google Drive authentication...")
            
            # Check if credentials file exists
            creds_path = Path(self.storage_config["providers"]["google_drive"]["credentials_path"])
            if not creds_path.exists():
                logger.error(f"❌ Credentials file not found: {creds_path}")
                logger.error("Please download credentials.json from Google Cloud Console")
                return False
            
            # Import Google Drive specific modules
            from google_auth_oauthlib.flow import InstalledAppFlow
            
            # OAuth2 flow
            flow = InstalledAppFlow.from_client_secrets_file(
                str(creds_path), 
                ["https://www.googleapis.com/auth/drive.file"]
            )
            
            # Run local server for authentication
            logger.info("🌐 Opening browser for authentication...")
            creds = flow.run_local_server(port=0)
            
            # Save the credentials
            token_path = Path(self.storage_config["providers"]["google_drive"]["token_path"])
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
            
            logger.info(f"✅ Google Drive authentication complete!")
            logger.info(f"💾 Token saved as: {token_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Google Drive authentication failed: {str(e)}")
            return False
    
    def authenticate_dropbox(self) -> bool:
        """Authenticate with Dropbox"""
        try:
            logger.info("🔐 Setting up Dropbox authentication...")
            
            # Check if dropbox package is installed
            try:
                import dropbox
            except ImportError:
                logger.error("❌ Dropbox package not installed")
                logger.error("Install with: pip install dropbox")
                return False
            
            # Get access token from user
            print("\n📝 Dropbox Authentication Setup")
            print("=" * 50)
            print("1. Go to: https://www.dropbox.com/developers/apps")
            print("2. Create a new app")
            print("3. Generate an access token")
            print("4. Enter the token below:")
            
            access_token = input("\nEnter your Dropbox access token: ").strip()
            
            if not access_token:
                logger.error("❌ No access token provided")
                return False
            
            # Test the token
            try:
                dbx = dropbox.Dropbox(access_token)
                account = dbx.users_get_current_account()
                logger.info(f"✅ Dropbox authentication successful!")
                logger.info(f"   Account: {account.name.display_name}")
                logger.info(f"   Email: {account.email}")
                
                # Save token to file
                token_path = Path("dropbox_token.json")
                token_data = {
                    "access_token": access_token,
                    "account_name": account.name.display_name,
                    "email": account.email
                }
                
                import json
                with open(token_path, 'w') as f:
                    json.dump(token_data, f, indent=2)
                
                logger.info(f"💾 Token saved as: {token_path}")
                return True
                
            except Exception as e:
                logger.error(f"❌ Invalid access token: {str(e)}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Dropbox authentication failed: {str(e)}")
            return False
    
    def authenticate_s3(self) -> bool:
        """Authenticate with AWS S3"""
        try:
            logger.info("🔐 Setting up AWS S3 authentication...")
            
            # Check if boto3 is installed
            try:
                import boto3
            except ImportError:
                logger.error("❌ boto3 package not installed")
                logger.error("Install with: pip install boto3")
                return False
            
            # Check environment variables
            access_key = os.environ.get('AWS_ACCESS_KEY_ID')
            secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
            
            if not access_key or not secret_key:
                logger.error("❌ AWS credentials not found in environment variables")
                logger.error("Please set:")
                logger.error("  export AWS_ACCESS_KEY_ID=your_access_key")
                logger.error("  export AWS_SECRET_ACCESS_KEY=your_secret_key")
                return False
            
            # Test credentials
            try:
                sts = boto3.client('sts')
                identity = sts.get_caller_identity()
                logger.info(f"✅ AWS S3 authentication successful!")
                logger.info(f"   Account: {identity['Account']}")
                logger.info(f"   User: {identity['Arn']}")
                return True
                
            except Exception as e:
                logger.error(f"❌ Invalid AWS credentials: {str(e)}")
                return False
            
        except Exception as e:
            logger.error(f"❌ AWS S3 authentication failed: {str(e)}")
            return False
    
    def authenticate_local(self) -> bool:
        """Set up local storage (no authentication required)"""
        try:
            logger.info("🔐 Setting up local storage...")
            
            # Create local storage directory
            storage_path = Path(self.storage_config["providers"]["local"]["storage_path"])
            storage_path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"✅ Local storage setup complete!")
            logger.info(f"   Storage path: {storage_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Local storage setup failed: {str(e)}")
            return False
    
    def authenticate_provider(self, provider_name: str = None) -> bool:
        """Authenticate with specified or current provider"""
        if provider_name is None:
            provider_name = self.current_provider
        
        logger.info(f"🚀 Starting authentication for {provider_name}...")
        
        # Get authentication method
        auth_methods = {
            "google_drive": self.authenticate_google_drive,
            "dropbox": self.authenticate_dropbox,
            "s3": self.authenticate_s3,
            "local": self.authenticate_local
        }
        
        if provider_name not in auth_methods:
            logger.error(f"❌ No authentication method for provider: {provider_name}")
            return False
        
        # Run authentication
        return auth_methods[provider_name]()
    
    def test_provider_connection(self, provider_name: str = None) -> bool:
        """Test connection to storage provider"""
        if provider_name is None:
            provider_name = self.current_provider
        
        try:
            logger.info(f"🔍 Testing connection to {provider_name}...")
            
            # Get provider instance
            provider_config = get_storage_provider_config()
            provider = get_storage_provider(provider_name, provider_config)
            
            # Test connection
            if provider.test_connection():
                logger.info(f"✅ {provider_name} connection test successful!")
                return True
            else:
                logger.error(f"❌ {provider_name} connection test failed!")
                return False
                
        except Exception as e:
            logger.error(f"💥 Error testing {provider_name} connection: {str(e)}")
            return False
    
    def run_authentication_setup(self, provider_name: str = None) -> bool:
        """Run complete authentication setup"""
        if provider_name is None:
            provider_name = self.current_provider
        
        logger.info(f"🚀 Storage Authentication Setup for {provider_name}")
        logger.info("=" * 60)
        
        try:
            # Show provider requirements
            requirements = self.get_provider_requirements(provider_name)
            if requirements:
                logger.info(f"📋 {requirements['description']}")
                logger.info("Steps:")
                for step in requirements['steps']:
                    logger.info(f"   {step}")
            
            # Run authentication
            if self.authenticate_provider(provider_name):
                logger.info(f"✅ {provider_name} authentication completed successfully!")
                
                # Test connection
                if self.test_provider_connection(provider_name):
                    logger.info(f"🎉 {provider_name} is ready to use!")
                    return True
                else:
                    logger.warning(f"⚠️  {provider_name} authentication succeeded but connection test failed")
                    return False
            else:
                logger.error(f"❌ {provider_name} authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"💥 Authentication setup failed: {str(e)}")
            return False

def main():
    """Main function"""
    import sys
    
    # Get provider from command line argument
    provider_name = sys.argv[1] if len(sys.argv) > 1 else None
    
    try:
        authenticator = StorageAuthenticator()
        
        if provider_name:
            # Authenticate specific provider
            success = authenticator.run_authentication_setup(provider_name)
        else:
            # Show available providers
            providers = authenticator.list_available_providers()
            current = authenticator.current_provider
            
            print("🔐 BigSkyAg Storage Authentication")
            print("=" * 50)
            print(f"Current provider: {current}")
            print(f"Available providers: {', '.join(providers)}")
            print("\nTo authenticate a provider, run:")
            print(f"  python3 authenticate_storage.py <provider_name>")
            print("\nExample:")
            print(f"  python3 authenticate_storage.py {current}")
            
            return True
        
        return success
        
    except Exception as e:
        logger.error(f"💥 Critical error in authentication: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
