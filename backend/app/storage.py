import os, io, uuid
import boto3
from botocore.client import Config

S3_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
S3_BUCKET   = os.getenv("MINIO_BUCKET", "adveritas")
S3_KEY      = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
S3_SECRET   = os.getenv("MINIO_SECRET_KEY", "minioadmin")
REGION      = os.getenv("AWS_REGION", "us-east-1")

_session = boto3.session.Session()
s3 = _session.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_KEY,
    aws_secret_access_key=S3_SECRET,
    config=Config(signature_version="s3v4"),
    region_name=REGION
)

def ensure_bucket():
    buckets = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
    if S3_BUCKET not in buckets:
        try:
            s3.create_bucket(Bucket=S3_BUCKET)
        except Exception:
            pass

def upload_bytes(key: str, data: bytes, content_type: str):
    ensure_bucket()
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=data, ContentType=content_type)
    return key

def upload_file(key: str, local_path: str, content_type: str="application/octet-stream"):
    ensure_bucket()
    s3.upload_file(local_path, S3_BUCKET, key, ExtraArgs={"ContentType": content_type})
    return key

def download_file(key: str, local_path: str):
    s3.download_file(S3_BUCKET, key, local_path)
    return local_path

def presign(key: str, expires=3600):
    return s3.generate_presigned_url(
        "get_object", Params={"Bucket": S3_BUCKET, "Key": key}, ExpiresIn=expires
    )
