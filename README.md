# BigSkyAg Automation System

A **storage-agnostic, white-label automation system** for agricultural operations, including file routing, backup management, SSD synchronization, and cloud storage integration.

## 🚀 **NEW: STORAGE-AGNOSTIC & WHITE-LABEL READY!**

This system now supports **multiple storage providers** and can be **white-labeled for any company**:

- **BigSkyAg** → Google Drive
- **PaulysOps** → Dropbox  
- **Any Company** → AWS S3, OneDrive, Local Storage, etc.

## 🌟 **Key Features**

- **🔌 Storage Agnostic**: Works with Google Drive, Dropbox, AWS S3, OneDrive, or local storage
- **🏷️ White-Label Ready**: Easy rebranding for any company or use case
- **📁 Smart File Router**: Automatically routes files based on type and extension
- **💾 Hybrid Backup System**: Daily incremental + weekly full backups
- **🔄 SSD Sync**: Mirrors Desktop folder to SSD for performance and backup
- **☁️ Cloud Integration**: Automatic uploads to any configured storage provider
- **🏥 System Health Monitoring**: Comprehensive health checks for all components

## 📁 **System Architecture**

```
BigSkyAg/
├── 00_Admin/Backups/          # Current working backup (1 file)
│   └── Archive/               # Historical archives (4 files)
├── BigSkyAgDropZone/          # Incoming files for routing
├── 05_Automation/Scripts/     # All automation scripts
│   ├── storage_providers/     # Storage abstraction layer
│   │   ├── base_provider.py   # Abstract base class
│   │   ├── google_drive.py    # Google Drive implementation
│   │   ├── dropbox.py         # Dropbox implementation
│   │   ├── s3.py              # AWS S3 implementation
│   │   └── local.py           # Local storage implementation
│   ├── config.py              # Storage-agnostic configuration
│   ├── router.py              # File routing engine
│   ├── create_backup_zip.py   # Backup creation
│   ├── upload_backup.py       # Storage-agnostic upload
│   ├── authenticate_storage.py # Generic authentication
│   ├── system_health.py       # System health checks
│   └── launch_all.command     # Master launcher script
└── Z_Archive/                 # Archive for unknown file types
```

## 🛠️ **Setup Instructions**

### **Prerequisites**

1. **Python 3.7+** installed
2. **SSD mounted** at `/Volumes/BigSkyAgSSD`
3. **Storage provider** configured (Google Drive, Dropbox, S3, etc.)

### **1. Install Dependencies**

```bash
cd 05_Automation/Scripts
pip install -r requirements.txt
```

### **2. Configure Storage Provider**

**For BigSkyAg (Google Drive):**
```bash
python3 authenticate_storage.py google_drive
```

**For PaulysOps (Dropbox):**
```bash
python3 authenticate_storage.py dropbox
```

**For Enterprise (AWS S3):**
```bash
python3 authenticate_storage.py s3
```

### **3. Verify System Health**

```bash
python3 system_health.py
```

## 📋 **Usage**

### **Quick Start**

Run the complete system:
```bash
./launch_all.command
```

### **Individual Operations**

**File Routing:**
```bash
python3 router.py
```

**Create Backup:**
```bash
python3 create_backup_zip.py
```

**Upload to Cloud Storage:**
```bash
python3 upload_backup.py daily    # Daily incremental
python3 upload_backup.py weekly   # Weekly full backup
python3 upload_backup.py monthly  # Monthly full backup
```

**System Health Check:**
```bash
python3 system_health.py
```

**Storage Authentication:**
```bash
python3 authenticate_storage.py <provider_name>
```

## ⚙️ **Configuration**

### **Storage Provider Selection**

Edit `config.py` to change storage provider:

```python
STORAGE_CONFIG = {
    "provider": "google_drive",  # google_drive, dropbox, s3, local
    "company_name": "BigSkyAg",
    "backup_prefix": "BigSkyAg_Backup"
}
```

### **Company Branding**

```python
COMPANY_TEMPLATES = {
    "BigSkyAg": {
        "storage_provider": "google_drive",
        "company_name": "BigSkyAg",
        "backup_prefix": "BigSkyAg_Backup"
    },
    "PaulysOps": {
        "storage_provider": "dropbox",
        "company_name": "PaulysOps",
        "backup_prefix": "PaulysOps_Backup"
    }
}
```

### **Environment Variables**

Override the base directory:
```bash
export BIGSKY_BASE="/path/to/your/bigsky/folder"
```

## 🔄 **Backup Strategy**

### **Hybrid Backup System**

- **Daily**: Incremental backups (only changed files)
- **Weekly**: Full system backups
- **Monthly**: Full system backups with long-term retention

