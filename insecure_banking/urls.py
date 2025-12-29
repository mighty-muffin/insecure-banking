"""URL configuration for Insecure Banking project."""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.accounts.urls")),
    path("", include("apps.banking.urls")),
    path("", include("apps.transfers.urls")),
]
