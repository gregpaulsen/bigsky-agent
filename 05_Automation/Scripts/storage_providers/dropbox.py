"""
Dropbox Storage Provider
Implements Dropbox storage functionality for PaulysOps
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any

from .base_provider import StorageProvider

class DropboxProvider(StorageProvider):
    """Dropbox storage provider implementation"""
    
    def _validate_config(self) -> bool:
        """Validate Dropbox configuration"""
        required_keys = ['access_token']
        
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")
        
        return True
    
    def _initialize_provider(self) -> bool:
        """Initialize Dropbox client"""
        try:
            # Try to import Dropbox module
            try:
                import dropbox
                from dropbox.exceptions import ApiError, AuthError
            except ImportError:
                raise ImportError("Dropbox module not installed. Run: pip install dropbox")
            
            # Create Dropbox client
            self.client = dropbox.Dropbox(self.config['access_token'])
            
            # Test connection
            self.client.users_get_current_account()
            
            # Set authentication status
            self._authenticated = True
            
            return True
            
        except Exception as e:
            self._authenticated = False
            raise Exception(f"Failed to initialize Dropbox: {str(e)}")
    
    def authenticate(self) -> bool:
        """Authenticate with Dropbox"""
        try:
            # Test authentication by getting account info
            self.client.users_get_current_account()
            self._authenticated = True
            return True
        except Exception as e:
            self._authenticated = False
            raise Exception(f"Dropbox authentication failed: {str(e)}")
    
    def upload_file(self, file_path: Path, destination: str) -> Optional[str]:
        """Upload file to Dropbox"""
        try:
            if not self._authenticated:
                if not self.authenticate():
                    return None
            
            # Ensure destination folder exists
            self._ensure_folder_exists(destination)
            
            # Upload file
            dropbox_path = f"/{destination}/{file_path.name}"
            
            with open(file_path, 'rb') as f:
                metadata = self.client.files_upload(
                    f.read(),
                    dropbox_path,
                    mode=dropbox.files.WriteMode.overwrite
                )
            
            return metadata.id
            
        except Exception as e:
            raise Exception(f"Dropbox upload failed: {str(e)}")
    
    def download_file(self, file_id: str, local_path: Path) -> bool:
        """Download file from Dropbox"""
        try:
            # Get file metadata
            metadata = self.client.files_get_metadata(file_id)
            
            # Download file content
            with open(local_path, 'wb') as f:
                metadata, response = self.client.files_download(metadata.path_display)
                f.write(response.content)
            
            return True
            
        except Exception as e:
            raise Exception(f"Dropbox download failed: {str(e)}")
    
    def list_files(self, folder_path: str = "") -> List[Dict[str, Any]]:
        """List files in Dropbox folder"""
        try:
            if folder_path == "":
                dropbox_path = ""
            else:
                dropbox_path = f"/{folder_path}"
            
            try:
                result = self.client.files_list_folder(dropbox_path)
            except Exception as e:
                if "not_found" in str(e).lower():
                    return []
                raise
            
            files = []
            for entry in result.entries:
                if hasattr(entry, 'id'):  # File or folder
                    files.append({
                        'id': entry.id,
                        'name': entry.name,
                        'size': getattr(entry, 'size', 0),
                        'modified_time': getattr(entry, 'server_modified', 0),
                        'url': self._get_shared_link(entry.path_display),
                        'type': 'file'
                    })
            
            return files
            
        except Exception as e:
            raise Exception(f"Dropbox list files failed: {str(e)}")
    
    def delete_file(self, file_id: str) -> bool:
        """Delete file from Dropbox"""
        try:
            # Get file metadata to get path
            metadata = self.client.files_get_metadata(file_id)
            self.client.files_delete_v2(metadata.path_display)
            return True
        except Exception as e:
            raise Exception(f"Dropbox delete failed: {str(e)}")
    
    def create_folder(self, folder_path: str) -> Optional[str]:
        """Create folder in Dropbox"""
        try:
            dropbox_path = f"/{folder_path}"
            
            # Create folder
            self.client.files_create_folder_v2(dropbox_path)
            
            # Get folder metadata
            metadata = self.client.files_get_metadata(dropbox_path)
            return metadata.id
            
        except Exception as e:
            raise Exception(f"Dropbox create folder failed: {str(e)}")
    
    def _ensure_folder_exists(self, folder_path: str):
        """Ensure folder exists, create if it doesn't"""
        if not folder_path:
            return
        
        path_parts = folder_path.strip('/').split('/')
        current_path = ""
        
        for part in path_parts:
            current_path = f"{current_path}/{part}" if current_path else part
            
            try:
                # Try to get folder metadata
                self.client.files_get_metadata(f"/{current_path}")
            except Exception as e:
                if "not_found" in str(e).lower():
                    # Folder doesn't exist, create it
                    self.client.files_create_folder_v2(f"/{current_path}")
                else:
                    raise
    
    def _get_shared_link(self, path: str) -> str:
        """Get shared link for file"""
        try:
            shared_link = self.client.sharing_create_shared_link(path)
            return shared_link.url
        except:
            return ""
