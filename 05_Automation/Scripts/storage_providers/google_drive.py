"""
Google Drive Storage Provider
Implements Google Drive storage functionality
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any

from .base_provider import StorageProvider

class GoogleDriveProvider(StorageProvider):
    """Google Drive storage provider implementation"""
    
    def _validate_config(self) -> bool:
        """Validate Google Drive configuration"""
        required_keys = ['credentials_path', 'token_path']
        
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")
        
        # Check if credential files exist
        creds_path = Path(self.config['credentials_path'])
        token_path = Path(self.config['token_path'])
        
        if not creds_path.exists():
            raise FileNotFoundError(f"Credentials file not found: {creds_path}")
        
        if not token_path.exists():
            raise FileNotFoundError(f"Token file not found: {token_path}")
        
        return True
    
    def _initialize_provider(self) -> bool:
        """Initialize Google Drive API client"""
        try:
            # Try to import Google Drive modules
            try:
                from google.oauth2.credentials import Credentials
                from googleapiclient.discovery import build
                from googleapiclient.http import MediaFileUpload
            except ImportError:
                raise ImportError("Google Drive modules not installed. Run: pip install google-auth google-auth-oauthlib google-api-python-client")
            
            # Load credentials
            self.creds = Credentials.from_authorized_user_file(
                self.config['token_path'], 
                ["https://www.googleapis.com/auth/drive.file"]
            )
            
            # Build service
            self.service = build("drive", "v3", credentials=self.creds)
            
            # Get root folder ID
            self.root_folder_id = self.config.get('backup_folder_id', 'root')
            
            # Set authentication status
            self._authenticated = True
            
            return True
            
        except Exception as e:
            self._authenticated = False
            raise Exception(f"Failed to initialize Google Drive: {str(e)}")
    
    def authenticate(self) -> bool:
        """Authenticate with Google Drive"""
        try:
            # Test authentication by listing files
            self.service.files().list(pageSize=1).execute()
            self._authenticated = True
            return True
        except Exception as e:
            self._authenticated = False
            raise Exception(f"Google Drive authentication failed: {str(e)}")
    
    def upload_file(self, file_path: Path, destination: str) -> Optional[str]:
        """Upload file to Google Drive"""
        try:
            if not self._authenticated:
                if not self.authenticate():
                    return None
            
            # Create or get destination folder
            folder_id = self._get_or_create_folder(destination)
            
            # Upload file
            from googleapiclient.http import MediaFileUpload
            media = MediaFileUpload(str(file_path), mimetype='application/zip')
            file_metadata = {
                "name": file_path.name,
                "parents": [folder_id]
            }
            
            uploaded = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id,webViewLink"
            ).execute()
            
            return uploaded['id']
            
        except Exception as e:
            raise Exception(f"Google Drive upload failed: {str(e)}")
    
    def download_file(self, file_id: str, local_path: Path) -> bool:
        """Download file from Google Drive"""
        try:
            # Get file metadata
            file_metadata = self.service.files().get(fileId=file_id).execute()
            
            # Download file content
            request = self.service.files().get_media(fileId=file_id)
            
            with open(local_path, 'wb') as f:
                f.write(request.execute())
            
            return True
            
        except Exception as e:
            raise Exception(f"Google Drive download failed: {str(e)}")
    
    def list_files(self, folder_path: str = "") -> List[Dict[str, Any]]:
        """List files in Google Drive folder"""
        try:
            if folder_path == "":
                folder_id = self.root_folder_id
            else:
                folder_id = self._get_folder_id(folder_path)
            
            if not folder_id:
                return []
            
            results = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields="files(id,name,size,modifiedTime,webViewLink)"
            ).execute()
            
            files = []
            for file_info in results.get('files', []):
                files.append({
                    'id': file_info['id'],
                    'name': file_info['name'],
                    'size': file_info.get('size', 0),
                    'modified_time': file_info.get('modifiedTime', ''),
                    'url': file_info.get('webViewLink', ''),
                    'type': 'file'
                })
            
            return files
            
        except Exception as e:
            raise Exception(f"Google Drive list files failed: {str(e)}")
    
    def delete_file(self, file_id: str) -> bool:
        """Delete file from Google Drive"""
        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
        except Exception as e:
            raise Exception(f"Google Drive delete failed: {str(e)}")
    
    def create_folder(self, folder_path: str) -> Optional[str]:
        """Create folder in Google Drive"""
        try:
            # Split path into components
            path_parts = folder_path.strip('/').split('/')
            current_parent = self.root_folder_id
            
            for part in path_parts:
                # Check if folder already exists
                existing_folder = self._get_folder_id(part, current_parent)
                if existing_folder:
                    current_parent = existing_folder
                    continue
                
                # Create new folder
                folder_metadata = {
                    "name": part,
                    "mimeType": "application/vnd.google-apps.folder",
                    "parents": [current_parent]
                }
                
                folder = self.service.files().create(
                    body=folder_metadata,
                    fields="id"
                ).execute()
                
                current_parent = folder['id']
            
            return current_parent
            
        except Exception as e:
            raise Exception(f"Google Drive create folder failed: {str(e)}")
    
    def _get_or_create_folder(self, folder_path: str) -> str:
        """Get folder ID, create if it doesn't exist"""
        folder_id = self._get_folder_id(folder_path)
        if folder_id:
            return folder_id
        
        return self.create_folder(folder_path)
    
    def _get_folder_id(self, folder_name: str, parent_id: str = None) -> Optional[str]:
        """Get folder ID by name and parent"""
        try:
            if parent_id is None:
                parent_id = self.root_folder_id
            
            query = f"name='{folder_name}' and '{parent_id}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'"
            
            results = self.service.files().list(
                q=query,
                fields="files(id)"
            ).execute()
            
            files = results.get('files', [])
            return files[0]['id'] if files else None
            
        except Exception:
            return None
