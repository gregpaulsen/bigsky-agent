"""
AWS S3 Storage Provider
Implements AWS S3 storage functionality for enterprise customers
"""

from pathlib import Path
from typing import Dict, List, Optional, Any

from .base_provider import StorageProvider

class S3Provider(StorageProvider):
    """AWS S3 storage provider implementation"""
    
    def _validate_config(self) -> bool:
        """Validate S3 configuration"""
        required_keys = ['bucket_name', 'region_name']
        
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")
        
        # Check for credentials
        if not self._has_credentials():
            raise ValueError("AWS credentials not found. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
        
        return True
    
    def _initialize_provider(self) -> bool:
        """Initialize S3 client"""
        try:
            # Try to import boto3
            try:
                import boto3
                from botocore.exceptions import ClientError, NoCredentialsError
            except ImportError:
                raise ImportError("boto3 module not installed. Run: pip install boto3")
            
            # Create S3 client
            self.s3_client = boto3.client(
                's3',
                region_name=self.config['region_name']
            )
            
            # Test connection by listing buckets
            self.s3_client.list_buckets()
            
            # Set bucket name
            self.bucket_name = self.config['bucket_name']
            
            # Set authentication status
            self._authenticated = True
            
            return True
            
        except Exception as e:
            self._authenticated = False
            raise Exception(f"Failed to initialize S3: {str(e)}")
    
    def _has_credentials(self) -> bool:
        """Check if AWS credentials are available"""
        import os
        return (
            os.environ.get('AWS_ACCESS_KEY_ID') and 
            os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
    
    def authenticate(self) -> bool:
        """Authenticate with AWS S3"""
        try:
            # Test authentication by listing buckets
            self.s3_client.list_buckets()
            self._authenticated = True
            return True
        except Exception as e:
            self._authenticated = False
            raise Exception(f"S3 authentication failed: {str(e)}")
    
    def upload_file(self, file_path: Path, destination: str) -> Optional[str]:
        """Upload file to S3"""
        try:
            if not self._authenticated:
                if not self.authenticate():
                    return None
            
            # Create S3 key
            s3_key = f"{destination}/{file_path.name}"
            
            # Upload file
            self.s3_client.upload_file(
                str(file_path),
                self.bucket_name,
                s3_key
            )
            
            # Generate URL
            url = f"https://{self.bucket_name}.s3.{self.config['region_name']}.amazonaws.com/{s3_key}"
            
            return s3_key
            
        except Exception as e:
            raise Exception(f"S3 upload failed: {str(e)}")
    
    def download_file(self, file_id: str, local_path: Path) -> bool:
        """Download file from S3"""
        try:
            # Download file
            self.s3_client.download_file(
                self.bucket_name,
                file_id,
                str(local_path)
            )
            
            return True
            
        except Exception as e:
            raise Exception(f"S3 download failed: {str(e)}")
    
    def list_files(self, folder_path: str = "") -> List[Dict[str, Any]]:
        """List files in S3 folder"""
        try:
            # List objects with prefix
            prefix = f"{folder_path}/" if folder_path else ""
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                Delimiter='/'
            )
            
            files = []
            
            # Add files
            if 'Contents' in response:
                for obj in response['Contents']:
                    if not obj['Key'].endswith('/'):  # Skip folders
                        files.append({
                            'id': obj['Key'],
                            'name': Path(obj['Key']).name,
                            'size': obj['Size'],
                            'modified_time': obj['LastModified'].timestamp(),
                            'url': f"https://{self.bucket_name}.s3.{self.config['region_name']}.amazonaws.com/{obj['Key']}",
                            'type': 'file'
                        })
            
            return files
            
        except Exception as e:
            raise Exception(f"S3 list files failed: {str(e)}")
    
    def delete_file(self, file_id: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_id
            )
            return True
        except Exception as e:
            raise Exception(f"S3 delete failed: {str(e)}")
    
    def create_folder(self, folder_path: str) -> Optional[str]:
        """Create folder in S3 (S3 doesn't have real folders, but we can create empty objects)"""
        try:
            # S3 doesn't have real folders, but we can create an empty object with trailing slash
            folder_key = f"{folder_path}/"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=folder_key,
                Body=''
            )
            
            return folder_key
            
        except Exception as e:
            raise Exception(f"S3 create folder failed: {str(e)}")
    
    def get_presigned_url(self, file_key: str, expiration: int = 3600) -> str:
        """Get presigned URL for file download"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key
                },
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")
