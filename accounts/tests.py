from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date, timedelta
import csv

class AccountsViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        # Create superuser
        self.superuser = User.objects.create_superuser(
            email="admin@example.com",
            password="admin123",
            first_name="Admin",
            last_name="User",
            contact_number="1234567890"
        )

        # Create normal user
        self.user = User.objects.create_user(
            email="user@example.com",
            password="user123",
            first_name="Normal",
            last_name="User",
            contact_number="0987654321"
        )

    # -------------------------
    # REGISTER VIEW
    # -------------------------
    def test_register_view(self):
        url = reverse("register")
        
        # Provide minimal valid data for your RegisterForm
        response = self.client.post(url, {
            "email": "admin@gmail.com",
            "first_name": "New",
            "last_name": "User",
            "contact_number": "01987132107",
            "date_of_birth": (date.today() - timedelta(days=365*20)).isoformat(),  # 20 years old
            "gender": "M",
            "password": "StrongPass123",
            "password2": "StrongPass123"
        })

        # Print form errors if form failed validation (helpful for debugging)
        if response.status_code == 200:
            print(response.context['form'].errors)

        # Assert redirect to login page
        self.assertRedirects(response, reverse("login"))

        # Assert the user was created
        self.assertTrue(User.objects.filter(email="admin@gmail.com").exists())

        # Optional: check user fields
        user = User.objects.get(email="admin@gmail.com")
        self.assertEqual(user.first_name, "New")
        self.assertEqual(user.gender, "M")


    # -------------------------
    # LOGIN VIEW
    # -------------------------
    def test_login_view_success(self):
        url = reverse("login")
        response = self.client.post(url, {
            "email": self.user.email,
            "password": "user123"
        })
        self.assertRedirects(response, reverse("home"))

    def test_login_view_invalid(self):
        url = reverse("login")
        response = self.client.post(url, {
            "email": "wrong@example.com",
            "password": "wrongpass"
        })
        self.assertContains(response, "Invalid email or password.")

    # -------------------------
    # LOGOUT VIEW
    # -------------------------
    def test_logout_view(self):
        self.client.login(email=self.user.email, password="user123")
        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, reverse("login"))

    # -------------------------
    # USER PROFILE
    # -------------------------
    def test_user_profile_update(self):
        self.client.login(email=self.user.email, password="user123")
        url = reverse("user_profile", args=[self.user.id])
        response = self.client.post(url, {
            "first_name": "Updated",
            "last_name": "User",
            "contact_number": "555555555"
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertRedirects(response, url)

    def test_user_profile_unauthorized(self):
        self.client.login(email=self.user.email, password="user123")
        url = reverse("user_profile", args=[self.superuser.id])
        response = self.client.get(url)
        self.assertRedirects(response, reverse("home"))

    # -------------------------
    # USER LIST
    # -------------------------
    def test_user_list_view(self):
        self.client.login(email=self.superuser.email, password="admin123")
        url = reverse("user_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.email)

    # -------------------------
    # DELETE USER
    # -------------------------
    def test_delete_user_superuser(self):
        self.client.login(email=self.superuser.email, password="admin123")
        url = reverse("delete_user", args=[self.user.id])
        response = self.client.post(url)
        self.assertRedirects(response, reverse("user_list"))
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_delete_user_non_superuser(self):
        self.client.login(email=self.user.email, password="user123")
        url = reverse("delete_user", args=[self.superuser.id])
        response = self.client.post(url)
        self.assertRedirects(response, reverse("home"))

    # -------------------------
    # EXPORT USERS CSV
    # -------------------------
    def test_export_users_csv(self):
        self.client.login(email=self.superuser.email, password="admin123")
        url = reverse("export_users_csv")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")

        # Check CSV content
        content = b"".join(response.streaming_content)
        decoded = content.decode("utf-8").splitlines()
        reader = csv.reader(decoded)
        header = next(reader)
        self.assertIn("Email", header)
        self.assertIn("First Name", header)
