"""
BigSkyAg Google Drive Authentication
Sets up OAuth2 authentication for Google Drive API access
"""

import logging
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from config import ensure_critical_folders, get_folder_path, GOOGLE_DRIVE_CONFIG

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def authenticate_google_drive():
    """Authenticate with Google Drive and save credentials"""
    
    # Ensure all critical folders exist
    ensure_critical_folders()
    
    # Get scripts folder path
    scripts_folder = get_folder_path("scripts")
    
    # Paths for credentials and token
    creds_file = scripts_folder / GOOGLE_DRIVE_CONFIG["credentials_file"]
    token_file = scripts_folder / GOOGLE_DRIVE_CONFIG["token_file"]
    
    # Check if credentials file exists
    if not creds_file.exists():
        logger.error(f"❌ Credentials file not found: {creds_file}")
        logger.error("Please download credentials.json from Google Cloud Console and place it in the Scripts folder")
        return False
    
    print("🔐 Starting Google Drive authentication...")
    print(f"📁 Using credentials file: {creds_file}")
    
    try:
        # OAuth2 flow
        flow = InstalledAppFlow.from_client_secrets_file(
            str(creds_file), 
            [GOOGLE_DRIVE_CONFIG["scopes"]]
        )
        
        # Run local server for authentication
        print("🌐 Opening browser for authentication...")
        creds = flow.run_local_server(port=0)
        
        # Save the credentials for future use
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
        
        print(f"✅ Google Drive authentication complete!")
        print(f"💾 Token saved as: {token_file}")
        print("🔒 You can now use upload_backup_to_drive.py")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Authentication failed: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 BigSkyAg Google Drive Authentication Setup")
    print("=" * 50)
    
    success = authenticate_google_drive()
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("💡 Next steps:")
        print("   1. Test with upload_backup_to_drive.py")
        print("   2. Add upload_backup_to_drive.py to your automation workflow")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

