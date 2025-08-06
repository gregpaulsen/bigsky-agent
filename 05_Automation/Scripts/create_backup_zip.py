import os
import subprocess
import time

SOURCE_FOLDER = "/Volumes/BigSkySSD/BigSkyAg"
BACKUP_FOLDER = os.path.join(SOURCE_FOLDER, "07_Backups")
DATE = time.strftime("%Y-%m-%d")
ZIP_NAME = f"BigSkyAg_Backup_{DATE}.zip"
ZIP_PATH = os.path.join(BACKUP_FOLDER, ZIP_NAME)

def create_zip(source, dest):
    print(f"🌀 Creating backup zip...\n")
    result = subprocess.run([
        "zip", "-r", dest, ".", 
        "-x", "*.DS_Store", "__MACOSX/*"
    ], cwd=source)
    return result.returncode == 0

def check_size(path):
    size_bytes = os.path.getsize(path)
    size_gb = round(size_bytes / (1024**3), 2)
    print(f"🗜️ Zip file size: {size_gb} GB")
    return size_gb

def main():
    if not os.path.exists(SOURCE_FOLDER):
        print(f"❌ Source folder does not exist: {SOURCE_FOLDER}")
        return
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)
        print(f"📁 Created backup folder: {BACKUP_FOLDER}")

    start_time = time.time()
    success = create_zip(SOURCE_FOLDER, ZIP_PATH)
    duration = round(time.time() - start_time, 2)

    if success:
        size_gb = check_size(ZIP_PATH)
        if size_gb < 3.0:
            print("⚠️ WARNING: Zip size is too small. Likely incomplete!")
        else:
            print(f"✅ Backup completed in {duration} seconds")
    else:
        print("❌ Zip creation failed.")

if __name__ == "__main__":
    main()

