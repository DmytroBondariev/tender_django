from django.contrib.auth import views
from django.urls import path
from tenders.views import (
    IndexView,
    TenderListView,
    RegisterView,
    button_to_fetch_tender,
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("register/", RegisterView.as_view(), name="register"),
    path("tenders/", TenderListView.as_view(), name="tender-list"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path(
        "tenders/update/",
        button_to_fetch_tender,
        name="tender-update-button"
    ),
]

app_name = "tenders"
