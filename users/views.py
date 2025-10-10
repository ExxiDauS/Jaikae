# views.py
from django.shortcuts import redirect, render
from django.contrib import messages
from users.forms import EditProfileForm
from users.models import User
from jaikae_project.utils import generate_presigned_url


def home(request):
    return render(request, "index.html")

def profile(request):
    if not request.user.is_authenticated:
        return redirect("account_login")

    # Get the User profile
    user_profile = User.objects.get(auth_user=request.user)

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            user = form.save()
            print(user.profile_image)
            return redirect("profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = EditProfileForm(instance=user_profile)
    presigned_url = generate_presigned_url(user_profile.profile_image.name)
    return render(
        request,
        "profile.html",
        {"form": form, "user_profile": user_profile, "presigned_url": presigned_url},
    )
