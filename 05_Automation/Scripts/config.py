"""
BigSkyAg Automation Configuration
Storage-agnostic, company-agnostic configuration for all automation scripts
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

# === COMPANY CONFIGURATION ===
# Change these values to deploy for any company
COMPANY_SETTINGS = {
    "company_name": "BigSkyAg",  # Change this to your company name
    "storage_provider": "google_drive",  # google_drive, dropbox, s3, local
    "backup_prefix": "BigSkyAg_Backup",  # Will auto-generate based on company name
    "use_archive_rotation": True,
    "max_working_backups": 1,
    "max_archive_backups": 4,
    "min_backup_size_gb": 3.0
}

# === BASE PATHS ===
# Primary working directory (can be overridden by environment variable)
DEFAULT_BASE = Path("/Volumes/BigSkyAgSSD/BigSkyAg")
BASE_DIR = Path(os.environ.get("BIGSKY_BASE", DEFAULT_BASE))

# Desktop source directory (for sync operations)
DESKTOP_SOURCE = Path("/Users/gregpaulsen/Desktop/BigSkyAg")

# === STORAGE CONFIGURATION ===
# Storage-agnostic configuration for different providers
STORAGE_CONFIG = {
    "provider": COMPANY_SETTINGS["storage_provider"],
    
    # Company branding (auto-generated from COMPANY_SETTINGS)
    "company_name": COMPANY_SETTINGS["company_name"],
    "backup_prefix": COMPANY_SETTINGS["backup_prefix"],
    
    # Provider-specific configurations
    "providers": {
        "google_drive": {
            "credentials_path": BASE_DIR / "05_Automation" / "Scripts" / "credentials.json",
            "token_path": BASE_DIR / "05_Automation" / "Scripts" / "token.json",
            "backup_folder_id": "1hJeN0e9ElQ617yrt_dsTq0o1CerUeQ15"
        },
        "dropbox": {
            "access_token": "YOUR_DROPBOX_ACCESS_TOKEN_HERE"
        },
        "s3": {
            "bucket_name": "YOUR_S3_BUCKET_NAME",
            "region_name": "us-west-2"
        },
        "local": {
            "storage_path": BASE_DIR / "00_Admin" / "Local_Backups"
        }
    }
}

# Company-specific dynamic names
COMPANY_DROPZONE_NAME = f"{STORAGE_CONFIG['company_name']}DropZone"

# === CRITICAL FOLDERS ===
# These folders will be created automatically if they don't exist
CRITICAL_FOLDERS = {
    "backups": BASE_DIR / "00_Admin" / "Backups",
    "dropzone": BASE_DIR / COMPANY_DROPZONE_NAME,
    "archive": BASE_DIR / "Z_Archive",
    "scripts": BASE_DIR / "05_Automation" / "Scripts",
    "admin": BASE_DIR / "00_Admin",
    "branding": BASE_DIR / "01_Branding",
    "field_projects": BASE_DIR / "02_Field_Projects",
    "mapping": BASE_DIR / "03_Mapping_QGIS",
    "training": BASE_DIR / "04_Training",
    "automation": BASE_DIR / "05_Automation",
    "business": BASE_DIR / "06_Business_Strategy"
}

# === FILE ROUTING RULES ===
# Maps file extensions to destination folders
ROUTING_RULES = {
    # Administrative documents
    ".pdf": "admin",
    ".docx": "admin", 
    ".doc": "admin",
    ".xlsx": "admin",
    ".xls": "admin",
    ".csv": "admin",
    ".txt": "admin",
    ".rtf": "admin",
    ".odt": "admin",
    ".ods": "admin",
    
    # Branding and marketing materials
    ".png": "branding",
    ".jpg": "branding",
    ".jpeg": "branding",
    ".gif": "branding",
    ".bmp": "branding",
    ".tiff": "branding",
    ".svg": "branding",
    ".ai": "branding",
    ".psd": "branding",
    ".eps": "branding",
    
    # Field projects and GIS data
    ".tif": "field_projects",
    ".shp": "field_projects",
    ".dbf": "field_projects",
    ".prj": "field_projects",
    ".shx": "field_projects",
    ".cpg": "field_projects",
    ".geojson": "field_projects",
    ".kml": "field_projects",
    ".kmz": "field_projects",
    ".las": "field_projects",
    ".laz": "field_projects",
    ".dem": "field_projects",
    ".asc": "field_projects",
    ".img": "field_projects",
    ".ecw": "field_projects",
    ".sid": "field_projects",
    
    # QGIS and mapping projects
    ".gpkg": "mapping",
    ".qgz": "mapping",
    ".qgs": "mapping",
    ".qgd": "mapping",
    ".sqlite": "mapping",
    ".db": "mapping",
    
    # Training materials
    ".mp4": "training",
    ".avi": "training",
    ".mov": "training",
    ".wmv": "training",
    ".flv": "training",
    ".webm": "training",
    ".mp3": "training",
    ".wav": "training",
    ".aac": "training",
    ".flac": "training",
    
    # Scripts and automation
    ".py": "scripts",
    ".sh": "scripts",
    ".command": "scripts",
    ".bat": "scripts",
    ".ps1": "scripts",
    ".js": "scripts",
    ".html": "scripts",
    ".css": "scripts",
    ".json": "scripts",
    ".xml": "scripts",
    ".yaml": "scripts",
    ".yml": "scripts",
    
    # Backups and archives
    ".zip": "backups",
    ".tar": "backups",
    ".gz": "backups",
    ".7z": "backups",
    ".rar": "backups",
    ".iso": "backups",
    
    # Business strategy documents
    ".pptx": "business",
    ".ppt": "business",
    ".key": "business",
    ".odp": "business",
    ".md": "business",
    ".markdown": "business"
}

# === BACKUP CONFIG ===
# New hybrid backup strategy
BACKUP_CONFIG = {
    "max_working_backups": COMPANY_SETTINGS["max_working_backups"],
    "max_archive_backups": COMPANY_SETTINGS["max_archive_backups"],
    "min_size_gb": COMPANY_SETTINGS["min_backup_size_gb"],
    "exclude_patterns": [
        "*.DS_Store", 
        "__MACOSX/*", 
        "*.tmp",
        "00_Admin/Backups/*",      # Exclude backup folder from backups
        "00_Admin/Local_Backups/*", # Exclude local backups
        f"{COMPANY_DROPZONE_NAME}/*", # Exclude dropzone from backups
        "*.log"                    # Exclude log files
    ],
    "backup_types": {
        "daily": {
            "type": "incremental",  # Only changed files
            "retention": 7,         # Keep 7 days
            "upload": True          # Upload to cloud storage
        },
        "weekly": {
            "type": "full",         # Complete system backup
            "retention": 4,         # Keep 4 weeks
            "upload": True          # Upload to cloud storage
        },
        "monthly": {
            "type": "full",         # Complete system backup
            "retention": 12,        # Keep 12 months
            "upload": True          # Upload to cloud storage
        }
    }
}

# === COMPANY CONFIGURATIONS ===
# Template configurations for different companies
COMPANY_TEMPLATES = {
    "BigSkyAg": {
        "storage_provider": "google_drive",
        "company_name": "BigSkyAg",
        "backup_prefix": "BigSkyAg_Backup",
        "description": "Agricultural automation and data management"
    },
    "PaulysOps": {
        "storage_provider": "dropbox",
        "company_name": "PaulysOps", 
        "backup_prefix": "PaulysOps_Backup",
        "description": "Operations automation and workflow management"
    },
    "GenericCorp": {
        "storage_provider": "s3",
        "company_name": "GenericCorp",
        "backup_prefix": "GenericCorp_Backup", 
        "description": "Enterprise automation and data management"
    }
}

def ensure_critical_folders():
    """Create all critical folders if they don't exist"""
    print("🔧 Ensuring critical folders exist...")
    
    for folder_name, folder_path in CRITICAL_FOLDERS.items():
        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created: {folder_path}")
        else:
            print(f"✅ Exists: {folder_path}")
    
    # Ensure backup archive subfolder exists
    archive_sub = CRITICAL_FOLDERS["backups"] / "Archive"
    archive_sub.mkdir(parents=True, exist_ok=True)
    print(f"✅ Ensured: {archive_sub}")
    
    print("✅ All critical folders verified")

