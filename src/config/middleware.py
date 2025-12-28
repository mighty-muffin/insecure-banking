"""Authentication middleware for the application."""

from django.http import HttpRequest, HttpResponseRedirect


class AuthRequiredMiddleware:
    """
    Middleware to enforce authentication for all views except login.

    This middleware checks if the user is authenticated before allowing
    access to any view. Unauthenticated users are redirected to the
    login page, except when they're already on the login page.
    """

    def __init__(self, get_response):
        """
        Initialize middleware.

        Args:
            get_response: Next middleware or view in the chain
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        """
        Process the request and enforce authentication.

        Args:
            request: HTTP request object

        Returns:
            HTTP response from next middleware/view or redirect to login
        """
        login_page = request.path.startswith("/login")
        principal = request.user
        if principal.is_authenticated or login_page:
            return self.get_response(request)
        return HttpResponseRedirect("/login")
