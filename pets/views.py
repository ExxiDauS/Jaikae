from django.shortcuts import render
from django.views import View
from .models import Pet, PetImage

# Create your views here.


class PetsView(View):
    def get(self, request):
        filters = {}
        name = request.GET.get("name")
        if name:  # Only when user typed something
            filters["name__icontains"] = name

        species = request.GET.get("species")
        if species:
            filters["species"] = species

        gender = request.GET.get("gender")
        if gender:
            filters["gender"] = gender

        min_age = request.GET.get("min_age")
        max_age = request.GET.get("max_age")
        if min_age:
            filters["age__gte"] = min_age
        if max_age:
            filters["age__lte"] = max_age

        min_weight = request.GET.get("min_weight")
        max_weight = request.GET.get("max_weight")
        if min_weight:
            filters["weight__gte"] = min_weight
        if max_weight:
            filters["weight__lte"] = max_weight
        
        min_fee = request.GET.get("min_fee")
        max_fee = request.GET.get("max_fee")
        if min_fee:
            filters["adoption_fee__gte"] = min_fee
        if max_fee:
            filters["adoption_fee__lte"] = max_fee

        vaccinated = request.GET.get("vaccinated")
        if vaccinated == "vaccinated":
            filters["vaccinated"] = True
        else:
            filters["vaccinated"] = False

        sort_by = request.GET.get("sort_by")
        if sort_by == "newest":
            ordering = "-created_at"
        elif sort_by == "oldest":
            ordering = "created_at"
        elif sort_by == "name_az":
            ordering = "name"
        elif sort_by == "name_za":
            ordering = "-name"
        elif sort_by == "price_low_high":
            ordering = "adoption_fee"
        elif sort_by == "price_high_low":
            ordering = "-adoption_fee"
        else:
            ordering = "-created_at"  # Default ordering
        
        for (key, value) in filters.items():
            print(f"{key}: {value}")

        print(f"Ordering by: {sort_by}")
        return render(request, "pets/pets_explore.html", {"filters": filters, "sort_by": sort_by})
