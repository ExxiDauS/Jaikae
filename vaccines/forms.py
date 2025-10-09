from django import forms

from vaccines.models import Vaccine

class VaccineForm(forms.ModelForm):
    class Meta:
        model = Vaccine
        fields = ['name', 'description', 'protects_against']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'description': forms.Textarea(attrs={'class': 'input input-bordered w-full resize-none h-48 pt-2'}),
            'protects_against': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
        }
        labels = {
            'name': 'Vaccine Name',
            'description': 'Description',
            'protects_against': 'Protects Against',
        }