from django.db import models

# Create your models here.
class Vaccine(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    protects_against = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name