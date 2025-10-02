from django.urls import path
from . import views

urlpatterns = [
    path("apply/", views.apply_for_adoption, name="apply_adoption"),
    path("apply/<int:pet_id>/", views.apply_for_adoption, name="apply_adoption_pet"),
    path("my-applications/", views.my_applications, name="my_applications"),
    path("manage/", views.manage_applications, name="manage_applications"),
    path("approve/<int:pk>/", views.approve_application, name="approve_application"),
    path("reject/<int:pk>/", views.reject_application, name="reject_application"),
    path(
        "application/<int:pk>/",
        views.adoption_application_detail,
        name="adoption_application_detail",
    ),
]
