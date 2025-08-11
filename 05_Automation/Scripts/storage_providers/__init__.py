"""
BigSkyAg Storage Providers Package
Provider-agnostic storage abstraction layer
"""

from importlib import import_module

PROVIDER_MODULES = {
    'google_drive': ('.google_drive', 'GoogleDriveProvider'),
    'dropbox': ('.dropbox', 'DropboxProvider'),
    's3': ('.s3', 'S3Provider'),
    'local': ('.local', 'LocalStorageProvider'),
}

def get_storage_provider(provider_name: str, config: dict):
    """Factory function to get storage provider instance"""
    if provider_name not in PROVIDER_MODULES:
        raise ValueError(f"Unsupported storage provider: {provider_name}")
    
    module_path, class_name = PROVIDER_MODULES[provider_name]
    try:
        module = import_module(module_path, package=__package__)
        provider_class = getattr(module, class_name)
        return provider_class(config)
    except ImportError as e:
        raise ImportError(f"Failed to import {module_path}: {e}")
    except AttributeError as e:
        raise AttributeError(f"Class {class_name} not found in {module_path}: {e}")

# Make the function available at module level
__all__ = ['get_storage_provider']
