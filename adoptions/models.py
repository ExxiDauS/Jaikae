from django.db import models
from pets.models import Pet
from users.models import User


class AdoptionApplication(models.Model):
    class ApplicationStatus(models.TextChoices):
        PE = "Pending"
        AP = "Approved"
        RE = "Rejected"

    class HousingType(models.TextChoices):
        HOUSE = "House", "House"
        APARTMENT = "Apartment", "Apartment"
        CONDO = "Condo", "Condo"
        OTHER = "Other", "Other"

    class HomeOwnership(models.TextChoices):
        OWN = "Own", "Own"
        RENT = "Rent", "Rent"

    # Basic Information
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=8,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PE,
    )
    notes = models.TextField(
        blank=True,
        null=True,
    )
    requested_date = models.DateField(blank=True, null=True)

    # Living Situation
    housing_type = models.CharField(
        max_length=20, choices=HousingType.choices, default=HousingType.HOUSE
    )
    home_ownership = models.CharField(
        max_length=10,
        choices=HomeOwnership.choices,
        default=HomeOwnership.OWN,
    )

    # Pet Experience
    has_other_pets = models.BooleanField(default=False)
    other_pets_details = models.TextField(
        blank=True,
        null=True,
    )

    work_schedule = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Application by {self.user.username} for {self.pet.name}"
