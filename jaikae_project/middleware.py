# core/middleware.py
from django.shortcuts import redirect
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
            if not any(request.path == path for path in allowed_paths):
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
        return response