def get_folder_path(folder_key):
    """Get the path for a specific folder by key"""
    if folder_key not in CRITICAL_FOLDERS:
        raise ValueError(f"Unknown folder key: {folder_key}")
    return CRITICAL_FOLDERS[folder_key]

def get_routing_destination(file_extension):
    """Get the destination folder for a file extension"""
    folder_key = ROUTING_RULES.get(file_extension.lower())
    if folder_key:
        return get_folder_path(folder_key)
    return None

def get_storage_provider_config():
    """Get configuration for the current storage provider"""
    provider_name = STORAGE_CONFIG["provider"]
    if provider_name not in STORAGE_CONFIG["providers"]:
        raise ValueError(f"Unknown storage provider: {provider_name}")
    
    # Merge base config with provider config
    config = STORAGE_CONFIG.copy()
    config.update(STORAGE_CONFIG["providers"][provider_name])
    return config

def get_company_config(company_name: str = None):
    """Get configuration for a specific company"""
    if company_name is None:
        company_name = STORAGE_CONFIG["company_name"]
    
    if company_name not in COMPANY_TEMPLATES:
        raise ValueError(f"Unknown company: {company_name}")
    
    return COMPANY_TEMPLATES[company_name]

def setup_company(company_name: str, storage_provider: str, custom_settings: Dict[str, Any] = None):
    """Setup configuration for a new company"""
    if custom_settings is None:
        custom_settings = {}
    
    # Update company settings
    COMPANY_SETTINGS["company_name"] = company_name
    COMPANY_SETTINGS["storage_provider"] = storage_provider
    
    # Auto-generate backup prefix if not provided
    if "backup_prefix" not in custom_settings:
        COMPANY_SETTINGS["backup_prefix"] = f"{company_name}_Backup"
    
    # Update other custom settings
    for key, value in custom_settings.items():
        if key in COMPANY_SETTINGS:
            COMPANY_SETTINGS[key] = value
    
    # Update storage config
    STORAGE_CONFIG["provider"] = storage_provider
    STORAGE_CONFIG["company_name"] = company_name
    STORAGE_CONFIG["backup_prefix"] = COMPANY_SETTINGS["backup_prefix"]
    
    # Update company dropzone name
    global COMPANY_DROPZONE_NAME
    COMPANY_DROPZONE_NAME = f"{company_name}DropZone"
    
    # Update critical folders
    CRITICAL_FOLDERS["dropzone"] = BASE_DIR / COMPANY_DROPZONE_NAME
    
    print(f"✅ Company setup complete: {company_name}")
    print(f"   Storage Provider: {storage_provider}")
    print(f"   Backup Prefix: {COMPANY_SETTINGS['backup_prefix']}")
    print(f"   DropZone: {COMPANY_DROPZONE_NAME}")

