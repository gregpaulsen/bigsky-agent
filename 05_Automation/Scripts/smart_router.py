#!/usr/bin/env python3
"""
BigSkyAg Smart Document Router
Intelligently routes documents based on content analysis, not just file extensions
"""

import os
import shutil
import logging
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from config import ensure_critical_folders, get_folder_path, CRITICAL_FOLDERS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('smart_router.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SmartDocumentRouter:
    """Intelligent document router with content analysis and smart naming"""
    
    def __init__(self):
        self.routed_count = 0
        self.errors = []
        self.warnings = []
        self.duplicates_handled = 0
        self.failed_files = []
        
        # Document type patterns for intelligent routing
        self.document_patterns = {
            'uei': {
                'keywords': ['uei', 'unique entity', 'entity identifier', 'sam.gov'],
                'destination': '00_Admin/UEI_Documents',
                'naming': 'UEI_{date}_{company}'
            },
            'contract': {
                'keywords': ['contract', 'agreement', 'sow', 'statement of work', 'proposal'],
                'destination': '00_Admin/Contracts',
                'naming': 'Contract_{date}_{title}'
            },
            'invoice': {
                'keywords': ['invoice', 'bill', 'payment', 'receipt'],
                'destination': '00_Admin/Invoices',
                'naming': 'Invoice_{date}_{vendor}_{amount}'
            },
            'grant': {
                'keywords': ['grant', 'funding', 'application', 'rfa', 'rfp'],
                'destination': '00_Admin/Grants',
                'naming': 'Grant_{date}_{agency}_{title}'
            },
            'crop_data': {
                'keywords': ['crop', 'field', 'yield', 'harvest', 'planting'],
                'destination': '02_Field_Projects/Crop_Data',
                'naming': 'Crop_{date}_{field}_{type}'
            },
            'drone_data': {
                'keywords': ['drone', 'uav', 'aerial', 'ndvi', 'multispectral'],
                'destination': '02_Field_Projects/Drone_Data',
                'naming': 'Drone_{date}_{field}_{mission}'
            },
            'gis_data': {
                'keywords': ['shapefile', 'geojson', 'kml', 'coordinates', 'boundary'],
                'destination': '03_Mapping_QGIS/GIS_Data',
                'naming': 'GIS_{date}_{type}_{location}'
            }
        }
        
        # File extension to general category mapping
        self.extension_categories = {
            '.pdf': 'document',
            '.docx': 'document',
            '.xlsx': 'spreadsheet',
            '.csv': 'data',
            '.tif': 'image',
            '.jpg': 'image',
            '.png': 'image',
            '.zip': 'archive',
            '.shp': 'gis',
            '.gpkg': 'gis',
            '.qgz': 'qgis_project'
        }
    
    def analyze_document_content(self, file_path: Path) -> Dict[str, any]:
        """Analyze document content to determine type and routing"""
        analysis = {
            'type': 'unknown',
            'confidence': 0.0,
            'destination': None,
            'naming_pattern': None,
            'keywords_found': [],
            'suggested_name': None
        }
        
        try:
            # Get file info
            file_size = file_path.stat().st_size
            file_name = file_path.name.lower()
            file_ext = file_path.suffix.lower()
            
            # Check file extension category
            if file_ext in self.extension_categories:
                analysis['type'] = self.extension_categories[file_ext]
            
            # Analyze filename for patterns
            for doc_type, pattern_info in self.document_patterns.items():
                score = 0.0
                keywords_found = []
                
                # Check filename for keywords
                for keyword in pattern_info['keywords']:
                    if keyword.lower() in file_name:
                        score += 0.3
                        keywords_found.append(keyword)
                
                # Check for specific patterns (like UEI numbers)
                if doc_type == 'uei' and re.search(r'uei[_-]?\d{12}', file_name, re.IGNORECASE):
                    score += 0.5
                    keywords_found.append('uei_number')
                
                # Check for date patterns
                if re.search(r'\d{4}[-_]\d{1,2}[-_]\d{1,2}', file_name):
                    score += 0.2
                    keywords_found.append('date')
                
                # If we found a good match
                if score > 0.3:
                    analysis['type'] = doc_type
                    analysis['confidence'] = score
                    analysis['destination'] = pattern_info['destination']
                    analysis['naming_pattern'] = pattern_info['naming']
                    analysis['keywords_found'] = keywords_found
                    break
            
            # Generate suggested name if we have a pattern
            if analysis['naming_pattern']:
                analysis['suggested_name'] = self._generate_smart_name(
                    file_path, analysis['naming_pattern']
                )
            
            # Fallback routing based on extension
            if not analysis['destination']:
                analysis['destination'] = self._get_fallback_destination(file_ext)
            
        except Exception as e:
            logger.warning(f"Could not analyze {file_path.name}: {str(e)}")
        
        return analysis
    
    def _generate_smart_name(self, file_path: Path, pattern: str) -> str:
        """Generate smart filename based on pattern"""
        try:
            # Extract date from filename or use current date
            date_match = re.search(r'\d{4}[-_]\d{1,2}[-_]\d{1,2}', file_path.name)
            if date_match:
                date_str = date_match.group().replace('_', '-')
            else:
                date_str = datetime.now().strftime('%Y-%m-%d')
            
            # Extract company/client name if present
            company_match = re.search(r'(bigsky|paulys|company|client)', file_path.name.lower())
            company = company_match.group(1) if company_match else 'unknown'
            
            # Build new name
            new_name = pattern.format(
                date=date_str,
                company=company.title(),
                title=file_path.stem[:20],
                vendor='unknown',
                amount='unknown',
                field='unknown',
                type='unknown',
                mission='unknown',
                location='unknown'
            )
            
            return f"{new_name}{file_path.suffix}"
            
        except Exception as e:
            logger.warning(f"Could not generate smart name: {str(e)}")
            return file_path.name
    
    def _get_fallback_destination(self, extension: str) -> str:
        """Get fallback destination for unknown file types"""
        fallback_map = {
            '.pdf': '00_Admin/Documents',
            '.docx': '00_Admin/Documents',
            '.xlsx': '00_Admin/Spreadsheets',
            '.csv': '00_Admin/Data',
            '.tif': '02_Field_Projects/Images',
            '.jpg': '02_Field_Projects/Images',
            '.png': '02_Field_Projects/Images',
            '.zip': '00_Admin/Archives',
            '.shp': '03_Mapping_QGIS/Shapefiles',
            '.gpkg': '03_Mapping_QGIS/Geopackages'
        }
        
        return fallback_map.get(extension, '00_Admin/Uncategorized')
    
    def route_document(self, file_path: Path) -> bool:
        """Route a single document intelligently"""
        try:
            print(f"🔍 Analyzing: {file_path.name}")
            
            # Analyze document content
            analysis = self.analyze_document_content(file_path)
            
            print(f"📊 Analysis: {analysis['type']} (confidence: {analysis['confidence']:.2f})")
            print(f"🎯 Destination: {analysis['destination']}")
            
            # Get destination folder
            dest_folder = Path(analysis['destination'])
            if not dest_folder.is_absolute():
                dest_folder = Path.home() / "Desktop" / "BigSkyAg" / analysis['destination']
            
            # Ensure destination exists
            dest_folder.mkdir(parents=True, exist_ok=True)
            
            # Generate destination filename
            if analysis['suggested_name'] and analysis['confidence'] > 0.5:
                dest_filename = analysis['suggested_name']
                print(f"✨ Smart naming: {dest_filename}")
            else:
                dest_filename = file_path.name
                print(f"📝 Keeping original name: {dest_filename}")
            
            dest_path = dest_folder / dest_filename
            
            # Handle filename conflicts
            if dest_path.exists():
                counter = 1
                while dest_path.exists():
                    stem = dest_path.stem
                    suffix = dest_path.suffix
                    dest_path = dest_folder / f"{stem}_{counter}{suffix}"
                    counter += 1
                print(f"🔄 Resolved conflict: {dest_path.name}")
            
            # Move the file
            shutil.move(str(file_path), str(dest_path))
            
            # Verify move
            if dest_path.exists() and not file_path.exists():
                print(f"✅ Routed: {file_path.name} → {dest_path}")
                self.routed_count += 1
                return True
            else:
                error_msg = f"File move failed for {file_path.name}"
                logger.error(error_msg)
                self.errors.append(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Error routing {file_path.name}: {str(e)}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
    
    def route_all_documents(self) -> bool:
        """Route all documents from Desktop Dropzone"""
        print("🚀 Starting BigSkyAg Smart Document Routing...")
        
        # Get Desktop Dropzone path
        dropzone = Path.home() / "Desktop" / "BigSkyAgDropzone"
        print(f"🔍 Dropzone: {dropzone}")
        
        if not dropzone.exists():
            print("❌ Desktop Dropzone not found")
            return False
        
        # Get all files
        files = [f for f in dropzone.glob("*") if f.is_file() and not f.name.startswith('.')]
        print(f"📂 Found {len(files)} documents to route")
        
        if not files:
            print("ℹ️  No documents found in Dropzone")
            return True
        
        # Route each document
        for file_path in files:
            success = self.route_document(file_path)
            if not success:
                self.failed_files.append(file_path.name)
        
        # Generate report
        self._generate_report()
        
        return len(self.errors) == 0
    
    def _generate_report(self):
        """Generate routing report"""
        print("\n" + "="*60)
        print("📊 SMART DOCUMENT ROUTING REPORT")
        print("="*60)
        print(f"✅ Documents routed: {self.routed_count}")
        print(f"❌ Errors: {len(self.errors)}")
        print(f"💥 Failed: {len(self.failed_files)}")
        
        if self.errors:
            print(f"\n❌ Errors:")
            for error in self.errors:
                print(f"   - {error}")
        
        if self.failed_files:
            print(f"\n💥 Failed files:")
            for failed in self.failed_files:
                print(f"   - {failed}")
        
        print("="*60)

def main():
    """Main function"""
    try:
        router = SmartDocumentRouter()
        success = router.route_all_documents()
        
        if success:
            print("🎉 Smart routing completed successfully!")
            return True
        else:
            print("❌ Smart routing completed with errors")
            return False
            
    except Exception as e:
        print(f"💥 Critical error: {str(e)}")
        return False

if __name__ == "__main__":
    main()
