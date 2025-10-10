from django.views import View
from django.shortcuts import render
from jaikae_project.utils import generate_presigned_url
from pets.models import Pet

class LandingPageView(View):
    def get(self, request):
        pets_qs = (
            Pet.objects.all()
            .select_related("image")
            .distinct()[:6]
        )

        pet_data = []
        for pet in pets_qs:
            image_url = None
            if getattr(pet, "image", None):
                image_url = generate_presigned_url(str(pet.image.pet_image))
            pet_data.append({
                "pet": pet,
                "image_url": image_url,
            })

        return render(request, "index.html", {"pets": pet_data})