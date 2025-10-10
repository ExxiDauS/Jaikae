from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from xhtml2pdf import pisa
import io

from .models import AdoptionApplication
from .forms import AdoptionApplicationForm
from pets.models import Pet
from users.models import User
from jaikae_project.utils import send_application_status_email


@login_required
def apply_for_adoption(request, pet_id=None):
    pet = None
    if pet_id:
        pet = get_object_or_404(Pet, id=pet_id, status="Available")

    if request.method == "POST":
        form = AdoptionApplicationForm(request.POST, pet_id=pet_id)

        if form.is_valid():
            application = form.save(commit=False)
            custom_user = User.objects.get(auth_user=request.user.id)
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
    custom_user = User.objects.get(auth_user=request.user.id)
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
    custom_user = User.objects.get(auth_user=request.user.id)
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
    application = AdoptionApplication.objects.get(id=pk)

    if request.method == "POST":
        from django.utils import timezone

        application.status = "Approved"
        application.approved_date = timezone.now().date()
        application.save()

        # Update pet status
        application.pet.status = "Adopted"
        application.pet.save()

        if send_application_status_email(application, request):
            messages.success(
                request,
                f"Application approved and email sent to {application.user.email}",
            )
        else:
            messages.warning(request, "Application approved but email failed to send.")

        # Reject other pending applications for this pet
        other_applications = AdoptionApplication.objects.filter(
            pet=application.pet, status="Pending"
        ).exclude(id=application.id)

        # Reject and send emails to other applicants
        rejected_count = 0
        email_sent_count = 0
        email_failed_count = 0

        for other_app in other_applications:
            other_app.status = "Rejected"
            other_app.save()
            rejected_count += 1

            # Send rejection email
            if send_application_status_email(other_app, request):
                email_sent_count += 1
            else:
                email_failed_count += 1

        # Show summary message
        if rejected_count > 0:
            messages.info(
                request,
                f"{rejected_count} other application(s) automatically rejected. "
                f"Emails sent: {email_sent_count}, Failed: {email_failed_count}",
            )

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

    if send_application_status_email(application, request):
        messages.success(
            request, f"Application rejected and email sent to {application.user.email}"
        )
    else:
        messages.warning(request, "Application rejected but email failed to send.")

    return render(
        request,
        "adoptions/confirm_reject.html",
        {
            "application": application,
        },
    )


@login_required
def adoption_application_detail(request, pk):
    custom_user = User.objects.get(auth_user=request.user.id)
    application = get_object_or_404(AdoptionApplication, id=pk, user=custom_user)

    context = {
        "application": application,
    }
    return render(request, "adoptions/application_detail.html", context)


@login_required
def download_application_pdf(request, pk):
    custom_user = User.objects.get(auth_user=request.user.id)
    application = get_object_or_404(AdoptionApplication, id=pk, user=custom_user)

    # Render HTML template with context
    html_string = render_to_string(
        "adoptions/application_pdf.html",
        {
            "application": application,
            "now": timezone.now(),
        },
    )

    # Create PDF
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html_string.encode("UTF-8")), result)

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type="application/pdf")
        filename = f"application_{application.pet.name}_{application.id}.pdf"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    return HttpResponse("Error generating PDF", status=400)
