from django import forms
from .models import AdoptionApplication
from pets.models import Pet


class AdoptionApplicationForm(forms.ModelForm):
    class Meta:
        model = AdoptionApplication
        fields = [
            "pet",
            "notes",
            "requested_date",
            "housing_type",
            "home_ownership",
            "has_other_pets",
            "other_pets_details",
            "work_schedule",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
            "other_pets_details": forms.Textarea(attrs={"rows": 3}),
            "requested_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, pet_id=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["pet"].queryset = Pet.objects.filter(status="Available")

        if pet_id:
            self.fields["pet"].initial = pet_id
            self.fields["pet"].disabled = True

        # Make certain fields required
        self.fields["notes"].required = True
        self.fields["housing_type"].required = True
        self.fields["home_ownership"].required = True
