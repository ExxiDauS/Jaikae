from django.db import models
from vaccines.models import Vaccine
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Pet(models.Model):
    class PetGender(models.TextChoices):
        MA = "Male"
        FE = "Female"
    class PetStatus(models.TextChoices):
        AV = "Available"
        PE = "Pending"
        AD = "Adopted"
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vaccines = models.ManyToManyField(Vaccine, blank=True)
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=100)
    breed = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    gender = models.CharField(max_length=15, choices=PetGender.choices, blank=True, null=True)
    status = models.CharField(max_length=15, choices=PetStatus.choices, default=PetStatus.AV)
    description = models.TextField(blank=True, null=True)
    adoption_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    dob = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} {self.species} {self.breed or ''} {self.color or ''}".strip()

class PetImage(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='images')
    image_unsigned_url = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)