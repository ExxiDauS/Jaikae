import boto3
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site


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


def send_application_status_email(application, request=None):
    user = application.user
    status = application.status
    site_url = (
        f"{request.scheme}://{get_current_site(request).domain}"
        if request
        else ("https://exxidaus.ucnil.dev/")
    )
    context = {
        "application": application,
        "status": status,
        "site_url": site_url,
        "contact_email": settings.DEFAULT_FROM_EMAIL,
    }
    subject = f"Adoption Application {status} - {application.pet.name}"
    html_content = render_to_string("emails/application_status.html", context)
    email = EmailMessage(
        subject=subject,
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.content_subtype = "html"

    # Send email
    try:
        email.send()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
