from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from utils.api_test_case import ProjectAPITestCase as APITestCase

from utils.test_mixins import AdminAuthMixins

User = get_user_model()


class AdminLoginAPITest(APITestCase, AdminAuthMixins):
    def setUp(self):
        # URL for the admin login endpoint
        self.login_url = reverse("admin-login")

        # Create a regular non-admin user
        self.regular_user = User.objects.create_user(username="regular_user", password="password123")

    def test_admin_login_success(self):
        # Login attempt with admin credentials
        _, response = self.login_admin()

        # Check if login is successful and JWT tokens are returned
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_non_admin_login_failure(self):
        # Login attempt with non-admin credentials
        response = self.client.post(
            self.login_url, {"username": "regular_user", "password": "password123"},
            format="json",
        )

        # Check if login fails because the user is not an admin
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Only admin users can log in here.", response.data["non_field_errors"][0])

    def test_incorrect_password_login_failure(self):
        # Login attempt with incorrect password for admin user
        self.client.post(
            self.login_url, {"username": "admin_user", "password": "wrongpassword"},
            format="json",
        )
        # Check if login fails due to incorrect password
        _, response = self.login_admin(login_password="wrongpassword", expected_status_code=status.HTTP_401_UNAUTHORIZED)
        self.assertIn("No active account found with the given credentials", response.data["detail"])
