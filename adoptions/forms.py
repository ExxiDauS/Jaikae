from django import forms
from .models import AdoptionApplication
from pets.models import Pet


class AdoptionApplicationForm(forms.ModelForm):
    class Meta:
        model = AdoptionApplication
        fields = ["pet", "notes", "requested_date"]

    def __init__(self, *args, pet_id=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["pet"].queryset = Pet.objects.filter(status="Available")

        if pet_id:
            self.fields["pet"].initial = pet_id
            self.fields["pet"].disabled = True
