from datetime import date, timedelta
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from .models import Pet


class PetsView(View):
    """View for displaying and filtering pets."""

    def get(self, request):
        # Parse filters
        filters_query, filters_template = self.build_filters(request)

        # Determine sorting
        ordering = self.get_ordering(request.GET.get("sort_by"))

        print("Filters Query:", filters_query)

        # Query pets with filters + sorting
        pets = Pet.objects.filter(**filters_query).order_by(ordering)

        # Populate species dropdown filter
        species_options = (
            Pet.objects.values_list("species", flat=True)
            .distinct()
            .order_by("species")
        )

        context = {
            "filters": filters_template,
            "sort_by": request.GET.get("sort_by"),
            "species_options": species_options,
            "pets": pets,
        }

        return render(request, "pets/pets_explore.html", context)

    # -------------------------------
    # Helpers
    # -------------------------------

    def build_filters(self, request):
        """Build filters from request GET params."""
        filters_query = {}
        filters_template = {}

        # Simple text/choice filters
        simple_fields = ["name", "species", "breed", "gender"]
        for field in simple_fields:
            value = request.GET.get(field)
            if value:
                query_field = (
                    f"{field}__icontains" if field == "name" else field
                )
                filters_query[query_field] = value
                filters_template[field] = value

        # Age filters (convert to dob range)
        min_age = request.GET.get("min_age")
        max_age = request.GET.get("max_age")

        if min_age:
            filters_query["dob__lte"] = (
                self.age_to_birthdate(max_age)
                if max_age
                else self.age_to_birthdate(min_age)
            )
            filters_template["min_age"] = min_age

        if max_age:
            filters_query["dob__gte"] = (
                self.age_to_birthdate(min_age)
                if min_age
                else self.age_to_birthdate(max_age)
            )
            filters_template["max_age"] = max_age

        # Numeric range filters
        self.add_range_filter(
            request, "weight", filters_query, filters_template
        )
        self.add_range_filter(
            request, "adoption_fee", filters_query, filters_template, "fee"
        )

        return filters_query, filters_template

    def add_range_filter(
        self, request, field, filters_query, filters_template, template_key=None
    ):
        """Helper to handle min/max filters for numeric fields."""
        template_key = template_key or field

        min_val = request.GET.get(f"min_{template_key}")
        max_val = request.GET.get(f"max_{template_key}")

        if min_val:
            filters_query[f"{field}__gte"] = min_val
            filters_template[f"min_{template_key}"] = min_val
        if max_val:
            filters_query[f"{field}__lte"] = max_val
            filters_template[f"max_{template_key}"] = max_val

    def age_to_birthdate(self, age):
        """Convert age in years into a date of birth approximation."""
        try:
            age = int(age)
            today = date.today()
            return today - timedelta(days=age * 365)
        except (TypeError, ValueError):
            return None

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
