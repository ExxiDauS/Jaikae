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
    path('', views.VaccineListView.as_view(), name='vaccines'),
    path('add/', views.AddVaccineView.as_view(), name='add_vaccine'),
    path('edit/<int:vaccine_id>/', views.EditVaccineView.as_view(), name='edit_vaccine'),
    path('delete/<int:vaccine_id>/', views.DeleteVaccineView.as_view(), name='delete_vaccine'),
]
