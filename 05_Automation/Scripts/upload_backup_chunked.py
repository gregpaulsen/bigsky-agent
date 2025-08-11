#!/usr/bin/env python3
"""
BigSkyAg Chunked Backup Upload Script
Handles large backup files with chunked uploads and resumable transfers
"""

import sys
import logging
import time
import os
from pathlib import Path
from typing import Optional, Dict, Any

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from config import get_storage_provider_config
    from storage_providers import get_storage_provider
    CONFIG_AVAILABLE = True
except ImportError as e:
    CONFIG_AVAILABLE = False
    print(f"❌ Import error: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chunked_upload.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration constants
CHUNK_SIZE = 50 * 1024 * 1024  # 50MB chunks
MAX_RETRIES = 3
RETRY_DELAY = 30
UPLOAD_TIMEOUT = 120  # 2 minutes per chunk

class ChunkedUploader:
    """Handles chunked uploads with resume capability"""
    
    def __init__(self, provider, file_path: Path):
        self.provider = provider
        self.file_path = file_path
        self.file_size = file_path.stat().st_size
        self.chunks = []
        self.uploaded_chunks = []
        self.resume_file = file_path.with_suffix('.upload_state')
        
    def calculate_chunks(self):
        """Calculate file chunks for upload"""
        self.chunks = []
        with open(self.file_path, 'rb') as f:
            chunk_num = 0
            while True:
                chunk_data = f.read(CHUNK_SIZE)
                if not chunk_data:
                    break
                    
                chunk_info = {
                    'number': chunk_num,
                    'data': chunk_data,
                    'size': len(chunk_data),
                    'offset': chunk_num * CHUNK_SIZE
                }
                self.chunks.append(chunk_info)
                chunk_num += 1
                
        logger.info(f"📦 File split into {len(self.chunks)} chunks of ~{CHUNK_SIZE // (1024*1024)}MB each")
        
    def save_upload_state(self):
        """Save upload progress for resume capability"""
        state = {
            'file_path': str(self.file_path),
            'file_size': self.file_size,
            'uploaded_chunks': self.uploaded_chunks,
            'timestamp': time.time()
        }
        
        import json
        with open(self.resume_file, 'w') as f:
            json.dump(state, f, indent=2)
            
    def load_upload_state(self) -> bool:
        """Load previous upload state for resume"""
        if not self.resume_file.exists():
            return False
            
        try:
            import json
            with open(self.resume_file, 'r') as f:
                state = json.load(f)
                
            # Verify file hasn't changed
            if (state['file_path'] == str(self.file_path) and 
                state['file_size'] == self.file_size):
                self.uploaded_chunks = state['uploaded_chunks']
                logger.info(f"🔄 Resuming upload from {len(self.uploaded_chunks)} completed chunks")
                return True
            else:
                logger.info("⚠️  File changed, starting fresh upload")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️  Could not load upload state: {e}")
            return False
            
    def upload_chunk(self, chunk_info: Dict[str, Any]) -> bool:
        """Upload a single chunk with retry logic"""
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"📤 Uploading chunk {chunk_info['number'] + 1}/{len(self.chunks)} "
                          f"(attempt {attempt + 1}/{MAX_RETRIES})")
                
                # Create temporary chunk file
                chunk_file = self.file_path.with_suffix(f'.chunk_{chunk_info["number"]}')
                with open(chunk_file, 'wb') as f:
                    f.write(chunk_info['data'])
                
                # Upload chunk
                start_time = time.time()
                chunk_id = self.provider.upload_file(chunk_file, f"chunks/{self.file_path.name}")
                upload_time = time.time() - start_time
                
                # Clean up chunk file
                chunk_file.unlink()
                
                if chunk_id:
                    logger.info(f"✅ Chunk {chunk_info['number'] + 1} uploaded in {upload_time:.1f}s")
                    return True
                else:
                    logger.error(f"❌ Chunk {chunk_info['number'] + 1} upload failed")
                    
            except Exception as e:
                logger.error(f"💥 Chunk {chunk_info['number'] + 1} attempt {attempt + 1} failed: {e}")
                if attempt < MAX_RETRIES - 1:
                    logger.info(f"⏳ Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                    
        return False
        
    def upload_file(self) -> bool:
        """Upload file using chunked approach"""
        try:
            # Load previous state if available
            self.load_upload_state()
            
            # Calculate chunks
            self.calculate_chunks()
            
            # Upload remaining chunks
            for chunk_info in self.chunks:
                if chunk_info['number'] in self.uploaded_chunks:
                    logger.info(f"⏭️  Skipping already uploaded chunk {chunk_info['number'] + 1}")
                    continue
                    
                if not self.upload_chunk(chunk_info):
                    logger.error(f"❌ Failed to upload chunk {chunk_info['number'] + 1}")
                    return False
                    
                # Mark chunk as uploaded
                self.uploaded_chunks.append(chunk_info['number'])
                self.save_upload_state()
                
            # All chunks uploaded, clean up state file
            if self.resume_file.exists():
                self.resume_file.unlink()
                
            logger.info("🎉 All chunks uploaded successfully!")
            return True
            
        except Exception as e:
            logger.error(f"💥 Chunked upload failed: {e}")
            return False

def find_latest_backup():
    """Find the most recent backup file"""
    try:
        backup_dir = Path("/Volumes/BigSkyAgSSD/BigSkyAg/00_Admin/Backups")
        if not backup_dir.exists():
            logger.error(f"❌ Backup directory not found: {backup_dir}")
            return None
        
        backup_files = list(backup_dir.glob("*.zip"))
        if not backup_files:
            logger.error("❌ No backup files found")
            return None
        
        # Sort by modification time, newest first
        latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
        
        if not latest_backup.exists():
            logger.error(f"❌ Latest backup file not found: {latest_backup}")
            return None
            
        file_size = latest_backup.stat().st_size
        if file_size == 0:
            logger.error(f"❌ Backup file is empty: {latest_backup}")
            return None
            
        logger.info(f"✅ Found latest backup: {latest_backup.name} ({file_size / (1024**2):.1f} MB)")
        return latest_backup
        
    except Exception as e:
        logger.error(f"💥 Error finding latest backup: {e}")
        return None

def main():
    """Main function"""
    logger.info("🚀 Starting chunked backup upload...")
    
    if not CONFIG_AVAILABLE:
        logger.error("❌ Configuration not available")
        return False
        
    try:
        # Initialize storage
        config = get_storage_provider_config()
        provider = get_storage_provider(config['provider'], config)
        
        if not provider:
            logger.error("❌ Failed to initialize storage provider")
            return False
            
        # Find latest backup
        backup_path = find_latest_backup()
        if not backup_path:
            logger.error("❌ No valid backup found")
            return False
            
        # Create chunked uploader
        uploader = ChunkedUploader(provider, backup_path)
        
        # Upload file
        if uploader.upload_file():
            logger.info("🎉 Chunked upload completed successfully!")
            return True
        else:
            logger.error("❌ Chunked upload failed")
            return False
            
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
