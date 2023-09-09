from django.contrib.auth import views
from django.urls import path
from tenders.views import (
    IndexView,
    TenderListView,
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("tenders/", TenderListView.as_view(), name="tender-list"),
    path("logout/", views.LogoutView.as_view(), name="logout")
]

app_name = "tenders"
