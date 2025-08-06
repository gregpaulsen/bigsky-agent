import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# === CONFIG ===
BACKUP_FOLDER = Path("/Volumes/BigSkySSD//07_Backups")
ROOT_FOLDER_ID = "1hJeN0e9ElQ617yrt_dsTq0o1CerUeQ15"
SUBFOLDER_NAME = "Backups"
CREDS_PATH = Path("/Volumes/BigSkySSD/05_Automation/Scripts/credentials.json")
TOKEN_PATH = Path("/Volumes/BigSkySSD/05_Automation/Scripts/token.json")

# === AUTH ===
creds = Credentials.from_authorized_user_file(TOKEN_PATH, ["https://www.googleapis.com/auth/drive.file"])
service = build("drive", "v3", credentials=creds)

# === FIND OR CREATE SUBFOLDER ===
def get_or_create_subfolder(service, parent_id, name):
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
        return folder["id"]

# Get or create the 'Backups' folder under main BigSkyAg Drive folder
folder_id = get_or_create_subfolder(service, ROOT_FOLDER_ID, SUBFOLDER_NAME)

# === FIND LATEST ZIP FILE ===
zips = list(BACKUP_FOLDER.glob("*.zip"))
print("🔍 Debug: Listing files in backup folder:")
for f in BACKUP_FOLDER.iterdir():
    print(" -", f.name)

if not zips:
    raise FileNotFoundError("❌ No zip files found in 07_Backups")

latest_zip = max(zips, key=os.path.getmtime)
print(f"📦 Uploading {latest_zip.name} to Google Drive → Backups folder...")

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

print(f"✅ Uploaded: https://drive.google.com/file/d/{uploaded['id']}")

print(f"📁 Scanning for zips in: {BACKUP_FOLDER}")
print("📄 Found:")
for z in BACKUP_FOLDER.glob("*.zip"):
    print(" -", z.name)

