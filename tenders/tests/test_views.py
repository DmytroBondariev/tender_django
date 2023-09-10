from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone

from tenders.models import Tender

TENDER_URL = reverse("tenders:tender-list")


class PublicTenderTests(TestCase):
    def test_login_required(self):
        response = self.client.get(TENDER_URL)

        self.assertNotEqual(response.status_code, 200)


class PrivateTenderTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test_user",
            password="Test12345!",
        )
        self.client.force_login(self.user)

    def test_login_asserted(self):
        response = self.client.get(TENDER_URL)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response=response, template_name="pages/tender_list.html"
        )

    def test_retrieve_tenders(self):
        Tender.objects.create(
            tender_id=1,
            description="Lorem ipsum dolor sit amet",
            amount=1000,
            date_modified=timezone.now(),
        )
        Tender.objects.create(
            tender_id=2,
            description="Lorem ipsum dolor sit amet",
            amount=1000,
            date_modified=timezone.now(),
        )

        response = self.client.get(TENDER_URL)

        tenders = Tender.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["tender_list"]), list(tenders))
        self.assertTemplateUsed(
            response=response, template_name="pages/tender_list.html"
        )


class RegisterViewTests(TestCase):
    def test_register_view_accessible_by_name(self):
        response = self.client.get(reverse("tenders:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/register.html")

    def test_register_view_creates_user(self):
        data = {
            "username": "new_user",
            "password1": "Test12345!",
            "password2": "Test12345!",
        }
        response = self.client.post(reverse("tenders:register"), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            get_user_model().objects.filter(username="new_user").exists()
        )


class ButtonToFetchViewTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test_user",
            password="Test12345!",
        )
        self.client.force_login(self.user)

    def test_button_to_fetch_tender(self):
        response = self.client.post(reverse("tenders:tender-update-button"))
        self.assertEqual(response.status_code, 302)

    def test_button_to_fetch_tender_redirects_to_tender_list(self):
        response = self.client.post(reverse("tenders:tender-update-button"))
        self.assertEqual(response.url, reverse("tenders:tender-list"))

    def test_button_to_fetch_tender_updates_tender_list(self):
        response = self.client.post(reverse("tenders:tender-update-button"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Tender.objects.count(), 10)
