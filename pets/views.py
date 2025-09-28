from datetime import date, timedelta
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from .models import Pet
from .forms import PetFilterForm

class PetsView(View):
    def get(self, request):
        form = PetFilterForm(request.GET or None)

        filters_query = {}
        sort_by_value = None
        if form.is_valid():
            cd = form.cleaned_data
            if cd.get("name"):
                filters_query["name__icontains"] = cd["name"]
            if cd.get("species"):
                filters_query["species"] = cd["species"]
            if cd.get("breed"):
                filters_query["breed"] = cd["breed"]
            if cd.get("gender"):
                filters_query["gender"] = cd["gender"]

            # Range Filters
            if cd.get("min_weight") is not None:
                filters_query["weight__gte"] = cd["min_weight"]
            if cd.get("max_weight") is not None:
                filters_query["weight__lte"] = cd["max_weight"]

            if cd.get("min_fee") is not None:
                filters_query["adoption_fee__gte"] = cd["min_fee"]
            if cd.get("max_fee") is not None:
                filters_query["adoption_fee__lte"] = cd["max_fee"]
            
            if cd.get("min_age") is not None:
                min_dob = self.age_to_birthdate(cd["min_age"])
                if min_dob:
                    filters_query["dob__lte"] = min_dob  # older than min_age
            if cd.get("max_age") is not None:
                max_dob = self.age_to_birthdate(cd["max_age"])
                if max_dob:
                    filters_query["dob__gte"] = max_dob  # younger than max_age

            if cd.get("vaccinated"):
                filters_query["vaccines__isnull"] = False
            
            if cd.get("sort_by"):
                sort_by_value = cd.get("sort_by")

        ordering = self.get_ordering(sort_by_value)
        pets = Pet.objects.filter(**filters_query).order_by(ordering)

        return render(
            request,
            "pets/pets_explore.html",
            {"form": form, "pets": pets},
        )

    def get_ordering(self, sort_by):
        """Map sort_by param to Django ORM ordering value."""
        sorting_map = {
            "newest": "-created_at",
            "oldest": "created_at",
            "name_az": "name",
            "name_za": "-name",
            "price_low_high": "adoption_fee",
            "price_high_low": "-adoption_fee",
        }
        # Default ordering
        return sorting_map.get(sort_by, "-created_at")
    
    def age_to_birthdate(self, age):
        """Convert age in years into a date of birth approximation."""
        try:
            age = int(age)
            today = date.today()
            return today - timedelta(days=age * 365)
        except (TypeError, ValueError):
            return None


class PetDetailView(View):
    """View for displaying detailed information about a specific pet."""

    def get(self, request, pet_id):
        try:
            pet = Pet.objects.get(id=pet_id)
        except Pet.DoesNotExist:
            return render(request, "404.html", status=404)

        context = {
            "pet": pet,
        }
        return render(request, "pets/pet_detail.html", context)


def get_breeds(request):
    """Return distinct breeds for a given species, excluding null/empty values."""
    species = request.GET.get("species")

    breeds = []
    if species:
        breeds = (
            Pet.objects.filter(species=species)
            .exclude(breed__isnull=True)   # exclude NULL
            .exclude(breed__exact="")      # exclude empty string
            .values_list("breed", flat=True)
            .distinct()
            .order_by("breed")
        )

    return JsonResponse({"breeds": list(breeds)})
