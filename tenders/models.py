from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class Tender(models.Model):
    tender_id = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_modified = models.DateTimeField()

    class Meta:
        ordering = ["-date_modified"]
        verbose_name = "Tender"
        verbose_name_plural = "Tenders"

    def __str__(self):
        return f"Tender id: {self.tender_id}; ({self.description}, {self.amount}). Date modified: {self.date_modified}"

    def get_absolute_url(self):
        return reverse("tenders:tender-detail", kwargs={"pk": self.id})


class User(AbstractUser):
    pass
