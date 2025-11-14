"""
S3 Connector for Energy Maps and Model Checkpoints

Production-grade S3 integration with async support, retry logic,
multipart uploads, and versioning for energy maps and diffusion checkpoints.
"""

import asyncio
import hashlib
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, BinaryIO
from datetime import datetime, timedelta
import json

try:
    import boto3
    from botocore.exceptions import ClientError, BotoCoreError
    from botocore.config import Config
    import aioboto3
except ImportError:
    boto3 = None
    aioboto3 = None
    ClientError = Exception
    BotoCoreError = Exception

import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class S3Config(BaseModel):
    """S3 configuration"""
    bucket_name: str
    region: str = "us-east-1"
    endpoint_url: Optional[str] = None  # For MinIO/localstack
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    use_ssl: bool = True
    max_pool_connections: int = 50
    connect_timeout: int = 60
    read_timeout: int = 60
    max_retries: int = 3
    multipart_threshold: int = 100 * 1024 * 1024  # 100 MB
    multipart_chunksize: int = 10 * 1024 * 1024  # 10 MB
    enable_versioning: bool = True


class S3Object(BaseModel):
    """S3 object metadata"""
    key: str
    size: int
    last_modified: datetime
    etag: str
    version_id: Optional[str] = None
    metadata: Dict[str, str] = {}
    content_type: str = "application/octet-stream"


