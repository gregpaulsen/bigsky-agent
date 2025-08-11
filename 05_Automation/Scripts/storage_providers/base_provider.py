"""
Abstract Base Storage Provider
Defines the interface that all storage providers must implement
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class StorageProvider(ABC):
    """Abstract base class for all storage providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_name = config.get('provider', 'unknown')
        self.company_name = config.get('company_name', 'Unknown')
        self.backup_prefix = config.get('backup_prefix', 'Backup')
        self._authenticated = False
        self._validate_config()
        self._initialize_provider()
    
    @abstractmethod
    def _validate_config(self) -> bool: ...

    @abstractmethod
    def _initialize_provider(self) -> bool: ...

    @abstractmethod
    def authenticate(self) -> bool: ...

    @abstractmethod
    def upload_file(self, file_path: Path, destination: str) -> Optional[str]: ...

    @abstractmethod
    def download_file(self, file_id: str, local_path: Path) -> bool: ...

    @abstractmethod
    def list_files(self, folder_path: str = "") -> List[Dict[str, Any]]: ...

    @abstractmethod
    def delete_file(self, file_id: str) -> bool: ...

    @abstractmethod
    def create_folder(self, folder_path: str) -> Optional[str]: ...

    def get_backup_destination(self, backup_type: str = "daily") -> str:
        return f"{self.backup_prefix}/{backup_type}"

    def upload_backup(self, backup_path: Path, backup_type: str = "daily") -> Optional[str]:
        try:
            destination = self.get_backup_destination(backup_type)
            file_id = self.upload_file(backup_path, destination)
            if file_id:
                logger.info(f"✅ Backup uploaded: {backup_path.name} → {destination}")
            else:
                logger.error(f"❌ Upload failed: {backup_path.name}")
            return file_id
        except Exception as e:
            logger.error(f"💥 Error uploading backup {backup_path.name}: {e}")
            return None

    def cleanup_old_backups(self, max_backups: int = 5, backup_type: str = "daily") -> bool:
        try:
            folder_path = self.get_backup_destination(backup_type)
            files = self.list_files(folder_path)
            if len(files) <= max_backups:
                return True
            files_sorted = sorted(files, key=lambda x: x.get('modified_time', 0), reverse=True)
            for old in files_sorted[max_backups:]:
                if not self.delete_file(old.get('id')):
                    logger.warning(f"⚠️ Could not delete old backup: {old.get('name')}")
            return True
        except Exception as e:
            logger.error(f"💥 Error during cleanup: {e}")
            return False

    def test_connection(self) -> bool:
        try:
            _ = self.list_files("")
            return True
        except Exception as e:
            logger.error(f"❌ Connection test failed for {self.provider_name}: {e}")
            return False

    def get_provider_info(self) -> Dict[str, Any]:
        return {
            "provider_name": self.provider_name,
            "company_name": self.company_name,
            "backup_prefix": self.backup_prefix,
            "authenticated": self._authenticated,
        }
