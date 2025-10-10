from django.views import View
from django.shortcuts import render
from jaikae_project.utils import generate_presigned_url
from users.models import User
from pets.models import Pet

class LandingPageView(View):
    def get(self, request):
        current_user = User.objects.get(auth_user=request.user)

        pets_qs = (
            Pet.objects.all()
            .exclude(user=current_user)
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