"""
BigSkyAg Google Drive Backup Uploader
Uploads the latest backup zip to Google Drive
"""

import os
import logging
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import (
    ensure_critical_folders, 
    get_folder_path, 
    GOOGLE_DRIVE_CONFIG
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_or_create_subfolder(service, parent_id, name):
    """Get or create a subfolder in Google Drive"""
    query = f"name='{name}' and '{parent_id}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get("files", [])
    
    if items:
        return items[0]["id"]
    else:
        metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id]
        }
        folder = service.files().create(body=metadata, fields="id").execute()
        logger.info(f"Created new folder: {name}")
        return folder["id"]

def upload_latest_backup():
    """Upload the latest backup zip to Google Drive"""
    
    # Ensure all critical folders exist
    ensure_critical_folders()
    
    # Get paths from config
    backup_folder = get_folder_path("backups")
    scripts_folder = get_folder_path("scripts")
    
    # Google Drive credentials and token paths
    creds_path = scripts_folder / GOOGLE_DRIVE_CONFIG["credentials_file"]
    token_path = scripts_folder / GOOGLE_DRIVE_CONFIG["token_file"]
    
    # Check if credentials exist
    if not creds_path.exists():
        logger.error(f"❌ Credentials file not found: {creds_path}")
        logger.error("Please run authenticate_drive.py first to set up Google Drive access")
        return False
    
    if not token_path.exists():
        logger.error(f"❌ Token file not found: {token_path}")
        logger.error("Please run authenticate_drive.py first to authenticate with Google Drive")
        return False
    
    try:
        # Load credentials
        creds = Credentials.from_authorized_user_file(
            token_path, 
            ["https://www.googleapis.com/auth/drive.file"]
        )
        service = build("drive", "v3", credentials=creds)
        
    except Exception as e:
        logger.error(f"❌ Failed to authenticate with Google Drive: {str(e)}")
        return False
    
    # Get or create the 'Backups' folder under main BigSkyAg Drive folder
    try:
        folder_id = get_or_create_subfolder(
            service, 
            GOOGLE_DRIVE_CONFIG["root_folder_id"], 
            GOOGLE_DRIVE_CONFIG["backups_subfolder"]
        )
    except Exception as e:
        logger.error(f"❌ Failed to get/create Google Drive folder: {str(e)}")
        return False
    
    # Find the latest zip file
    zips = list(backup_folder.glob("*.zip"))
    
    if not zips:
        logger.error("❌ No zip files found in backup folder")
        return False
    
    latest_zip = max(zips, key=os.path.getmtime)
    print(f"📦 Uploading {latest_zip.name} to Google Drive → Backups folder...")
    
    try:
        # Upload the file
        media = MediaFileUpload(latest_zip, mimetype='application/zip')
        file_metadata = {
            "name": latest_zip.name,
            "parents": [folder_id]
        }
        
        uploaded = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()
        
        print(f"✅ Uploaded successfully!")
        print(f"🔗 File URL: https://drive.google.com/file/d/{uploaded['id']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Upload failed: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 Starting Google Drive backup upload...")
    
    success = upload_latest_backup()
    
    if success:
        print("✅ Google Drive backup upload completed successfully")
    else:
        print("❌ Google Drive backup upload failed")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

