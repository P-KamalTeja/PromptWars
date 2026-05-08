"""Google Cloud Storage service integration."""
import os
from typing import Optional, List
from google.cloud import storage

from src.core import Config, get_logger, GoogleServicesError

logger = get_logger(__name__)


class StorageService:
    """Handles Google Cloud Storage operations."""

    def __init__(self, config: Config):
        """Initialize storage service.

        Args:
            config: Application configuration
        """
        self.config = config
        self.client = None
        self.bucket_name = os.getenv("GCS_BUCKET_NAME")
        self._initialize_client()

    def _initialize_client(self):
        """Initialize GCS client."""
        try:
            if self.config.GOOGLE_CLOUD_PROJECT:
                self.client = storage.Client(project=self.config.GOOGLE_CLOUD_PROJECT)
            else:
                self.client = storage.Client()
            logger.info("GCS client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GCS client: {str(e)}")
            # Don't raise here, allow lazy initialization or check in methods
            self.client = None

    def upload_file(
        self, local_path: str, remote_path: str, content_type: Optional[str] = None
    ) -> str:
        """Upload a file to GCS.

        Args:
            local_path: Path to local file
            remote_path: Path in GCS bucket
            content_type: MIME type of the file

        Returns:
            Public URL or GCS URI

        Raises:
            GoogleServicesError: If upload fails
        """
        if not self.client or not self.bucket_name:
            raise GoogleServicesError(
                "GCS client or bucket not configured",
                service="Storage",
            )

        try:
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(remote_path)
            blob.upload_from_filename(local_path, content_type=content_type)
            
            logger.info(
                "Successfully uploaded %s to gs://%s/%s",
                local_path,
                self.bucket_name,
                remote_path,
            )
            return f"https://storage.googleapis.com/{self.bucket_name}/{remote_path}"
        except Exception as e:
            logger.error(f"GCS upload failed: {str(e)}")
            raise GoogleServicesError(
                f"Failed to upload to GCS: {str(e)}",
                service="Storage",
            )

    def download_file(self, remote_path: str, local_path: str):
        """Download a file from GCS.

        Args:
            remote_path: Path in GCS bucket
            local_path: Path to save locally

        Raises:
            GoogleServicesError: If download fails
        """
        if not self.client or not self.bucket_name:
            raise GoogleServicesError(
                "GCS client or bucket not configured",
                service="Storage",
            )

        try:
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(remote_path)
            blob.download_to_filename(local_path)
            logger.info(
                "Successfully downloaded gs://%s/%s to %s",
                self.bucket_name,
                remote_path,
                local_path,
            )
        except Exception as e:
            logger.error(f"GCS download failed: {str(e)}")
            raise GoogleServicesError(
                f"Failed to download from GCS: {str(e)}",
                service="Storage",
            )

    def list_files(self, prefix: Optional[str] = None) -> List[str]:
        """List files in the bucket.

        Args:
            prefix: Prefix to filter files

        Returns:
            List of file paths
        """
        if not self.client or not self.bucket_name:
            return []

        try:
            bucket = self.client.bucket(self.bucket_name)
            blobs = bucket.list_blobs(prefix=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            logger.error(f"GCS list failed: {str(e)}")
            return []

    def delete_file(self, remote_path: str):
        """Delete a file from GCS.

        Args:
            remote_path: Path in GCS bucket
        """
        if not self.client or not self.bucket_name:
            return

        try:
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(remote_path)
            blob.delete()
            logger.info(f"Deleted gs://{self.bucket_name}/{remote_path}")
        except Exception as e:
            logger.error(f"GCS delete failed: {str(e)}")
