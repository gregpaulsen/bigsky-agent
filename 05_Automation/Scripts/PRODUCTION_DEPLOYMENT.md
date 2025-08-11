# 🚀 Production Deployment Guide

## 📋 **Overview**

This guide covers deploying the BigSkyAg automation system to production for any company. The system is now **100% white-label ready** and supports multiple storage providers.

## 🎯 **Quick Start (5 minutes)**

### **1. Company Setup**
```bash
python3 setup_company.py
```
Follow the prompts to configure your company name and storage provider.

### **2. Storage Authentication**
```bash
python3 authenticate_storage.py <provider_name>
```
Replace `<provider_name>` with: `google_drive`, `dropbox`, `s3`, or `local`

### **3. Test System**
```bash
python3 system_health.py
```
Should show 117/117 tests passing.

### **4. Run Full System**
```bash
./launch_all.command
```

## 🔧 **Detailed Setup by Storage Provider**

### **Google Drive Setup**

1. **Get Credentials**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing
   - Enable Google Drive API
   - Create OAuth 2.0 credentials
   - Download `credentials.json`

2. **Place Credentials**
   ```bash
   # Copy credentials to Scripts folder
   cp ~/Downloads/credentials.json /path/to/Scripts/
   ```

3. **Authenticate**
   ```bash
   python3 authenticate_storage.py google_drive
   ```

### **Dropbox Setup**

1. **Get Access Token**
   - Go to [Dropbox App Console](https://www.dropbox.com/developers/apps)
   - Create new app
   - Generate access token

2. **Update Config**
   ```python
   # In config.py, update the dropbox section:
   "dropbox": {
       "access_token": "YOUR_ACTUAL_TOKEN_HERE"
   }
   ```

3. **Authenticate**
   ```bash
   python3 authenticate_storage.py dropbox
   ```

### **AWS S3 Setup**

1. **Create IAM User**
   - Create IAM user with S3 access
   - Generate access key and secret key

2. **Set Environment Variables**
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   ```

3. **Update Config**
   ```python
   # In config.py, update the s3 section:
   "s3": {
       "bucket_name": "your-bucket-name",
       "region_name": "us-west-2"
   }
   ```

4. **Authenticate**
   ```bash
   python3 authenticate_storage.py s3
   ```

### **Local Storage Setup**

1. **No Setup Required**
   ```bash
   python3 authenticate_storage.py local
   ```

## 🏢 **Company Configuration**

### **Basic Company Setup**
```python
# In config.py, update COMPANY_SETTINGS:
COMPANY_SETTINGS = {
    "company_name": "YourCompanyName",
    "storage_provider": "dropbox",  # or google_drive, s3, local
    "backup_prefix": "YourCompany_Backup",
    "use_archive_rotation": True,
    "max_working_backups": 1,
    "max_archive_backups": 4,
    "min_backup_size_gb": 3.0
}
```

### **Advanced Company Setup**
```python
# Use the setup_company function:
from config import setup_company

setup_company(
    company_name="EnterpriseCorp",
    storage_provider="s3",
    custom_settings={
        "max_working_backups": 3,
        "max_archive_backups": 12,
        "min_backup_size_gb": 5.0
    }
)
```

## 📁 **Folder Structure Customization**

### **Default Structure**
```
YourCompany/
├── 00_Admin/          # Administrative files
├── 01_Branding/       # Marketing materials
├── 02_Field_Projects/ # Project data
├── 03_Mapping_QGIS/   # GIS projects
├── 04_Training/       # Training materials
├── 05_Automation/     # Scripts and automation
├── 06_Business_Strategy/ # Business documents
├── YourCompanyDropZone/ # Incoming files
└── Z_Archive/         # Unknown file types
```

### **Custom Structure**
```python
# Modify CRITICAL_FOLDERS in config.py
CRITICAL_FOLDERS = {
    "custom_folder": BASE_DIR / "Custom_Folder",
    # ... other folders
}
```

## 🔄 **File Routing Customization**

### **Add New File Types**
```python
# In config.py, add to ROUTING_RULES:
ROUTING_RULES[".newtype"] = "destination_folder"
```

### **Custom Routing Logic**
```python
# Use smart_router.py for content-based routing
python3 smart_router.py
```

## 📦 **Backup Configuration**

### **Backup Types**
- **Daily**: Incremental backups (changed files only)
- **Weekly**: Full system backups
- **Monthly**: Full system backups with long-term retention

### **Customize Backup Settings**
```python
# In config.py, modify BACKUP_CONFIG:
BACKUP_CONFIG = {
    "max_working_backups": 2,      # Keep 2 current backups
    "max_archive_backups": 8,      # Keep 8 historical archives
    "min_size_gb": 5.0,           # Minimum expected size
    # ... other settings
}
```

## 🚀 **Production Deployment Checklist**

### **Pre-Deployment**
- [ ] Company name configured
- [ ] Storage provider selected and authenticated
- [ ] System health check passes (117/117 tests)
- [ ] Backup configuration verified
- [ ] File routing rules tested

### **Deployment**
- [ ] Run `setup_company.py` for company configuration
- [ ] Complete storage provider authentication
- [ ] Test file routing with sample files
- [ ] Verify backup creation and upload
- [ ] Test full system with `launch_all.command`

### **Post-Deployment**
- [ ] Monitor system logs
- [ ] Verify automated backups
- [ ] Test file routing with real files
- [ ] Document company-specific procedures

## 🔍 **Monitoring & Maintenance**

### **System Health Checks**
```bash
# Daily health check
python3 system_health.py

# Check storage provider status
python3 authenticate_storage.py <provider> --test
```

### **Log Monitoring**
- Check `router.log` for file routing issues
- Check `authenticate_storage.log` for storage issues
- Monitor backup creation and upload logs

### **Performance Optimization**
- Monitor backup creation time
- Check storage provider upload speeds
- Optimize file routing rules if needed

## 🆘 **Troubleshooting**

### **Common Issues**

1. **Storage Authentication Fails**
   - Check credentials/tokens are valid
   - Verify internet connection
   - Check storage provider status

2. **File Routing Issues**
   - Verify file extensions are supported
   - Check destination folders exist
   - Review routing rules in config.py

3. **Backup Failures**
   - Check available disk space
   - Verify storage provider access
   - Check backup configuration

### **Getting Help**
1. Run `python3 system_health.py`
2. Check script logs for error details
3. Verify configuration settings
4. Test individual components

## 🎉 **Success Indicators**

Your system is production-ready when:
- ✅ System health: 117/117 tests passing
- ✅ Storage provider authenticated and tested
- ✅ File routing working with sample files
- ✅ Backup creation and upload successful
- ✅ Full system runs without errors
- ✅ Company branding properly configured

## 🚀 **Next Steps**

After successful deployment:
1. **Automate**: Set up cron jobs or scheduled tasks
2. **Monitor**: Implement log monitoring and alerts
3. **Scale**: Add more storage providers or customize routing
4. **Integrate**: Connect with other business systems

---

**🎯 You now have a production-ready, white-label automation system that can work for any company with any storage provider!**
