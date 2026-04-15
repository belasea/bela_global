from django.test import TestCase, Client
from django.urls import reverse
from contacts.models import Contact
from accounts.models import User

class ContactViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Correct superuser creation without username
        self.superuser = User.objects.create_superuser(
            email="admin@gmail.com",
            password="admin123",
            first_name="Admin",
            last_name="User",
            contact_number="01987132107"
        )
        # Login with email instead of username
        self.client.login(email="admin@gmail.com", password="admin123")

        # Create a sample contact
        self.contact = Contact.objects.create(
            name="Test User",
            email="jayed.swe@gmail.com",
            message="Hello"
        )

    def test_contact_page_loads(self):
        response = self.client.get(reverse("contact-us"))
        self.assertEqual(response.status_code, 200)

    def test_contact_list_page(self):
        response = self.client.get(reverse("contact-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.contact.name)

    def test_update_contact(self):
        def test_update_contact(self):
            url = reverse("update-contact", args=[self.contact.id])
            response = self.client.post(url, {
                "name": "Updated Name",
                "email": "jibon.py@gmail.com",
                "message": "Updated message"
            })
            self.contact.refresh_from_db()
            self.assertEqual(self.contact.name, "Updated Name")
            self.assertRedirects(response, reverse("contact-list") + "?page=1")

    def test_delete_contact(self):
        url = reverse("delete-contact", args=[self.contact.id])
        response = self.client.post(url)
        self.assertFalse(Contact.objects.filter(id=self.contact.id).exists())

    def test_reply_contact(self):
        url = reverse("replay-contact", args=[self.contact.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_download_csv(self):
        response = self.client.get(reverse("download-contact-list-csv"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")

    def test_download_csv_by_date(self):
        response = self.client.get(reverse("download-contact-list-by-date"), {
            "start_date": "2020-01-01",
            "end_date": "2030-01-01"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
