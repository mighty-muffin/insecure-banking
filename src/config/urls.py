"""
URL configuration for insecure banking project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/

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

from django.contrib import admin
from django.urls import path

from web import views

# URL patterns for the application
# Note: APPEND_SLASH is False, so URLs must match exactly
urlpatterns = [
    # Django admin interface
    path("admin/", admin.site.urls, name="django_admin"),
    # Authentication
    path("login", views.LoginView.as_view(), name="login"),
    path("logout", views.LogoutView.as_view(), name="logout"),
    # Dashboard and home
    path("", views.DashboardView.as_view(), name="home"),
    path("dashboard", views.DashboardView.as_view(), name="dashboard"),
    # Admin panel (custom)
    path("admin", views.AdminView.as_view(), name="admin"),
    # Activity and transactions
    path("activity", views.ActivityView.as_view(), name="activity"),
    path("activity/<str:account>/detail", views.ActivityView.as_view(), name="activity_detail"),
    path("activity/detail", views.ActivityView.as_view(), name="activity_detail_post"),
    path("activity/credit", views.ActivityCreditView.as_view(), name="activityCredit"),
    # User profile
    path("dashboard/userDetail", views.UserDetailView.as_view(), name="userDetail"),
    path(
        "dashboard/userDetail/creditCardImage",
        views.CreditCardImageView.as_view(),
        name="creditCardImage",
    ),
    path("dashboard/userDetail/avatar", views.AvatarView.as_view(), name="avatar"),
    path(
        "dashboard/userDetail/avatar/update",
        views.AvatarUpdateView.as_view(),
        name="avatarUpdate",
    ),
    # Certificates (demonstrating insecure deserialization)
    path(
        "dashboard/userDetail/certificate",
        views.CertificateDownloadView.as_view(),
        name="certificateDownload",
    ),
    path(
        "dashboard/userDetail/maliciouscertificate",
        views.MaliciousCertificateDownloadView.as_view(),
        name="maliciousCertificateDownload",
    ),
    path(
        "dashboard/userDetail/newcertificate",
        views.NewCertificateView.as_view(),
        name="newCertificate",
    ),
    # Transfers
    path("transfer", views.TransferView.as_view(), name="transfer"),
    path("transfer/confirm", views.TransferView.as_view(), name="transfer_confirm"),
]
