from django.contrib.auth import views
from django.urls import path
from tenders.views import (
    IndexView,
    TenderListView, RegisterView, ButtonToGetTenderView,
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("register/", RegisterView.as_view(), name="register"),
    path("tenders/", TenderListView.as_view(), name="tender-list"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("tenders/update/", ButtonToGetTenderView.as_view(), name="tender-update-button"),
]

app_name = "tenders"
