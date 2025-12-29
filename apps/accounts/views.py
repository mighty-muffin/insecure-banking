"""Account views."""

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.views.generic.base import TemplateView, View

from apps.accounts.services import AccountService


class LoginView(TemplateView):
    """Login view."""

    http_method_names = ["get", "post"]
    template_name = "login.html"

    def post(self, request, *args, **kwargs):
        """Handle login POST request."""
        user = authenticate(request=request)
        if user is None:
            template = loader.get_template("login.html")
            context = {"authenticationFailure": True}
            return HttpResponse(template.render(context, request))
        login(request, user)
        return redirect("/dashboard")


class LogoutView(View):
    """Logout view."""

    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        """Handle logout GET request."""
        logout(request)
        return redirect("/login")


class AdminView(TemplateView):
    """Admin view."""

    http_method_names = ["get"]
    template_name = "admin.html"

    def get_context_data(self, *args, **kwargs):
        """Get context data."""
        context = super().get_context_data(**kwargs)
        principal = self.request.user
        context["account"] = AccountService.find_users_by_username(principal.username)[0]
        context["accounts"] = AccountService.find_all_users()
        return context
