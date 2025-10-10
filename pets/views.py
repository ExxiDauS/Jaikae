from datetime import date, timedelta
from django.shortcuts import redirect, render
from django.views import View
from django.http import HttpResponse, JsonResponse
from .models import Pet
from .forms import PetFilterForm, RegisterPetForm, PetImageForm
from django.db import transaction
from users.models import User
from jaikae_project.utils import generate_presigned_url
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import io


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
        current_user = User.objects.get(auth_user=request.user)

        pets_qs = (
            Pet.objects.filter(**filters_query)
            .exclude(user=current_user)
            .select_related("image")
            .order_by(ordering)
            .distinct()
        )

        paginator = Paginator(pets_qs, 6)  # 6 pets per page (adjust as needed)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        # Attach presigned URLs only for this page’s pets
        pet_data = []
        for pet in page_obj:
            image_url = None
            if getattr(pet, "image", None):
                image_url = generate_presigned_url(str(pet.image.pet_image))
            pet_data.append({
                "pet": pet,
                "image_url": image_url,
            })

        querydict = request.GET.copy()
        if "page" in querydict:
            querydict.pop("page")  # drop any old page query
        filters_querystring = querydict.urlencode()

        return render(
            request,
            "pets/pets_explore.html",
            {
                "form": form,
                "pets": pet_data,
                "page_obj": page_obj,
                "filters_querystring": filters_querystring,
            },
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
            image_url = None
            if getattr(pet, "image", None):
                image_url = generate_presigned_url(str(pet.image.pet_image))
            current_user = User.objects.get(auth_user=request.user)
        except Pet.DoesNotExist:
            return render(request, "404.html", status=404)

        context = {
            "pet": pet,
            "image_url": image_url,
            "current_user": current_user,
        }
        return render(request, "pets/pet_detail.html", context)


class RegisterPetView(View):
    """View for registering a new pet."""

    def get(self, request):
        pet_form = RegisterPetForm()
        image_form = PetImageForm()
        return render(
            request,
            "pets/register_pet.html",
            {"pet_form": pet_form, "image_form": image_form},
        )

    def post(self, request):
        pet_form = RegisterPetForm(request.POST)
        image_form = PetImageForm(request.POST, request.FILES)

        if pet_form.is_valid() and image_form.is_valid():
            with transaction.atomic():
                # Get current user's profile
                user_profile = User.objects.get(auth_user=request.user)

                # Save Pet but don’t commit yet
                pet = pet_form.save(commit=False)
                pet.user = user_profile   # attach user
                pet.save()

                pet_form.save_m2m()

                # Save image and link to pet
                pet_image = image_form.save(commit=False)
                pet_image.pet = pet
                pet_image.save()

            return redirect("my_pets")

        # If invalid, re-render with errors
        return render(
            request,
            "pets/register_pet.html",
            {"pet_form": pet_form, "image_form": image_form},
        )


class MyPetsView(View):
    """View for displaying the current user's registered pets."""

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("account_login")

        user_profile = User.objects.get(auth_user=request.user)
        pets_qs = Pet.objects.filter(user=user_profile).select_related(
            "image").order_by("-created_at")

        paginator = Paginator(pets_qs, 6)  # 6 pets per page (adjust as needed)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        # Attach presigned URLs only for this page’s pets
        pet_data = []
        for pet in page_obj:
            image_url = None
            if getattr(pet, "image", None):
                image_url = generate_presigned_url(str(pet.image.pet_image))
            pet_data.append({
                "pet": pet,
                "image_url": image_url,
            })

        querydict = request.GET.copy()
        if "page" in querydict:
            querydict.pop("page")  # drop any old page query
        filters_querystring = querydict.urlencode()

        return render(
            request,
            "pets/my_pets.html",
            {"pets": pet_data,
             "page_obj": page_obj,
             "filters_querystring": filters_querystring, },
        )


class EditPetView(View):
    """View for editing an existing pet's details."""

    def get(self, request, pet_id):
        if not request.user.is_authenticated:
            return redirect("account_login")

        try:
            pet = Pet.objects.get(id=pet_id, user__auth_user=request.user)
        except Pet.DoesNotExist:
            return render(request, "404.html", status=404)

        pet_form = RegisterPetForm(instance=pet)
        image_form = PetImageForm(instance=getattr(pet, "image", None))

        image_url = None
        if getattr(pet, "image", None):
            image_url = generate_presigned_url(str(pet.image.pet_image))

        return render(
            request,
            "pets/edit_pet.html",
            {
                "pet_form": pet_form,
                "image_form": image_form,
                "pet": pet,
                "image_url": image_url
            },
        )

    def post(self, request, pet_id):
        if not request.user.is_authenticated:
            return redirect("account_login")

        try:
            pet = Pet.objects.get(id=pet_id, user__auth_user=request.user)
        except Pet.DoesNotExist:
            return render(request, "404.html", status=404)

        pet_form = RegisterPetForm(request.POST, instance=pet)
        image_form = PetImageForm(
            request.POST, request.FILES, instance=getattr(pet, "image", None))

        if pet_form.is_valid() and image_form.is_valid():
            print(pet_form.cleaned_data)
            with transaction.atomic():
                pet_form.save()
                image_form.save()

            return redirect("my_pets")

        # Generate image_url for error case too
        image_url = None
        if getattr(pet, "image", None):
            image_url = generate_presigned_url(str(pet.image.pet_image))

        return render(
            request,
            "pets/edit_pet.html",
            {
                "pet_form": pet_form,
                "image_form": image_form,
                "pet": pet,
                "image_url": image_url
            },
        )


class DeletePetView(View):
    """View for deleting an existing pet."""

    def post(self, request, pet_id):
        if not request.user.is_authenticated:
            return redirect("account_login")

        try:
            pet = Pet.objects.get(id=pet_id, user__auth_user=request.user)
        except Pet.DoesNotExist:
            return render(request, "404.html", status=404)

        if getattr(pet, "status", None) == "Pending":
            return redirect("my_pets")

        with transaction.atomic():
            pet.delete()
        return redirect("my_pets")


class PetPDFView(View):
    """View for downloading pet details as a PDF."""

    def get(self, request, pet_id):
        if not request.user.is_authenticated:
            return redirect("account_login")

        try:
            pet = Pet.objects.get(id=pet_id)
        except Pet.DoesNotExist:
            return render(request, "404.html", status=404)

        # Render pet details to HTML
        html_string = render_to_string(
            'pets/pet_pdf.html', {'pet': pet, "now": date.today()})

        # Convert HTML to PDF
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(
            html_string.encode("UTF-8")), result)

        if not pdf.err:
            respone = HttpResponse(
                result.getvalue(), content_type='application/pdf')
            file_name = f"{pet.name}_details.pdf"
            respone['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return respone

        return HttpResponse("Error generating PDF", status=500)


def get_breeds(request):
    """Return distinct breeds for a given species, excluding null/empty values."""
    species = request.GET.get("species")

    breeds = []
    if species:
        current_user = User.objects.get(auth_user=request.user)
        breeds = (
            Pet.objects.filter(species=species)
            .exclude(breed__isnull=True)   # exclude NULL
            .exclude(breed__exact="")      # exclude empty string
            .exclude(user=current_user)  # exclude current user's pets
            .values_list("breed", flat=True)  # get list of breed values
            .distinct()
            .order_by("breed")
        )

    return JsonResponse({"breeds": list(breeds)})
