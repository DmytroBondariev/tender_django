from django.contrib.auth import views
from django.urls import path
from tenders.views import (
    IndexView,
    TenderListView,
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("logout/", views.LogoutView.as_view(), name="logout")
]

app_name = "tenders"
