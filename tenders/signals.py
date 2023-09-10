from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver

"""Signal to create a demo user after migrations are done."""


@receiver(post_migrate)
def create_demo_user(sender, **kwargs):
    if sender.name == "tenders":
        get_user_model().objects.all().delete()
        get_user_model().objects.create_user(
            username="demo",
            password="demo",
            first_name="Demo User",
        )
