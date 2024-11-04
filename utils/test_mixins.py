from typing import Tuple, Optional, Any

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

User = get_user_model()


class AdminAuthMixins:
    def login_admin(self, username: str = "admin", password: str = "adminpass", login_password: Optional[str] = None,
                    expected_status_code: int = status.HTTP_200_OK) -> Tuple[Optional[str], Any]:
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, password=password)

        self.client = APIClient()

        login_url = reverse('admin-login')
        response = self.client.post(login_url, {'username': username, 'password': login_password or password},
                                    format='json')
        self.assertEqual(response.status_code, expected_status_code, msg=response.json())
        token = response.data.get('access')
        self.set_admin_authorization(token)
        return token, response

    def set_admin_authorization(self, token:str):
        # Add Authorization header for subsequent requests
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def unset_authorization(self):
        # Remove Authorization header for subsequent requests
        self.client.credentials()


class SellerUserMixins:
    def login_seller(self, username: str, password: str = "password",
                     expected_status_code: int = status.HTTP_200_OK) -> Tuple[Optional[str], Any]:
        seller_login_url = reverse("seller-login")
        response = self.client.post(seller_login_url, {"username": username, "password": password}, format="json")
        self.assertEqual(response.status_code, expected_status_code, msg=response.json())
        token = response.data.get("access")

        return token, response

    def set_seller_authorization_token(self, token: str):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def unset_authorization_token(self):
        self.client.credentials()
