from django.db import models
from pets.models import Pet
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class AdoptionApplication(models.Model):
    class ApplicationStatus(models.TextChoices):
        PE = "Pending"
        AP = "Approved"
        RE = "Rejected"
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=8, choices=ApplicationStatus.choices, default=ApplicationStatus.PE)
    notes = models.TextField(blank=True, null=True)
    requested_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Application by {self.user.username} for {self.pet.name}"