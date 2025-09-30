from datetime import date
from django.db import models
from vaccines.models import Vaccine
from users.models import User
# from django.contrib.auth import get_user_model

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
    
    @property # make it accessible as pet.age not pet.age(), using method as attribute-like
    def age(self):
        """Return the pet's age as a tuple (years, months)."""
        if not self.dob:
            return None
        today = date.today()
        years = today.year - self.dob.year
        months = today.month - self.dob.month
        if today.day < self.dob.day:
            months -= 1
        if months < 0:
            years -= 1
            months += 12
        return years, months

class PetImage(models.Model):
    pet = models.OneToOneField(Pet, on_delete=models.CASCADE, related_name='image')
    pet_image = models.ImageField(upload_to='pet_images/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)