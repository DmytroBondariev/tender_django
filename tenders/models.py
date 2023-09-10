from django.contrib.auth.models import AbstractUser
from django.db import models


class Tender(models.Model):
    tender_id = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    date_modified = models.DateTimeField()

    class Meta:
        ordering = ["-date_modified"]
        verbose_name = "Tender"
        verbose_name_plural = "Tenders"

    def __str__(self):
        return f"Tender id: {self.tender_id}; ({self.description}, {self.amount}). Date modified: {self.date_modified}"


class User(AbstractUser):
    pass
