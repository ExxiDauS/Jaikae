"""
URL configuration for jaikae_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.PetsView.as_view(), name="pets"),
    path("register/", views.RegisterPetView.as_view(), name="register_pet"),
    path("my-pets/", views.MyPetsView.as_view(), name="my_pets"),
    path("get-breeds/", views.get_breeds, name="get_breeds"),

    path("<int:pet_id>/", views.PetDetailView.as_view(), name="pet_detail"),
    path("<int:pet_id>/edit/", views.EditPetView.as_view(), name="edit_pet"),
    path("<int:pet_id>/delete/", views.DeletePetView.as_view(), name="delete_pet"),
    path("<int:pet_id>/download-pdf/", views.PetPDFView.as_view(), name="download_pet_pdf"),
]
