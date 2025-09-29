import boto3
from django.conf import settings


def connect_minio_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name="us-east-1",
        use_ssl=False,
        verify=False,
        config=boto3.session.Config(signature_version="s3v4"),
    )


def generate_presigned_url(object_name, expiration=3600, http_method="GET"):
    try:
        s3_client = connect_minio_client()

        method_mapping = {
            "GET": "get_object",
            "PUT": "put_object",
            "POST": "post_object",  # For form uploads
            "DELETE": "delete_object",
        }

        if not s3_client:
            raise Exception("Could not connect to MinIO client")
        response = s3_client.generate_presigned_url(
            method_mapping[http_method],
            Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": object_name},
            ExpiresIn=expiration,
        )
        return response
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None
