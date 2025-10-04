# pets/forms.py
from django import forms
from .models import Pet, PetImage


class PetFilterForm(forms.Form):
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "input input-bordered input-sm",
            "placeholder": "Enter pet name..."
        })
    )

    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ("newest", "Sort by: Newest"),
            ("oldest", "Sort by: Oldest"),
            ("name_az", "Sort by: Name A-Z"),
            ("name_za", "Sort by: Name Z-A"),
            ("price_low_high", "Sort by: Price Low-High"),
            ("price_high_low", "Sort by: Price High-Low"),
        ],
        widget=forms.Select(
            attrs={"class": "select select-bordered select-sm"})
    )

    species = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            "id": "species",
            "class": "select select-bordered select-sm",
            "onchange": "toggleBreedSelect()"
        })
    )
    breed = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            "id": "breed",
            "class": "select select-bordered select-sm"
        })
    )

    gender = forms.ChoiceField(
        required=False,
        choices=[("", "Any"), ("Male", "Male"), ("Female", "Female")],
        widget=forms.RadioSelect(
            attrs={"class": "radio radio-primary radio-sm"})
    )

    # Range filters
    min_age = forms.IntegerField(required=False, min_value=0, widget=forms.NumberInput(attrs={
        "class": "input input-bordered input-sm", "placeholder": "Min"
    }))
    max_age = forms.IntegerField(required=False, min_value=0, widget=forms.NumberInput(attrs={
        "class": "input input-bordered input-sm", "placeholder": "Max"
    }))

    min_weight = forms.DecimalField(required=False, min_value=0, decimal_places=2, widget=forms.NumberInput(attrs={
        "class": "input input-bordered input-sm", "placeholder": "Min", "step": "0.1"
    }))
    max_weight = forms.DecimalField(required=False, min_value=0, decimal_places=2, widget=forms.NumberInput(attrs={
        "class": "input input-bordered input-sm", "placeholder": "Max", "step": "0.1"
    }))

    min_fee = forms.DecimalField(required=False, min_value=0, decimal_places=2, widget=forms.NumberInput(attrs={
        "class": "input input-bordered input-sm", "placeholder": "Min"
    }))
    max_fee = forms.DecimalField(required=False, min_value=0, decimal_places=2, widget=forms.NumberInput(attrs={
        "class": "input input-bordered input-sm", "placeholder": "Max"
    }))

    vaccinated = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={"class": "checkbox checkbox-primary checkbox-sm text-primary"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically populate species dropdown from DB
        species_qs = (
            Pet.objects.values_list("species", flat=True)
            .distinct()
            .order_by("species")
        )
        self.fields["species"].choices = [("", "All Species")] + [
            (s, s) for s in species_qs if s
        ]

        # Use initial request data to filter breeds
        species_selected = self.data.get(
            "species") or self.initial.get("species")
        if species_selected:
            breed_qs = (
                Pet.objects.filter(species=species_selected)
                .exclude(breed__isnull=True)
                .exclude(breed__exact="")
                .values_list("breed", flat=True)
                .distinct()
                .order_by("breed")
            )
            self.fields["breed"].choices = [("", "All Breeds")] + [
                (b, b) for b in breed_qs if b
            ]
        else:
            self.fields["breed"].choices = [("", "All Breeds")]


class RegisterPetForm(forms.ModelForm):
    GENDER_CHOICES = [
        ('', 'Select gender'),  # Empty string as value
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    # Override the gender field to add choices
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            "class": "select select-bordered select-primary",
        })
    )

    class Meta:
        model = Pet
        fields = [
            "name", "species", "breed", "color", "weight", "gender", "description", "adoption_fee", "dob"
        ]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "input input-bordered input-primary",
                "placeholder": "e.g., Buddy, Luna, Max",
                "required": True,
            }),
            "species": forms.TextInput(attrs={
                "class": "input input-bordered input-primary",
                "required": True,
                "placeholder": "e.g., Dog, Cat, Rabbit",
            }),
            "breed": forms.TextInput(attrs={
                "class": "input input-bordered input-primary",
                "placeholder": "e.g., Golden Retriever, Persian",
            }),
            "color": forms.TextInput(attrs={
                "class": "input input-bordered input-primary",
                "placeholder": "e.g., Brown, Black & White",
            }),
            "weight": forms.NumberInput(attrs={
                "class": "input input-bordered input-primary",
                "placeholder": "0.0",
                "step": "0.1",
                "min": "0",
            }),
            "adoption_fee": forms.NumberInput(attrs={
                "class": "input input-bordered input-primary",
                "placeholder": "0.00",
                "step": "0.01",
                "min": "0",
            }),
            "dob": forms.DateInput(attrs={
                "type": "date",
                "class": "input input-bordered input-primary",
            }),
            "description": forms.Textarea(attrs={
                "rows": 4,
                "class": "textarea textarea-bordered textarea-primary h-32 w-full",
                "placeholder": "Tell us about this pet's personality, habits, medical history, and any special needs...",
            }),
        }
        labels = {
            "name": "Pet Name *",
            "species": "Species *",
            "breed": "Breed",
            "color": "Color",
            "weight": "Weight (kg)",
            "gender": "Gender",
            "adoption_fee": "Adoption Fee ($)",
            "dob": "Date of Birth",
            "description": "Description",
        }
        help_texts = {
            "adoption_fee": "Leave empty or set to 0 if free adoption",
            "description": "Include personality traits, training status, health information, etc.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the empty_label lines since they don't work with ChoiceField

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.status:
            instance.status = Pet.PetStatus.AV  # enforce default
        if commit:
            instance.save()
        return instance


class PetImageForm(forms.ModelForm):
    class Meta:
        model = PetImage
        fields = ["pet_image"]
        widgets = {
            "pet_image": forms.FileInput(attrs={
                "accept": "image/*",
                "class": "file-input file-input-bordered file-input-primary w-full mt-2",
            }),
        }
        labels = {
            "pet_image": "Upload Pet Image",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make the image field required
        self.fields['pet_image'].required = True
