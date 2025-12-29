"""Banking URLs."""

from django.urls import path

from apps.banking import views

app_name = "banking"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="home"),
    path("dashboard", views.DashboardView.as_view(), name="dashboard"),
    path("activity", views.ActivityView.as_view(), name="activity"),
    path("activity/<str:account>/detail", views.ActivityView.as_view(), name="activity_detail"),
    path("activity/detail", views.ActivityView.as_view(), name="activity_detail_post"),
    path("activity/credit", views.ActivityCreditView.as_view(), name="activityCredit"),
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
]
