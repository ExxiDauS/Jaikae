from django.shortcuts import redirect, render
from django.views import View
from .models import Vaccine
from .forms import VaccineForm
from django.db import transaction
from django.contrib.auth.mixins import PermissionRequiredMixin

# Create your views here.
class VaccineListView(PermissionRequiredMixin, View):
    permission_required = ["vaccines.view_vaccine"]

    def get(self, request):
        vaccines = Vaccine.objects.all()
        return render(request, "vaccines/vaccines_list.html", {"vaccines": vaccines})

class AddVaccineView(PermissionRequiredMixin, View):
    permission_required = ["vaccines.add_vaccine"]

    def get(self, request):
        form = VaccineForm()
        return render(request, "vaccines/add_vaccine.html", {"form": form})

    def post(self, request):
        form = VaccineForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            return render(request, "vaccines/vaccines_list.html", {"vaccines": Vaccine.objects.all()})
        return render(request, "vaccines/add_vaccine.html", {"form": form})

class EditVaccineView(PermissionRequiredMixin, View):
    permission_required = ["vaccines.change_vaccine"]

    def get(self, request, vaccine_id):
        try:
            vaccine = Vaccine.objects.get(id=vaccine_id)
        except Vaccine.DoesNotExist:
            return render(request, "404.html", status=404)
        form = VaccineForm(instance=vaccine)
        return render(request, "vaccines/edit_vaccine.html", {"form": form})

    def post(self, request, vaccine_id):
        try:
            vaccine = Vaccine.objects.get(id=vaccine_id)
        except Vaccine.DoesNotExist:
            return render(request, "404.html", status=404)

        form = VaccineForm(request.POST, instance=vaccine)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            return render(request, "vaccines/vaccines_list.html", {"vaccines": Vaccine.objects.all()})
        return render(request, "vaccines/edit_vaccine.html", {"form": form})

class DeleteVaccineView(PermissionRequiredMixin, View):
    permission_required = ["vaccines.delete_vaccine"]

    def get(self, request, vaccine_id):
        return redirect("vaccines_list")
    
    def post(self, request, vaccine_id):
        try:
            vaccine = Vaccine.objects.get(id=vaccine_id)
            with transaction.atomic():
                vaccine.delete()
            return render(request, "vaccines/vaccines_list.html", {"vaccines": Vaccine.objects.all()})
        except Vaccine.DoesNotExist:
            return render(request, "404.html", status=404)