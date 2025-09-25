from allauth.account.forms import SignupForm
from django import forms
from .models import *


class CustomSignUpForm(SignupForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)
    address = forms.CharField(widget=forms.Textarea, required=False)
    phone_number = forms.CharField(max_length=10, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)

    def save(self, request):
        user = super(CustomSignUpForm, self).save(request)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.address = self.cleaned_data["address"]
        user.phone_number = self.cleaned_data["phone_number"]
        user.description = self.cleaned_data["description"]
        local_user = User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone_number=user.phone_number,
            address=user.address,
            description=user.description,
        )
        local_user.save()
        user.save()
        return user

    # def __init__(self, *args, **kwargs):
    #     super(CustomSignUpForm, self).__init__(*args, **kwargs)
