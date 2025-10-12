# core/middleware.py
from urllib import response
from django.shortcuts import redirect, render
from django.urls import reverse, resolve
from django.contrib import messages


class AuthPermissionMiddleware:
    """
    Middleware to check user authentication and permission automatically
    before hitting the view.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to run before the view is called

        # Skip for certain paths (e.g., login, signup, admin, static)
        allowed_paths = [
            reverse("account_login"),
            reverse("account_signup"),
            reverse("account_logout"),
            reverse("landing"),  # public landing page
        ]

        # If user isn't authenticated and trying to access protected pages
        if not request.user.is_authenticated:
            path = request.path

            if not (path.startswith("/metrics") or path in allowed_paths):
                messages.warning(request, "Please log in to continue.")
                return redirect("account_login")
        else:
            # Example: check user permission for staff-only routes
            if request.path.startswith("/admin/") and not request.user.is_staff:
                messages.error(
                    request, "You don't have permission to access admin area.")
                return redirect("landing")

        # Pass request to next middleware or view
        response = self.get_response(request)
        if response.status_code == 403:
            return render(request, "403.html", status=403)
        elif response.status_code == 404:
            return render(request, "404.html", status=404)
        return response
