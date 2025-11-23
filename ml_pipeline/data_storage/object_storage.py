"""
Object storage client for MinIO/S3
Handles storage of large files (DICOM images, model artifacts)
"""
from pathlib import Path
from typing import Optional, List, BinaryIO
from io import BytesIO
import json

from minio import Minio
from minio.error import S3Error
import boto3
from botocore.exceptions import ClientError

from ml_pipeline.config.settings import settings
from ml_pipeline.config.logging_config import main_logger, log_audit


class ObjectStorageClient:
    """
    Unified client for object storage (MinIO or S3)
    """
    
    def __init__(self):
        self.storage_type = settings.STORAGE_TYPE
        
        if self.storage_type == "minio":
            self.client = self._init_minio()
        elif self.storage_type == "s3":
            self.client = self._init_s3()
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
        
        self.bucket_name = settings.S3_BUCKET
        self._ensure_bucket_exists()
    
    def _init_minio(self) -> Minio:
        """Initialize MinIO client"""
        try:
            client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE
            )
            main_logger.info(
                "MinIO client initialized",
                extra={'operation': 'storage_init', 'user_id': 'system'}
            )
            return client
        except Exception as e:
            main_logger.error(
                f"Failed to initialize MinIO client: {str(e)}",
                extra={'operation': 'storage_init', 'user_id': 'system'}
            )
            raise
    
    def _init_s3(self):
        """Initialize S3 client"""
        try:
            client = boto3.client(
                's3',
                region_name=settings.S3_REGION
            )
            main_logger.info(
                "S3 client initialized",
                extra={'operation': 'storage_init', 'user_id': 'system'}
            )
            return client
        except Exception as e:
            main_logger.error(
                f"Failed to initialize S3 client: {str(e)}",
                extra={'operation': 'storage_init', 'user_id': 'system'}
            )
            raise
    
    def _ensure_bucket_exists(self):
        """Ensure the bucket exists, create if it doesn't"""
        try:
            if self.storage_type == "minio":
                if not self.client.bucket_exists(self.bucket_name):
                    self.client.make_bucket(self.bucket_name)
                    main_logger.info(
                        f"Created bucket: {self.bucket_name}",
                        extra={'operation': 'bucket_create', 'user_id': 'system'}
                    )
            elif self.storage_type == "s3":
                try:
                    self.client.head_bucket(Bucket=self.bucket_name)
                except ClientError:
                    self.client.create_bucket(
                        Bucket=self.bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': settings.S3_REGION}
                    )
                    main_logger.info(
                        f"Created bucket: {self.bucket_name}",
                        extra={'operation': 'bucket_create', 'user_id': 'system'}
                    )
        except Exception as e:
            main_logger.error(
                f"Failed to ensure bucket exists: {str(e)}",
                extra={'operation': 'bucket_create', 'user_id': 'system'}
            )
            raise
    
    def upload_file(
        self,
        file_path: Path,
        object_name: str,
        metadata: Optional[dict] = None
    ) -> bool:
        """
        Upload a file to object storage
        
        Args:
            file_path: Path to local file
            object_name: Name of object in storage
            metadata: Optional metadata dictionary
            
        Returns:
            True if successful
        """
        try:
            if self.storage_type == "minio":
                self.client.fput_object(
                    self.bucket_name,
                    object_name,
                    str(file_path),
                    metadata=metadata
                )
            elif self.storage_type == "s3":
                extra_args = {'Metadata': metadata} if metadata else {}
                self.client.upload_file(
                    str(file_path),
                    self.bucket_name,
                    object_name,
                    ExtraArgs=extra_args
                )
            
            main_logger.info(
                f"Uploaded file: {object_name}",
                extra={'operation': 'file_upload', 'user_id': 'system'}
            )
            
            log_audit(
                operation='file_upload',
                user_id='system',
                details=f"Uploaded {object_name} to {self.bucket_name}"
            )
            
            return True
            
        except Exception as e:
            main_logger.error(
                f"Failed to upload file {object_name}: {str(e)}",
                extra={'operation': 'file_upload', 'user_id': 'system'}
            )
            return False
    
    def upload_bytes(
        self,
        data: bytes,
        object_name: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[dict] = None
    ) -> bool:
        """
        Upload bytes to object storage
        
        Args:
            data: Bytes to upload
            object_name: Name of object in storage
            content_type: MIME type
            metadata: Optional metadata dictionary
            
        Returns:
            True if successful
        """
        try:
            data_stream = BytesIO(data)
            
            if self.storage_type == "minio":
                self.client.put_object(
                    self.bucket_name,
                    object_name,
                    data_stream,
                    length=len(data),
                    content_type=content_type,
                    metadata=metadata
                )
            elif self.storage_type == "s3":
                extra_args = {
                    'ContentType': content_type,
                    'Metadata': metadata or {}
                }
                self.client.put_object(
                    Bucket=self.bucket_name,
                    Key=object_name,
                    Body=data,
                    **extra_args
                )
            
            main_logger.info(
                f"Uploaded bytes: {object_name}",
                extra={'operation': 'bytes_upload', 'user_id': 'system'}
            )
            
            return True
            
        except Exception as e:
            main_logger.error(
                f"Failed to upload bytes {object_name}: {str(e)}",
                extra={'operation': 'bytes_upload', 'user_id': 'system'}
            )
            return False
    
    def download_file(
        self,
        object_name: str,
        file_path: Path
    ) -> bool:
        """
        Download a file from object storage
        
        Args:
            object_name: Name of object in storage
            file_path: Path to save file locally
            
        Returns:
            True if successful
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            if self.storage_type == "minio":
                self.client.fget_object(
                    self.bucket_name,
                    object_name,
                    str(file_path)
                )
            elif self.storage_type == "s3":
                self.client.download_file(
                    self.bucket_name,
                    object_name,
                    str(file_path)
                )
            
            main_logger.info(
                f"Downloaded file: {object_name}",
                extra={'operation': 'file_download', 'user_id': 'system'}
            )
            
            log_audit(
                operation='file_download',
                user_id='system',
                details=f"Downloaded {object_name} from {self.bucket_name}"
            )
            
            return True
            
        except Exception as e:
            main_logger.error(
                f"Failed to download file {object_name}: {str(e)}",
                extra={'operation': 'file_download', 'user_id': 'system'}
            )
            return False
    
    def download_bytes(self, object_name: str) -> Optional[bytes]:
        """
        Download object as bytes
        
        Args:
            object_name: Name of object in storage
            
        Returns:
            Bytes if successful, None otherwise
        """
        try:
            if self.storage_type == "minio":
                response = self.client.get_object(self.bucket_name, object_name)
                data = response.read()
                response.close()
                response.release_conn()
            elif self.storage_type == "s3":
                response = self.client.get_object(
                    Bucket=self.bucket_name,
                    Key=object_name
                )
                data = response['Body'].read()
            
            main_logger.info(
                f"Downloaded bytes: {object_name}",
                extra={'operation': 'bytes_download', 'user_id': 'system'}
            )
            
            return data
            
        except Exception as e:
            main_logger.error(
                f"Failed to download bytes {object_name}: {str(e)}",
                extra={'operation': 'bytes_download', 'user_id': 'system'}
            )
            return None
    
    def delete_object(self, object_name: str) -> bool:
        """
        Delete an object from storage
        
        Args:
            object_name: Name of object to delete
            
        Returns:
            True if successful
        """
        try:
            if self.storage_type == "minio":
                self.client.remove_object(self.bucket_name, object_name)
            elif self.storage_type == "s3":
                self.client.delete_object(
                    Bucket=self.bucket_name,
                    Key=object_name
                )
            
            main_logger.info(
                f"Deleted object: {object_name}",
                extra={'operation': 'object_delete', 'user_id': 'system'}
            )
            
            log_audit(
                operation='object_delete',
                user_id='system',
                details=f"Deleted {object_name} from {self.bucket_name}"
            )
            
            return True
            
        except Exception as e:
            main_logger.error(
                f"Failed to delete object {object_name}: {str(e)}",
                extra={'operation': 'object_delete', 'user_id': 'system'}
            )
            return False
    
    def list_objects(self, prefix: str = "") -> List[str]:
        """
        List objects in storage
        
        Args:
            prefix: Optional prefix to filter objects
            
        Returns:
            List of object names
        """
        try:
            if self.storage_type == "minio":
                objects = self.client.list_objects(
                    self.bucket_name,
                    prefix=prefix,
                    recursive=True
                )
                return [obj.object_name for obj in objects]
            elif self.storage_type == "s3":
                response = self.client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=prefix
                )
                return [obj['Key'] for obj in response.get('Contents', [])]
            
        except Exception as e:
            main_logger.error(
                f"Failed to list objects: {str(e)}",
                extra={'operation': 'object_list', 'user_id': 'system'}
            )
            return []
    
    def object_exists(self, object_name: str) -> bool:
        """
        Check if an object exists
        
        Args:
            object_name: Name of object to check
            
        Returns:
            True if object exists
        """
        try:
            if self.storage_type == "minio":
                self.client.stat_object(self.bucket_name, object_name)
            elif self.storage_type == "s3":
                self.client.head_object(
                    Bucket=self.bucket_name,
                    Key=object_name
                )
            return True
        except:
            return False
    
    def get_object_metadata(self, object_name: str) -> Optional[dict]:
        """
        Get object metadata
        
        Args:
            object_name: Name of object
            
        Returns:
            Metadata dictionary if successful
        """
        try:
            if self.storage_type == "minio":
                stat = self.client.stat_object(self.bucket_name, object_name)
                return {
                    'size': stat.size,
                    'last_modified': stat.last_modified,
                    'content_type': stat.content_type,
                    'metadata': stat.metadata
                }
            elif self.storage_type == "s3":
                response = self.client.head_object(
                    Bucket=self.bucket_name,
                    Key=object_name
                )
                return {
                    'size': response['ContentLength'],
                    'last_modified': response['LastModified'],
                    'content_type': response['ContentType'],
                    'metadata': response.get('Metadata', {})
                }
        except Exception as e:
            main_logger.error(
                f"Failed to get metadata for {object_name}: {str(e)}",
                extra={'operation': 'metadata_get', 'user_id': 'system'}
            )
            return None


# Global storage client instance
storage_client = ObjectStorageClient()
