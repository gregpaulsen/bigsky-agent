import shutil
from pathlib import Path

DROPZONE = Path("/Volumes/BigSkySSD/BigSkyAg/BigSkyAgDropZone")
DEST_BASE = Path("/Volumes/BigSkySSD/BigSkyAg")

routes = {
    ".pdf": "01_Admin",
    ".docx": "01_Admin",
    ".xlsx": "01_Admin",
    ".png": "02_Branding",
    ".jpg": "02_Branding",
    ".tif": "04_Data",
    ".zip": "07_Backups",
    ".py": "05_Automation/Scripts",
    ".sh": "05_Automation/Scripts",
    ".command": "05_Automation/Scripts"
}

print("📂 Routing files from DropZone...")

for file in DROPZONE.glob("*"):
    ext = file.suffix.lower()
    dest_folder = routes.get(ext)
    if dest_folder:
        dest_path = DEST_BASE / dest_folder / file.name
        print(f"🔁 Moving {file.name} → {dest_folder}")
        shutil.move(str(file), str(dest_path))

print("✅ Routing complete.")