def get_system_info():
    """Get comprehensive system information"""
    return {
        "company_name": COMPANY_SETTINGS["company_name"],
        "storage_provider": STORAGE_CONFIG["provider"],
        "backup_prefix": STORAGE_CONFIG["backup_prefix"],
        "base_directory": str(BASE_DIR),
        "desktop_source": str(DESKTOP_SOURCE),
        "dropzone_name": COMPANY_DROPZONE_NAME,
        "critical_folders": {k: str(v) for k, v in CRITICAL_FOLDERS.items()},
        "routing_rules_count": len(ROUTING_RULES),
        "backup_config": BACKUP_CONFIG
    }

if __name__ == "__main__":
    # Test the configuration
    print(f"🏠 Base directory: {BASE_DIR}")
    print(f"💻 Desktop source: {DESKTOP_SOURCE}")
    print(f"☁️  Storage provider: {STORAGE_CONFIG['provider']}")
    print(f"🏢 Company: {STORAGE_CONFIG['company_name']}")
    print(f"📦 Backup prefix: {STORAGE_CONFIG['backup_prefix']}")
    print(f"🔄 DropZone: {COMPANY_DROPZONE_NAME}")
    
    # Show system info
    print("\n📊 System Information:")
    info = get_system_info()
    for key, value in info.items():
        if key != "critical_folders":
            print(f"   {key}: {value}")
    
    ensure_critical_folders()
