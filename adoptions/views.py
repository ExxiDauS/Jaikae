from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AdoptionApplication
from .forms import AdoptionApplicationForm
from pets.models import Pet
from users.models import User


@login_required
def apply_for_adoption(request, pet_id=None):
    pet = None
    if pet_id:
        pet = get_object_or_404(Pet, id=pet_id, status="Available")

    if request.method == "POST":
        form = AdoptionApplicationForm(request.POST, pet_id=pet_id)

        if form.is_valid():
            application = form.save(commit=False)
            custom_user = User.objects.get(id=request.user.id)
            application.user = custom_user

            # Check duplicate
            if AdoptionApplication.objects.filter(
                user=custom_user, pet=application.pet, status="Pending"
            ).exists():
                messages.warning(
                    request, "You already have a pending application for this pet."
                )
                return redirect("my_applications")

            application.save()
            messages.success(request, "Application submitted successfully!")
            return redirect("my_applications")
    else:
        form = AdoptionApplicationForm(pet_id=pet_id)

    return render(
        request,
        "adoptions/apply.html",
        {
            "form": form,
            "pet": pet,
        },
    )


@login_required
def my_applications(request):
    custom_user = User.objects.get(id=request.user.id)
    applications = (
        AdoptionApplication.objects.filter(user=custom_user)
        .select_related("pet")
        .order_by("-created_at")
    )

    return render(
        request,
        "adoptions/my_applications.html",
        {
            "applications": applications,
        },
    )


@login_required
def manage_applications(request):
    custom_user = User.objects.get(id=request.user.id)
    my_pet = Pet.objects.filter(user=custom_user)
    my_applications = AdoptionApplication.objects.filter(pet__in=my_pet)
    print(request.user.id, custom_user.first_name)

    return render(
        request,
        "adoptions/manage_applications.html",
        {
            "applications": my_applications,
        },
    )


@login_required
def approve_application(request, pk):
    application = get_object_or_404(AdoptionApplication, id=pk, pet__owner=request.user)

    if request.method == "POST":
        from django.utils import timezone

        application.status = "Approved"
        application.approved_date = timezone.now().date()
        application.save()

        # Update pet status
        application.pet.status = "Adopted"
        application.pet.save()

        # Reject other pending applications for this pet
        AdoptionApplication.objects.filter(
            pet=application.pet, status="Pending"
        ).exclude(id=application.id).update(status="Rejected")

        messages.success(request, "Application approved!")
        return redirect("manage_applications")

    return render(
        request,
        "adoptions/confirm_approve.html",
        {
            "application": application,
        },
    )


@login_required
def reject_application(request, pk):
    application = get_object_or_404(AdoptionApplication, id=pk, pet__owner=request.user)

    if request.method == "POST":
        application.status = "Rejected"
        application.save()

        messages.info(request, "Application rejected.")
        return redirect("manage_applications")

    return render(
        request,
        "adoptions/confirm_reject.html",
        {
            "application": application,
        },
    )


@login_required
def adoption_application_detail(request, pk):
    custom_user = User.objects.get(id=request.user.id)
    application = get_object_or_404(AdoptionApplication, id=pk, user=custom_user)

    context = {
        "application": application,
    }
    return render(request, "adoptions/application_detail.html", context)
