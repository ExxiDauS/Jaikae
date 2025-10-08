from django.shortcuts import render
from django.views import View
from .models import Vaccine

# Create your views here.
class VaccineListView(View):
    def get(self, request):
        vaccines = Vaccine.objects.all()
        return render(request, "vaccines/vaccines_list.html", {"vaccines": vaccines})

class AddVaccineView(View):
    def get(self, request):
        return render(request, "vaccines/add_vaccine.html")

    def post(self, request):
        name = request.POST.get("name")
        description = request.POST.get("description")
        if name:
            Vaccine.objects.create(name=name, description=description)
            return render(request, "vaccines/vaccines_list.html", {"vaccines": Vaccine.objects.all(), "success": "Vaccine added successfully!"})
        return render(request, "vaccines/add_vaccine.html", {"error": "Name is required."})
    
class EditVaccineView(View):
    def get(self, request, vaccine_id):
        try:
            vaccine = Vaccine.objects.get(id=vaccine_id)
        except Vaccine.DoesNotExist:
            return render(request, "404.html", status=404)
        return render(request, "vaccines/edit_vaccine.html", {"vaccine": vaccine})

    def post(self, request, vaccine_id):
        try:
            vaccine = Vaccine.objects.get(id=vaccine_id)
        except Vaccine.DoesNotExist:
            return render(request, "404.html", status=404)
        
        name = request.POST.get("name")
        description = request.POST.get("description")
        if name:
            vaccine.name = name
            vaccine.description = description
            vaccine.save()
            return render(request, "vaccines/vaccines_list.html", {"vaccines": Vaccine.objects.all(), "success": "Vaccine updated successfully!"})
        return render(request, "vaccines/edit_vaccine.html", {"vaccine": vaccine, "error": "Name is required."})

class DeleteVaccineView(View):
    def post(self, request, vaccine_id):
        try:
            vaccine = Vaccine.objects.get(id=vaccine_id)
            vaccine.delete()
            return render(request, "vaccines/vaccines_list.html", {"vaccines": Vaccine.objects.all(), "success": "Vaccine deleted successfully!"})
        except Vaccine.DoesNotExist:
            return render(request, "404.html", status=404)