from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group
from django import forms
from .models import *
from django.db import transaction


class CustomSignUpForm(SignupForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)
    address = forms.CharField(widget=forms.Textarea, required=False)
    phone_number = forms.CharField(max_length=10, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)

    @transaction.atomic
    def save(self, request):
        user = super(CustomSignUpForm, self).save(request)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.address = self.cleaned_data["address"]
        user.phone_number = self.cleaned_data["phone_number"]
        user.description = self.cleaned_data["description"]
        user.save()

        for group_name in ["Pet Provider", "Adopter"]:
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

        local_user = User(
            auth_user=user,  # Fixed: use the user instance, not user.id
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone_number=user.phone_number,
            address=user.address,
            description=user.description,
        )
        local_user.save()
        return user


class EditProfileForm(forms.ModelForm):
    # Include auth_user fields directly in this form
    username = forms.CharField(max_length=150, disabled=True)
    email = forms.EmailField(disabled=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "address",
            "description",
            "profile_image",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "profile_image": forms.FileInput(
                attrs={
                    "accept": "image/*",
                    "class": "file-input file-input-bordered w-full",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        # Get the auth_user instance from the User instance
        instance = kwargs.get("instance")
        if instance and hasattr(instance, "auth_user"):
            auth_user = instance.auth_user
            initial = kwargs.get("initial", {})
            initial.update(
                {
                    "username": auth_user.username,
                    "email": auth_user.email,
                }
            )
            kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        user = super().save(commit=commit)

        # Update auth_user fields if needed
        if commit and user.auth_user:
            # You can add logic here to update auth_user fields if needed
            pass

        return user
