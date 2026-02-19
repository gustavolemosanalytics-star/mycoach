"""
File Service — Upload/download de arquivos para S3/R2/Railway Object Storage.
"""
import uuid
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings


def _get_s3_client():
    if not settings.S3_ENDPOINT_URL or not settings.S3_ACCESS_KEY:
        return None

    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
    )


async def upload_file(file_bytes: bytes, key: str) -> str:
    """Upload file to S3. Returns the key."""
    client = _get_s3_client()
    if client is None:
        # Local fallback: save to disk
        import os
        local_dir = "/tmp/mycoach-files"
        os.makedirs(local_dir, exist_ok=True)
        path = os.path.join(local_dir, key.replace("/", "_"))
        with open(path, "wb") as f:
            f.write(file_bytes)
        return key

    client.put_object(
        Bucket=settings.S3_BUCKET_NAME,
        Key=key,
        Body=file_bytes,
    )
    return key


def generate_file_key(user_id: str, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "fit"
    return f"activities/{user_id}/{uuid.uuid4()}.{ext}"
