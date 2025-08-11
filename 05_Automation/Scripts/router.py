"""
BigSkyAg File Router
Automatically routes files from DropZone to appropriate folders based on file type
"""

import os
import shutil
import logging
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from config import ensure_critical_folders, get_routing_destination, get_folder_path, CRITICAL_FOLDERS

# Set up logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('router.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FileRouter:
    """Handles file routing with comprehensive error handling and collision prevention"""
    
    def __init__(self):
        self.routed_count = 0
        self.errors = []
        self.warnings = []
        self.duplicates_handled = 0
        self.failed_files = []
        
    def validate_destination_folders(self) -> bool:
        """Validate that all destination folders exist and are writable"""
        logger.info("🔍 Validating destination folders...")
        
        validation_errors = []
        
        for folder_key, folder_path in CRITICAL_FOLDERS.items():
            try:
                if not folder_path.exists():
                    logger.warning(f"⚠️  Creating missing folder: {folder_path}")
                    folder_path.mkdir(parents=True, exist_ok=True)
                
                # Test write access
                test_file = folder_path / ".router_test"
                test_file.write_text("test")
                test_file.unlink()
                
                logger.info(f"✅ {folder_key}: {folder_path}")
                
            except PermissionError:
                error_msg = f"Permission denied for folder: {folder_path}"
                logger.error(error_msg)
                validation_errors.append(error_msg)
            except Exception as e:
                error_msg = f"Failed to validate folder {folder_path}: {str(e)}"
                logger.error(error_msg)
                validation_errors.append(error_msg)
        
        if validation_errors:
            logger.error(f"❌ Folder validation failed with {len(validation_errors)} errors")
            return False
        
        logger.info("✅ All destination folders validated successfully")
        return True
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file content for duplicate detection"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.warning(f"⚠️  Could not calculate hash for {file_path.name}: {str(e)}")
            return ""
    
    def find_duplicate_by_content(self, file_path: Path, dest_folder: Path) -> Optional[Path]:
        """Find duplicate file by content hash in destination folder"""
        if not dest_folder.exists():
            return None
            
        source_hash = self.calculate_file_hash(file_path)
        if not source_hash:
            return None
            
        for existing_file in dest_folder.glob("*"):
            if existing_file.is_file() and existing_file.suffix.lower() == file_path.suffix.lower():
                try:
                    existing_hash = self.calculate_file_hash(existing_file)
                    if existing_hash == source_hash:
                        return existing_file
                except Exception:
                    continue
        return None
    
    def generate_unique_filename(self, file_path: Path, dest_folder: Path) -> Path:
        """Generate unique filename to prevent overwrites"""
        counter = 1
        original_name = file_path.stem
        extension = file_path.suffix
        
        while True:
            new_name = f"{original_name}_{counter}{extension}"
            new_path = dest_folder / new_name
            if not new_path.exists():
                return new_path
            counter += 1
    
    def validate_file_for_routing(self, file_path: Path) -> Tuple[bool, str]:
        """Validate that a file is safe to route"""
        try:
            # Check if file exists and is readable
            if not file_path.exists():
                return False, "File does not exist"
            
            if not file_path.is_file():
                return False, "Not a regular file"
            
            if file_path.stat().st_size == 0:
                return False, "File is empty"
            
            # Check file permissions
            if not os.access(file_path, os.R_OK):
                return False, "File is not readable"
            
            return True, "File is valid"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def route_single_file(self, file_path: Path) -> bool:
        """Route a single file to its appropriate destination"""
        try:
            # Validate file
            is_valid, validation_msg = self.validate_file_for_routing(file_path)
            if not is_valid:
                logger.warning(f"⚠️  Skipping invalid file {file_path.name}: {validation_msg}")
                self.warnings.append(f"{file_path.name}: {validation_msg}")
                return False
            
            # Get file extension and destination
            ext = file_path.suffix.lower()
            dest_folder = get_routing_destination(ext)
            
            if not dest_folder:
                # Route unknown file types to archive
                dest_folder = get_folder_path("archive")
                logger.info(f"📦 Routing unknown file type {ext} to archive")
            
            # Ensure destination folder exists
            dest_folder.mkdir(parents=True, exist_ok=True)
            
            # Check for duplicates by content
            duplicate_file = self.find_duplicate_by_content(file_path, dest_folder)
            if duplicate_file:
                logger.info(f"🔄 Duplicate content detected: {file_path.name} matches {duplicate_file.name}")
                self.duplicates_handled += 1
                
                # Remove the duplicate file from dropzone
                file_path.unlink()
                logger.info(f"🗑️  Removed duplicate file: {file_path.name}")
                return True
            
            # Generate destination path
            dest_path = dest_folder / file_path.name
            
            # Handle filename conflicts
            if dest_path.exists():
                logger.info(f"⚠️  Filename conflict detected: {file_path.name}")
                dest_path = self.generate_unique_filename(file_path, dest_folder)
                logger.info(f"🔄 Using unique filename: {dest_path.name}")
            
            # Move the file
            shutil.move(str(file_path), str(dest_path))
            
            # Verify move was successful
            if dest_path.exists() and not file_path.exists():
                logger.info(f"✅ Routed: {file_path.name} → {dest_folder.name}/{dest_path.name}")
                self.routed_count += 1
                return True
            else:
                error_msg = f"File move verification failed for {file_path.name}"
                logger.error(error_msg)
                self.errors.append(error_msg)
                return False
                
        except PermissionError as e:
            error_msg = f"Permission denied routing {file_path.name}: {str(e)}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
        except OSError as e:
            error_msg = f"OS error routing {file_path.name}: {str(e)}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
        except Exception as e:
            error_msg = f"Unexpected error routing {file_path.name}: {str(e)}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
    
    def route_files(self) -> bool:
        """Route all files from DropZone to appropriate destination folders"""
        print("🚀 ROUTER: Starting BigSkyAg file routing process...")
        logger.info("🚀 Starting BigSkyAg file routing process...")
        
        # Ensure all critical folders exist
        ensure_critical_folders()
        
        # Validate destination folders
        if not self.validate_destination_folders():
            logger.error("❌ Destination folder validation failed")
            return False
        
        # Get DropZone path
        dropzone = get_folder_path("dropzone")
        print(f"🔍 ROUTER: DropZone path: {dropzone}")
        logger.info(f"🔍 DropZone path: {dropzone}")
        
        if not dropzone.exists():
            logger.error(f"❌ DropZone folder does not exist: {dropzone}")
            return False
        
        # Get all files in dropzone (excluding hidden files and system files)
        all_items = list(dropzone.glob("*"))
        print(f"🔍 ROUTER: All items in DropZone: {[item.name for item in all_items]}")
        logger.info(f"🔍 All items in DropZone: {[item.name for item in all_items]}")
        
        files = [
            f for f in all_items
            if f.is_file() 
            and not f.name.startswith('.')
            and not f.name.startswith('._')
            and f.name != '.DS_Store'
            and f.name != 'Thumbs.db'
        ]
        
        print(f"🔍 ROUTER: Files to route (after filtering): {[f.name for f in files]}")
        logger.info(f"🔍 Files to route (after filtering): {[f.name for f in files]}")
        
        if not files:
            print("ℹ️  ROUTER: No files found in DropZone")
            logger.info("ℹ️  No files found in DropZone")
            return True
        
        print(f"📂 ROUTER: Found {len(files)} files to route")
        logger.info(f"📂 Found {len(files)} files to route")
        
        # Route each file
        for file_path in files:
            print(f"🔄 ROUTER: Processing file: {file_path.name}")
            logger.info(f"🔄 Processing file: {file_path.name}")
            success = self.route_single_file(file_path)
            if not success:
                self.failed_files.append(file_path.name)
                print(f"❌ ROUTER: Failed to route: {file_path.name}")
                logger.error(f"❌ Failed to route: {file_path.name}")
        
        # Generate comprehensive report
        self.generate_routing_report()
        
        return len(self.errors) == 0
    
    def generate_routing_report(self):
        """Generate comprehensive routing report"""
        print("\n" + "="*60)
        print("📊 BIGSKYAG FILE ROUTING REPORT")
        print("="*60)
        
        print(f"✅ Files successfully routed: {self.routed_count}")
        print(f"🔄 Duplicates handled: {self.duplicates_handled}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Errors: {len(self.errors)}")
        print(f"💥 Failed files: {len(self.failed_files)}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        if self.errors:
            print(f"\n❌ Errors:")
            for error in self.errors:
                print(f"   - {error}")
        
        if self.failed_files:
            print(f"\n💥 Failed files:")
            for failed_file in self.failed_files:
                print(f"   - {failed_file}")
        
        print("\n" + "="*60)
        
        if self.errors:
            logger.error(f"Routing completed with {len(self.errors)} errors")
        else:
            logger.info("Routing completed successfully")

def main():
    """Main function"""
    try:
        router = FileRouter()
        success = router.route_files()
        
        if success:
            logger.info("🎉 File routing completed successfully")
            return True
        else:
            logger.error("❌ File routing completed with errors")
            return False
            
    except Exception as e:
        logger.error(f"💥 Critical error in file routing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

