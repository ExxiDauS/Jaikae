from django.shortcuts import render
from django.views import View
from .models import Pet, PetImage

# Create your views here.
class PetsView(View):
    def get(self, request):
        gender = request.GET.get("gender")
        print("gender:", gender)
        return render(request, "pets/pets_explore.html")