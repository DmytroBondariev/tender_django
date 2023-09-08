from django.urls import path
from tenders.views import (
    IndexView,
    TenderListView,
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
]

app_name = "tenders"
