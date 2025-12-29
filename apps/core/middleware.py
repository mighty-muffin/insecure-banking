"""Core middleware."""

from django.http import HttpResponseRedirect


class AuthRequiredMiddleware:
    """Middleware to redirect unauthenticated users to login page."""

    def __init__(self, get_response):
        """Initialize middleware."""
        self.get_response = get_response

    def __call__(self, request):
        """Process request."""
        login_page = request.path.startswith("/login")
        principal = request.user
        if principal.is_authenticated or login_page:
            return self.get_response(request)
        return HttpResponseRedirect("/login")
