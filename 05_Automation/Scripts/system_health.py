#!/usr/bin/env python3
"""
BigSkyAg System Health Check
Comprehensive health check for the BigSkyAg automation system
"""

import os
import sys
import importlib
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

# Import config (will fail gracefully if not available)
try:
    from config import (
        BASE_DIR, 
        CRITICAL_FOLDERS, 
        ROUTING_RULES,
        STORAGE_CONFIG,
        get_storage_provider_config
    )
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    print("⚠️  Warning: config.py not available, using fallback configuration")

class SystemHealthChecker:
    """Comprehensive system health checker for BigSkyAg automation"""
    
    def __init__(self):
        self.results = {}
        self.errors = []
        self.warnings = []
        
        # Fallback configuration if config.py is not available
        if not CONFIG_AVAILABLE:
            self.base_dir = Path("/Volumes/BigSkyAgSSD/BigSkyAg")
            self.critical_folders = {
                "backups": self.base_dir / "00_Admin" / "Backups",
                "dropzone": self.base_dir / "BigSkyAgDropZone",
                "archive": self.base_dir / "Z_Archive",
                "scripts": self.base_dir / "05_Automation" / "Scripts",
                "admin": self.base_dir / "00_Admin",
                "branding": self.base_dir / "01_Branding",
                "field_projects": self.base_dir / "02_Field_Projects",
                "mapping": self.base_dir / "03_Mapping_QGIS",
                "training": self.base_dir / "04_Training",
                "automation": self.base_dir / "05_Automation",
                "business": self.base_dir / "06_Business_Strategy"
            }
        else:
            self.base_dir = BASE_DIR
            self.critical_folders = CRITICAL_FOLDERS
    
    def print_header(self):
        """Print the health check header"""
        print("🏥" + "="*58 + "🏥")
        print("🏥                BIGSKYAG SYSTEM HEALTH CHECK                🏥")
        print("🏥" + "="*58 + "🏥")
        print()
    
    def print_section_header(self, title: str):
        """Print a section header"""
        print(f"🔍 {title}")
        print("-" * 60)
    
    def print_result(self, test_name: str, passed: bool, details: str = ""):
        """Print a test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} {test_name}")
        if details:
            print(f"      {details}")
        
        # Store result
        self.results[test_name] = passed
        if not passed:
            self.errors.append(test_name)
    
    def check_ssd_mount(self) -> bool:
        """Check if SSD is mounted and accessible"""
        self.print_section_header("SSD MOUNT STATUS")
        
        ssd_volume = Path("/Volumes/BigSkyAgSSD")
        
        if not ssd_volume.exists():
            self.print_result("SSD Volume Mount", False, "SSD not mounted at /Volumes/BigSkyAgSSD")
            return False
        
        # Test write access
        try:
            test_file = ssd_volume / ".health_check_test"
            test_file.write_text("test")
            test_file.unlink()
            self.print_result("SSD Volume Mount", True, f"SSD accessible at {ssd_volume}")
            self.print_result("SSD Write Access", True, "Can write to SSD volume")
        except Exception as e:
            self.print_result("SSD Volume Mount", True, f"SSD accessible at {ssd_volume}")
            self.print_result("SSD Write Access", False, f"Cannot write to SSD: {str(e)}")
            return False
        
        return True
    
    def check_base_directory(self) -> bool:
        """Check if the base BigSkyAg directory exists and is accessible"""
        self.print_section_header("BASE DIRECTORY STATUS")
        
        if not self.base_dir.exists():
            self.print_result("Base Directory", False, f"Base directory not found: {self.base_dir}")
            return False
        
        try:
            # Test write access
            test_file = self.base_dir / ".health_check_test"
            test_file.write_text("test")
            test_file.unlink()
            
            self.print_result("Base Directory", True, f"Base directory accessible: {self.base_dir}")
            self.print_result("Base Directory Write Access", True, "Can write to base directory")
            return True
            
        except Exception as e:
            self.print_result("Base Directory", True, f"Base directory accessible: {self.base_dir}")
            self.print_result("Base Directory Write Access", False, f"Cannot write to base directory: {str(e)}")
            return False
    
    def check_critical_folders(self) -> bool:
        """Check if all critical folders exist and are accessible"""
        self.print_section_header("CRITICAL FOLDERS STATUS")
        
        all_folders_ok = True
        
        for folder_name, folder_path in self.critical_folders.items():
            try:
                if not folder_path.exists():
                    # Try to create the folder
                    folder_path.mkdir(parents=True, exist_ok=True)
                    if folder_path.exists():
                        self.print_result(f"Folder: {folder_name}", True, f"Created: {folder_path}")
                    else:
                        self.print_result(f"Folder: {folder_name}", False, f"Failed to create: {folder_path}")
                        all_folders_ok = False
                else:
                    # Test write access
                    test_file = folder_path / ".health_check_test"
                    test_file.write_text("test")
                    test_file.unlink()
                    self.print_result(f"Folder: {folder_name}", True, f"Exists and writable: {folder_path}")
                    
            except Exception as e:
                self.print_result(f"Folder: {folder_name}", False, f"Error: {str(e)}")
                all_folders_ok = False
        
        return all_folders_ok
    
    def check_storage_provider_setup(self) -> bool:
        """Check storage provider authentication/setup (provider-agnostic)"""
        self.print_section_header("STORAGE PROVIDER SETUP")

        if not CONFIG_AVAILABLE:
            self.print_result("Storage Provider", False, "config.py not available")
            return False

        provider = STORAGE_CONFIG.get("provider", "unknown")
        self.print_result("Selected Provider", True, provider)

        scripts_folder = self.critical_folders.get("scripts", self.base_dir / "05_Automation" / "Scripts")
        if not scripts_folder.exists():
            self.print_result("Scripts Folder", False, f"Scripts folder not found: {scripts_folder}")
            return False

        ok = True
        if provider == "google_drive":
            creds = scripts_folder / "credentials.json"
            token = scripts_folder / "token.json"
            self.print_result("credentials.json", creds.exists(), str(creds))
            self.print_result("token.json", token.exists(), str(token))
            ok = creds.exists() and token.exists()
        elif provider == "dropbox":
            # token stored in config or external file as needed
            self.print_result("Dropbox Token", True, "Configured via STORAGE_CONFIG or dropbox_token.json")
        elif provider == "s3":
            # environment variables required
            has_ak = bool(os.environ.get("AWS_ACCESS_KEY_ID"))
            has_sk = bool(os.environ.get("AWS_SECRET_ACCESS_KEY"))
            self.print_result("AWS_ACCESS_KEY_ID", has_ak)
            self.print_result("AWS_SECRET_ACCESS_KEY", has_sk)
            ok = has_ak and has_sk
        elif provider == "local":
            self.print_result("Local Storage", True, "No authentication required")
        else:
            self.print_result("Storage Provider", False, f"Unsupported provider: {provider}")
            ok = False

        self.print_result("Provider Setup", ok, "OK" if ok else "Check provider configuration")
        return ok
    
    def check_python_packages(self) -> bool:
        """Check required Python packages"""
        self.print_section_header("PYTHON PACKAGES STATUS")
        
        required_packages = [
            "pathlib",
            "shutil", 
            "os",
            "sys",
            "logging",
            "subprocess",
            "hashlib",
            "time",
            "typing"
        ]
        
        optional_packages = [
            "google.auth",
            "google_auth_oauthlib", 
            "googleapiclient"
        ]
        
        all_required_ok = True
        
        # Check required packages
        for package in required_packages:
            try:
                importlib.import_module(package)
                self.print_result(f"Required: {package}", True)
            except ImportError:
                self.print_result(f"Required: {package}", False, f"Package {package} not available")
                all_required_ok = False
        
        # Check optional packages
        for package in optional_packages:
            try:
                importlib.import_module(package)
                self.print_result(f"Optional: {package}", True)
            except ImportError:
                self.print_result(f"Optional: {package}", False, f"Package {package} not available (Google Drive features disabled)")
        
        return all_required_ok
    
    def check_system_tools(self) -> bool:
        """Check required system tools"""
        self.print_section_header("SYSTEM TOOLS STATUS")
        
        required_tools = ["zip", "rsync"]
        all_tools_ok = True
        
        for tool in required_tools:
            try:
                result = subprocess.run([tool, "--version"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.print_result(f"Tool: {tool}", True)
                else:
                    self.print_result(f"Tool: {tool}", False, f"Tool {tool} returned error code {result.returncode}")
                    all_tools_ok = False
            except FileNotFoundError:
                self.print_result(f"Tool: {tool}", False, f"Tool {tool} not found in PATH")
                all_tools_ok = False
            except subprocess.TimeoutExpired:
                self.print_result(f"Tool: {tool}", False, f"Tool {tool} timed out")
                all_tools_ok = False
            except Exception as e:
                self.print_result(f"Tool: {tool}", False, f"Error checking {tool}: {str(e)}")
                all_tools_ok = False
        
        return all_tools_ok
    
    def check_automation_scripts(self) -> bool:
        """Check presence of required automation scripts"""
        self.print_section_header("AUTOMATION SCRIPTS STATUS")
        
        scripts_folder = self.critical_folders.get("scripts", self.base_dir / "05_Automation" / "Scripts")
        
        if not scripts_folder.exists():
            self.print_result("Scripts Directory", False, f"Scripts directory not found: {scripts_folder}")
            return False
        
        required_scripts = [
            "config.py",
            "router.py",
            "create_backup_zip.py",
            "cleanup_old_backups.py",
            "mirror_to_ssd.py",
            "upload_backup.py",
            "authenticate_storage.py",
            "system_health.py"
        ]
        
        all_scripts_ok = True
        
        for script in required_scripts:
            script_path = scripts_folder / script
            if script_path.exists():
                self.print_result(f"Script: {script}", True)
            else:
                self.print_result(f"Script: {script}", False, f"Script not found: {script_path}")
                all_scripts_ok = False
        
        return all_scripts_ok
    
    def check_file_routing_rules(self) -> bool:
        """Check file routing rules configuration"""
        self.print_section_header("FILE ROUTING RULES STATUS")
        
        if not CONFIG_AVAILABLE:
            self.print_result("Routing Rules", False, "config.py not available")
            return False
        
        if not ROUTING_RULES:
            self.print_result("Routing Rules", False, "No routing rules defined")
            return False
        
        # Check that all routing destinations exist
        all_rules_ok = True
        for ext, folder_key in ROUTING_RULES.items():
            if folder_key in self.critical_folders:
                folder_path = self.critical_folders[folder_key]
                if folder_path.exists():
                    self.print_result(f"Route: {ext} → {folder_key}", True)
                else:
                    self.print_result(f"Route: {ext} → {folder_key}", False, f"Destination folder not found: {folder_path}")
                    all_rules_ok = False
            else:
                self.print_result(f"Route: {ext} → {folder_key}", False, f"Unknown destination folder: {folder_key}")
                all_rules_ok = False
        
        return all_rules_ok
    
    def generate_summary(self):
        """Generate and print the health check summary"""
        print("\n" + "🏥" + "="*58 + "🏥")
        print("🏥                    HEALTH CHECK SUMMARY                    🏥")
        print("🏥" + "="*58 + "🏥")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 OVERALL STATUS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        
        if failed_tests == 0:
            print(f"\n🎉 ALL SYSTEMS OPERATIONAL!")
            print(f"   The BigSkyAg automation system is ready to use.")
        else:
            print(f"\n⚠️  {failed_tests} ISSUES DETECTED:")
            for test_name in self.errors:
                print(f"   ❌ {test_name}")
            
            print(f"\n💡 RECOMMENDATIONS:")
            if "SSD Volume Mount" in self.errors:
                print("   • Ensure SSD is mounted at /Volumes/BigSkyAgSSD")
            if "Google Credentials" in self.errors or "Google Token" in self.errors:
                print("   • Set up Google Drive authentication (run authenticate_drive.py)")
            if "Tool: zip" in self.errors or "Tool: rsync" in self.errors:
                print("   • Install missing system tools (zip, rsync)")
            if "Required:" in str(self.errors):
                print("   • Install missing Python packages")
        
        print("\n" + "🏥" + "="*58 + "🏥")
        
        return failed_tests == 0
    
    def run_health_check(self) -> bool:
        """Run the complete health check"""
        self.print_header()
        
        # Run all health checks
        checks = [
            ("SSD Mount", self.check_ssd_mount),
            ("Base Directory", self.check_base_directory),
            ("Critical Folders", self.check_critical_folders),
            ("Storage Provider Setup", self.check_storage_provider_setup),
            ("Python Packages", self.check_python_packages),
            ("System Tools", self.check_system_tools),
            ("Automation Scripts", self.check_automation_scripts),
            ("File Routing Rules", self.check_file_routing_rules)
        ]
        
        for check_name, check_func in checks:
            try:
                check_func()
            except Exception as e:
                self.print_result(check_name, False, f"Health check failed: {str(e)}")
                self.errors.append(check_name)
        
        # Generate summary
        return self.generate_summary()

def main():
    """Main function"""
    try:
        checker = SystemHealthChecker()
        success = checker.run_health_check()
        return success
    except Exception as e:
        print(f"💥 Critical error in health check: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
