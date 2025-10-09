from django.shortcuts import render
from django.views import View
from .models import Vaccine
from .forms import VaccineForm

# Create your views here.
class VaccineListView(View):
    def get(self, request):
        vaccines = Vaccine.objects.all()
        return render(request, "vaccines/vaccines_list.html", {"vaccines": vaccines})

class AddVaccineView(View):
    def get(self, request):
        form = VaccineForm()
        return render(request, "vaccines/add_vaccine.html", {"form": form})

    def post(self, request):
        form = VaccineForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "vaccines/vaccines_list.html", {"vaccines": Vaccine.objects.all()})
        return render(request, "vaccines/add_vaccine.html", {"form": form})
    
class EditVaccineView(View):
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
            form.save()
            return render(request, "vaccines/vaccines_list.html", {"vaccines": Vaccine.objects.all()})
        return render(request, "vaccines/edit_vaccine.html", {"form": form})

class DeleteVaccineView(View):
    def post(self, request, vaccine_id):
        try:
            vaccine = Vaccine.objects.get(id=vaccine_id)
            vaccine.delete()
            return render(request, "vaccines/vaccines_list.html", {"vaccines": Vaccine.objects.all(), "success": "Vaccine deleted successfully!"})
        except Vaccine.DoesNotExist:
            return render(request, "404.html", status=404)