### **Storage Pattern**

```
00_Admin/Backups/
├── BigSkyAg_Current_2025-01-15.zip    # Tonight's backup
└── Archive/
    ├── BigSkyAg_2025-01-14.zip        # Last 4 nights
    ├── BigSkyAg_2025-01-13.zip
    ├── BigSkyAg_2025-01-12.zip
    └── BigSkyAg_2025-01-11.zip
```

### **Smart Upload**

- **Only uploads if changes exist**
- **Automatic cleanup of old backups**
- **Provider-agnostic storage**

## 📊 **File Routing Rules**

The router automatically categorizes files based on their extensions:

| File Type | Destination | Examples |
|-----------|-------------|----------|
| **Administrative** | `00_Admin/` | PDF, DOCX, XLSX, CSV, TXT, RTF |
| **Branding** | `01_Branding/` | PNG, JPG, SVG, AI, PSD, EPS |
| **Field Projects** | `02_Field_Projects/` | TIF, SHP, DBF, KML, LAS, DEM |
| **QGIS/Mapping** | `03_Mapping_QGIS/` | GPKG, QGZ, QGS, SQLITE |
| **Training** | `04_Training/` | MP4, AVI, MOV, MP3, WAV |
| **Scripts** | `05_Automation/Scripts/` | PY, SH, JS, HTML, JSON, YAML |
| **Backups** | `00_Admin/Backups/` | ZIP, TAR, 7Z, RAR, ISO |
| **Business Strategy** | `06_Business_Strategy/` | PPTX, PPT, KEY, MD |
| **Unknown** | `Z_Archive/` | Any unrecognized file types |

### **Advanced Routing Features**

- **Duplicate Detection**: Uses MD5 hashing to identify and remove duplicate files
- **Collision Prevention**: Automatically generates unique filenames for conflicts
- **Content Validation**: Ensures files are readable and non-empty before routing
- **Comprehensive Logging**: Detailed logs with both console and file output
- **Error Recovery**: Continues processing even if individual files fail
- **System File Filtering**: Automatically excludes hidden and system files

## 🏷️ **White-Label Deployment**

### **For BigSkyAg (Google Drive)**
```python
STORAGE_CONFIG = {
    "provider": "google_drive",
    "company_name": "BigSkyAg",
    "backup_prefix": "BigSkyAg_Backup"
}
```

### **For PaulysOps (Dropbox)**
```python
STORAGE_CONFIG = {
    "provider": "dropbox",
    "company_name": "PaulysOps", 
    "backup_prefix": "PaulysOps_Backup"
}
```

### **For Enterprise (AWS S3)**
```python
STORAGE_CONFIG = {
    "provider": "s3",
    "company_name": "EnterpriseCorp",
    "backup_prefix": "EnterpriseCorp_Backup"
}
```

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Storage Provider Not Working**
   - Run `python3 authenticate_storage.py <provider>`
   - Check credentials and tokens
   - Verify internet connection

2. **Missing Dependencies**
   - Run `pip install -r requirements.txt`
   - Check Python version (3.7+ required)

3. **Permission Errors**
   - Ensure write access to all folders
   - Check file ownership and permissions

### **Health Check**

Always run the health check first:
```bash
python3 system_health.py
```

This will identify and help resolve most common issues.

## 🚀 **What's Next**

### **Phase 1: Core Infrastructure ✅**
- ✅ Storage provider abstraction
- ✅ Configuration templates
- ✅ Provider-agnostic backup system
- ✅ Authentication framework

### **Phase 2: Provider Implementation ✅**
- ✅ Google Drive (BigSkyAg)
- ✅ Dropbox (PaulysOps)
- ✅ AWS S3 (Enterprise)
- ✅ Local storage (Testing)

### **Phase 3: White-Label Framework 🚧**
- 🚧 Company branding system
- 🚧 Configuration templates
- 🚧 Deployment scripts
- 🚧 Documentation

### **Phase 4: Market Ready 📋**
- 📋 PaulysOps GitHub repo
- 📋 White-label documentation
- 📋 Deployment guides
- 📋 Support framework

## 🤝 **Contributing**

When modifying scripts:
1. Update `config.py` for new paths/settings
2. Add proper error handling and logging
3. Test with `system_health.py`
4. Update this README if needed
5. Ensure storage provider compatibility

## 📞 **Support**

For issues or questions:
1. Run `system_health.py` first
2. Check the troubleshooting section above
3. Review script logs and error messages
4. Ensure all prerequisites are met

---

**BigSkyAg Automation System** - **Storage-agnostic, white-label ready automation for any company, any storage provider, any use case.**