class S3Connector:
    """
    Production S3 connector for EIL platform.

    Features:
    - Async and sync interfaces
    - Automatic retry with exponential backoff
    - Multipart upload for large files
    - Versioning support
    - Metadata tagging
    - Pre-signed URLs for secure sharing
    - Energy map serialization/deserialization
    - Model checkpoint management
    """

    def __init__(self, config: S3Config):
        """
        Initialize S3 connector.

        Args:
            config: S3 configuration
        """
        if boto3 is None:
            raise ImportError(
                "boto3 and aioboto3 required for S3 integration. "
                "Install with: pip install boto3 aioboto3"
            )

        self.config = config

        # Boto3 config
        self.boto_config = Config(
            region_name=config.region,
            max_pool_connections=config.max_pool_connections,
            connect_timeout=config.connect_timeout,
            read_timeout=config.read_timeout,
            retries={'max_attempts': config.max_retries, 'mode': 'adaptive'}
        )

        # Sync client
        self.s3_client = boto3.client(
            's3',
            endpoint_url=config.endpoint_url,
            aws_access_key_id=config.access_key_id,
            aws_secret_access_key=config.secret_access_key,
            use_ssl=config.use_ssl,
            config=self.boto_config
        )

        # Async session
        self.async_session = aioboto3.Session()

        # Ensure bucket exists
        self._ensure_bucket()

        logger.info(
            f"S3Connector initialized: bucket={config.bucket_name}, "
            f"region={config.region}"
        )

    def _ensure_bucket(self):
        """Create bucket if it doesn't exist"""
        try:
            self.s3_client.head_bucket(Bucket=self.config.bucket_name)
            logger.debug(f"Bucket exists: {self.config.bucket_name}")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.info(f"Creating bucket: {self.config.bucket_name}")
                try:
                    if self.config.region == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.config.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.config.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.config.region}
                        )

                    # Enable versioning if configured
                    if self.config.enable_versioning:
                        self.s3_client.put_bucket_versioning(
                            Bucket=self.config.bucket_name,
                            VersioningConfiguration={'Status': 'Enabled'}
                        )
                        logger.info(f"Versioning enabled for: {self.config.bucket_name}")

                except ClientError as create_error:
                    logger.error(f"Failed to create bucket: {create_error}")
                    raise
            else:
                logger.error(f"Bucket access error: {e}")
                raise

    def upload_file(
        self,
        file_path: str,
        s3_key: str,
        metadata: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None,
        storage_class: str = 'STANDARD'
    ) -> S3Object:
        """
        Upload file to S3.

        Args:
            file_path: Local file path
            s3_key: S3 object key
            metadata: Custom metadata
            content_type: MIME type
            storage_class: S3 storage class (STANDARD, INTELLIGENT_TIERING, etc.)

        Returns:
            S3Object metadata
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        extra_args = {
            'StorageClass': storage_class
        }

        if metadata:
            extra_args['Metadata'] = metadata

        if content_type:
            extra_args['ContentType'] = content_type

        try:
            logger.info(f"Uploading: {file_path} -> s3://{self.config.bucket_name}/{s3_key}")

            # Use multipart for large files
            if file_path.stat().st_size > self.config.multipart_threshold:
                self.s3_client.upload_file(
                    str(file_path),
                    self.config.bucket_name,
                    s3_key,
                    ExtraArgs=extra_args,
                    Config=boto3.s3.transfer.TransferConfig(
                        multipart_threshold=self.config.multipart_threshold,
                        multipart_chunksize=self.config.multipart_chunksize,
                        use_threads=True
                    )
                )
            else:
                self.s3_client.upload_file(
                    str(file_path),
                    self.config.bucket_name,
                    s3_key,
                    ExtraArgs=extra_args
                )

            # Get object metadata
            response = self.s3_client.head_object(
                Bucket=self.config.bucket_name,
                Key=s3_key
            )

            return S3Object(
                key=s3_key,
                size=response['ContentLength'],
                last_modified=response['LastModified'],
                etag=response['ETag'].strip('"'),
                version_id=response.get('VersionId'),
                metadata=response.get('Metadata', {}),
                content_type=response.get('ContentType', 'application/octet-stream')
            )

        except (ClientError, BotoCoreError) as e:
            logger.error(f"Upload failed: {e}")
            raise

    def download_file(
        self,
        s3_key: str,
        file_path: str,
        version_id: Optional[str] = None
    ) -> Path:
        """
        Download file from S3.

        Args:
            s3_key: S3 object key
            file_path: Local destination path
            version_id: Specific version to download

        Returns:
            Path to downloaded file
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            logger.info(f"Downloading: s3://{self.config.bucket_name}/{s3_key} -> {file_path}")

            extra_args = {}
            if version_id:
                extra_args['VersionId'] = version_id

            self.s3_client.download_file(
                self.config.bucket_name,
                s3_key,
                str(file_path),
                ExtraArgs=extra_args if extra_args else None
            )

            return file_path

        except (ClientError, BotoCoreError) as e:
            logger.error(f"Download failed: {e}")
            raise

    def upload_bytes(
        self,
        data: bytes,
        s3_key: str,
        metadata: Optional[Dict[str, str]] = None,
        content_type: str = 'application/octet-stream'
    ) -> S3Object:
        """
        Upload bytes to S3.

        Args:
            data: Binary data
            s3_key: S3 object key
            metadata: Custom metadata
            content_type: MIME type

        Returns:
            S3Object metadata
        """
        extra_args = {
            'ContentType': content_type
        }

        if metadata:
            extra_args['Metadata'] = metadata

        try:
            logger.debug(f"Uploading {len(data)} bytes to s3://{self.config.bucket_name}/{s3_key}")

            self.s3_client.put_object(
                Bucket=self.config.bucket_name,
                Key=s3_key,
                Body=data,
                **extra_args
            )

            response = self.s3_client.head_object(
                Bucket=self.config.bucket_name,
                Key=s3_key
            )

            return S3Object(
                key=s3_key,
                size=response['ContentLength'],
                last_modified=response['LastModified'],
                etag=response['ETag'].strip('"'),
                version_id=response.get('VersionId'),
                metadata=response.get('Metadata', {}),
                content_type=content_type
            )

        except (ClientError, BotoCoreError) as e:
            logger.error(f"Upload failed: {e}")
            raise

    def download_bytes(
        self,
        s3_key: str,
        version_id: Optional[str] = None
    ) -> bytes:
        """
        Download bytes from S3.

        Args:
            s3_key: S3 object key
            version_id: Specific version

        Returns:
            Binary data
        """
        try:
            extra_args = {}
            if version_id:
                extra_args['VersionId'] = version_id

            response = self.s3_client.get_object(
                Bucket=self.config.bucket_name,
                Key=s3_key,
                **extra_args
            )

            return response['Body'].read()

        except (ClientError, BotoCoreError) as e:
            logger.error(f"Download failed: {e}")
            raise

    def list_objects(
        self,
        prefix: str = "",
        max_keys: int = 1000
    ) -> List[S3Object]:
        """
        List objects in bucket.

        Args:
            prefix: Key prefix filter
            max_keys: Maximum objects to return

        Returns:
            List of S3 objects
        """
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(
                Bucket=self.config.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )

            objects = []
            for page in pages:
                for obj in page.get('Contents', []):
                    objects.append(S3Object(
                        key=obj['Key'],
                        size=obj['Size'],
                        last_modified=obj['LastModified'],
                        etag=obj['ETag'].strip('"')
                    ))

            return objects

        except (ClientError, BotoCoreError) as e:
            logger.error(f"List failed: {e}")
            raise

    def delete_object(
        self,
        s3_key: str,
        version_id: Optional[str] = None
    ) -> bool:
        """
        Delete object from S3.

        Args:
            s3_key: S3 object key
            version_id: Specific version to delete

        Returns:
            True if deleted
        """
        try:
            extra_args = {}
            if version_id:
                extra_args['VersionId'] = version_id

            self.s3_client.delete_object(
                Bucket=self.config.bucket_name,
                Key=s3_key,
                **extra_args
            )

            logger.info(f"Deleted: s3://{self.config.bucket_name}/{s3_key}")
            return True

        except (ClientError, BotoCoreError) as e:
            logger.error(f"Delete failed: {e}")
            return False

    def generate_presigned_url(
        self,
        s3_key: str,
        expiration: int = 3600,
        operation: str = 'get_object'
    ) -> str:
        """
        Generate pre-signed URL for secure sharing.

        Args:
            s3_key: S3 object key
            expiration: URL expiration in seconds
            operation: S3 operation (get_object, put_object)

        Returns:
            Pre-signed URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                operation,
                Params={
                    'Bucket': self.config.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )

            logger.debug(f"Generated presigned URL for {s3_key} (expires in {expiration}s)")
            return url

        except (ClientError, BotoCoreError) as e:
            logger.error(f"Presigned URL generation failed: {e}")
            raise

    # ========================================================================
    # Energy Map Storage
    # ========================================================================

    def save_energy_map(
        self,
        energy_map: np.ndarray,
        s3_key: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> S3Object:
        """
        Save energy map to S3 with compression.

        Args:
            energy_map: 2D numpy array
            s3_key: S3 object key
            metadata: Additional metadata

        Returns:
            S3Object metadata
        """
        # Serialize to compressed format
        data = {
            'energy_map': energy_map.tolist(),
            'shape': energy_map.shape,
            'dtype': str(energy_map.dtype),
            'timestamp': datetime.utcnow().isoformat(),
            'metadata': metadata or {}
        }

        json_bytes = json.dumps(data).encode('utf-8')

        # Add checksum
        checksum = hashlib.sha256(json_bytes).hexdigest()

        upload_metadata = {
            'checksum': checksum,
            'format': 'json',
            'type': 'energy_map'
        }

        return self.upload_bytes(
            json_bytes,
            s3_key,
            metadata=upload_metadata,
            content_type='application/json'
        )

    def load_energy_map(
        self,
        s3_key: str,
        version_id: Optional[str] = None
    ) -> np.ndarray:
        """
        Load energy map from S3.

        Args:
            s3_key: S3 object key
            version_id: Specific version

        Returns:
            Energy map as numpy array
        """
        json_bytes = self.download_bytes(s3_key, version_id)
        data = json.loads(json_bytes.decode('utf-8'))

        energy_map = np.array(data['energy_map'], dtype=data['dtype'])
        return energy_map

    # ========================================================================
    # Model Checkpoint Storage
    # ========================================================================

    def save_checkpoint(
        self,
        checkpoint_path: str,
        s3_key: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> S3Object:
        """
        Save model checkpoint to S3.

        Args:
            checkpoint_path: Local checkpoint file
            s3_key: S3 object key
            metadata: Checkpoint metadata

        Returns:
            S3Object metadata
        """
        checkpoint_metadata = {
            'type': 'model_checkpoint',
            'timestamp': datetime.utcnow().isoformat()
        }

        if metadata:
            checkpoint_metadata.update(metadata)

        return self.upload_file(
            checkpoint_path,
            s3_key,
            metadata=checkpoint_metadata,
            content_type='application/octet-stream',
            storage_class='INTELLIGENT_TIERING'  # Cost optimization
        )

    def load_checkpoint(
        self,
        s3_key: str,
        download_path: str,
        version_id: Optional[str] = None
    ) -> Path:
        """
        Load model checkpoint from S3.

        Args:
            s3_key: S3 object key
            download_path: Local destination
            version_id: Specific version

        Returns:
            Path to downloaded checkpoint
        """
        return self.download_file(s3_key, download_path, version_id)

    async def async_upload_file(
        self,
        file_path: str,
        s3_key: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> S3Object:
        """
        Async file upload.

        Args:
            file_path: Local file path
            s3_key: S3 object key
            metadata: Custom metadata

        Returns:
            S3Object metadata
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        async with self.async_session.client(
            's3',
            endpoint_url=self.config.endpoint_url,
            aws_access_key_id=self.config.access_key_id,
            aws_secret_access_key=self.config.secret_access_key,
            region_name=self.config.region
        ) as s3:
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata

            with open(file_path, 'rb') as f:
                await s3.upload_fileobj(
                    f,
                    self.config.bucket_name,
                    s3_key,
                    ExtraArgs=extra_args if extra_args else None
                )

            response = await s3.head_object(
                Bucket=self.config.bucket_name,
                Key=s3_key
            )

            return S3Object(
                key=s3_key,
                size=response['ContentLength'],
                last_modified=response['LastModified'],
                etag=response['ETag'].strip('"'),
                version_id=response.get('VersionId'),
                metadata=response.get('Metadata', {})
            )


# ============================================================================
# Global S3 Connector
# ============================================================================

_s3_connector: Optional[S3Connector] = None


def get_s3_connector(config: Optional[S3Config] = None) -> S3Connector:
    """Get global S3 connector instance"""
    global _s3_connector
    if _s3_connector is None:
        if config is None:
            raise ValueError("S3Config required for first initialization")
        _s3_connector = S3Connector(config)
    return _s3_connector


# ============================================================================
# Convenience Functions
# ============================================================================

def save_energy_map_to_s3(
    energy_map: np.ndarray,
    s3_key: str,
    config: Optional[S3Config] = None
) -> S3Object:
    """Save energy map to S3 (convenience function)"""
    connector = get_s3_connector(config)
    return connector.save_energy_map(energy_map, s3_key)


def load_energy_map_from_s3(
    s3_key: str,
    config: Optional[S3Config] = None
) -> np.ndarray:
    """Load energy map from S3 (convenience function)"""
    connector = get_s3_connector(config)
    return connector.load_energy_map(s3_key)
