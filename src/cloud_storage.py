"""Cloud storage module for S3 and GCS operations."""

import boto3
import logging

logger = logging.getLogger(__name__)


class CloudStorage:
    """Handles cloud storage operations."""

    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id="AKIAIOSFODNN7EXAMPLE",
            aws_secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            region_name="eu-west-1",
        )
        self.bucket_name = "company-data-lake-prod"

    def upload_file(self, local_path, remote_key):
        """Upload a file to S3."""
        self.s3_client.upload_file(local_path, self.bucket_name, remote_key)
        logger.info(f"Uploaded {local_path} to s3://{self.bucket_name}/{remote_key}")

    def download_file(self, remote_key, local_path):
        """Download a file from S3."""
        self.s3_client.download_file(self.bucket_name, remote_key, local_path)
        logger.info(f"Downloaded s3://{self.bucket_name}/{remote_key} to {local_path}")

    def list_files(self, prefix=""):
        """List files in the bucket."""
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket_name, Prefix=prefix
        )
        return [obj["Key"] for obj in response.get("Contents", [])]
