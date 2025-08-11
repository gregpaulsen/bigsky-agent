# Legacy Scripts Archive

This folder contains scripts that were part of the old BigSkyAg system before the storage-agnostic, white-label refactor.

## 📁 **Scripts Moved Here**

### **authenticate_drive.py**
- **Why moved**: Replaced by `authenticate_storage.py` which supports multiple storage providers
- **Old functionality**: Google Drive only authentication
- **New equivalent**: `authenticate_storage.py google_drive`

### **upload_backup_to_drive.py**
- **Why moved**: Replaced by `upload_backup.py` which is storage-agnostic
- **Old functionality**: Google Drive only backup uploads
- **New equivalent**: `upload_backup.py` (works with any storage provider)

## 🔄 **Migration Guide**

If you were using these old scripts, here's how to update:

### **Before (Old Way)**
```bash
python3 authenticate_drive.py
python3 upload_backup_to_drive.py
```

### **After (New Way)**
```bash
python3 authenticate_storage.py google_drive
python3 upload_backup.py daily
```

## 📋 **What Changed**

1. **Storage Agnostic**: New system works with Google Drive, Dropbox, S3, or local storage
2. **Company Agnostic**: Easy to deploy for any company, not just BigSkyAg
3. **Unified Interface**: All storage operations use the same commands
4. **Better Error Handling**: More robust error handling and logging
5. **Configuration Driven**: Easy to change settings without editing code

## 🚨 **Do Not Use These Scripts**

These scripts are **deprecated** and may not work with the current system. They reference old configuration variables and hardcoded paths that no longer exist.

## 💡 **Need Help?**

If you need to restore functionality from these scripts, check the main documentation or use the new unified commands.
