"""Transfer URLs."""

from django.urls import path

from apps.transfers import views

app_name = "transfers"

urlpatterns = [
    path("transfer", views.TransferView.as_view(), name="transfer"),
    path("transfer/confirm", views.TransferView.as_view(), name="transfer_confirm"),
]
