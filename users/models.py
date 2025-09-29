# models.py
from django.db import models


def user_image_path(instance, filename):
    """Generate upload path for user profile images."""
    return f"profiles/{instance.auth_user.id}/{filename}"


class User(models.Model):
    auth_user = models.OneToOneField("auth.User", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(
        upload_to="profile_images/", blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.auth_user.username

    def username(self):
        return self.auth_user.username

    def get_profile_image_url(self):
        """Get profile image URL - automatically generates presigned URL with MinIO."""
        if self.profile_image:
            return self.profile_image.url
        return None
