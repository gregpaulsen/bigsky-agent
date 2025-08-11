"""
Local Storage Provider
Implements local storage functionality for testing and offline use
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any

from .base_provider import StorageProvider

class LocalStorageProvider(StorageProvider):
    """Local storage provider implementation"""
    
    def _validate_config(self) -> bool:
        """Validate local storage configuration"""
        required_keys = ['storage_path']
        
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")
        
        # Ensure storage path exists
        storage_path = Path(self.config['storage_path'])
        if not storage_path.exists():
            storage_path.mkdir(parents=True, exist_ok=True)
        
        return True
    
    def _initialize_provider(self) -> bool:
        """Initialize local storage"""
        try:
            # Set storage path
            self.storage_path = Path(self.config['storage_path'])
            
            # Ensure storage directory exists
            self.storage_path.mkdir(parents=True, exist_ok=True)
            
            # Set authentication status (always true for local)
            self._authenticated = True
            
            return True
            
        except Exception as e:
            self._authenticated = False
            raise Exception(f"Failed to initialize local storage: {str(e)}")
    
    def authenticate(self) -> bool:
        """Authenticate with local storage (always succeeds)"""
        self._authenticated = True
        return True
    
    def upload_file(self, file_path: Path, destination: str) -> Optional[str]:
        """Copy file to local storage"""
        try:
            if not self._authenticated:
                if not self.authenticate():
                    return None
            
            # Create destination directory
            dest_dir = self.storage_path / destination
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            dest_path = dest_dir / file_path.name
            
            # Handle filename conflicts
            counter = 1
            original_dest = dest_path
            while dest_path.exists():
                stem = original_dest.stem
                suffix = original_dest.suffix
                dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            
            shutil.copy2(file_path, dest_path)
            
            return str(dest_path.relative_to(self.storage_path))
            
        except Exception as e:
            raise Exception(f"Local storage upload failed: {str(e)}")
    
    def download_file(self, file_id: str, local_path: Path) -> bool:
        """Copy file from local storage"""
        try:
            # Construct full path
            source_path = self.storage_path / file_id
            
            if not source_path.exists():
                raise FileNotFoundError(f"File not found: {file_id}")
            
            # Copy file
            shutil.copy2(source_path, local_path)
            
            return True
            
        except Exception as e:
            raise Exception(f"Local storage download failed: {str(e)}")
    
    def list_files(self, folder_path: str = "") -> List[Dict[str, Any]]:
        """List files in local storage folder"""
        try:
            if folder_path == "":
                search_path = self.storage_path
            else:
                search_path = self.storage_path / folder_path
            
            if not search_path.exists():
                return []
            
            files = []
            
            for item in search_path.iterdir():
                if item.is_file():
                    stat = item.stat()
                    files.append({
                        'id': str(item.relative_to(self.storage_path)),
                        'name': item.name,
                        'size': stat.st_size,
                        'modified_time': stat.st_mtime,
                        'url': str(item.absolute()),
                        'type': 'file'
                    })
            
            return files
            
        except Exception as e:
            raise Exception(f"Local storage list files failed: {str(e)}")
    
    def delete_file(self, file_id: str) -> bool:
        """Delete file from local storage"""
        try:
            file_path = self.storage_path / file_id
            
            if not file_path.exists():
                return False
            
            file_path.unlink()
            return True
            
        except Exception as e:
            raise Exception(f"Local storage delete failed: {str(e)}")
    
    def create_folder(self, folder_path: str) -> Optional[str]:
        """Create folder in local storage"""
        try:
            folder_path_obj = self.storage_path / folder_path
            folder_path_obj.mkdir(parents=True, exist_ok=True)
            
            return str(folder_path_obj.relative_to(self.storage_path))
            
        except Exception as e:
            raise Exception(f"Local storage create folder failed: {str(e)}")
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get local storage information"""
        try:
            total_size = sum(f.stat().st_size for f in self.storage_path.rglob('*') if f.is_file())
            file_count = len(list(self.storage_path.rglob('*')))
            
            return {
                'storage_path': str(self.storage_path),
                'total_size': total_size,
                'file_count': file_count,
                'free_space': shutil.disk_usage(self.storage_path).free
            }
        except Exception as e:
            return {
                'storage_path': str(self.storage_path),
                'error': str(e)
            }
