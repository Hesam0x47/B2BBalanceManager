from django.urls import reverse
from rest_framework import status

from apps.accounts.tests.utils import AccountsTestUtils
from apps.transactions.tests.utils import IncreaseBalanceTestMixins
from utils.api_test_case import ProjectAPITestCase as APITestCase
from utils.test_mixins import AdminAuthMixins, SellerUserMixins


class BalanceIncreaseRequestsAPITestCase(APITestCase, AdminAuthMixins, IncreaseBalanceTestMixins, SellerUserMixins):
    fixtures = APITestCase.fixtures + ["apps/status/fixtures/status_changer_group.json"]

    def setUp(self):
        self.status_changer_user, self.status_changer = AccountsTestUtils.create_status_changer()

        self.status_api_list_url = reverse('status-api-list')

    def test_status_changer_user_change_name_and_status_forbidden_403(self):
        token, _ = self.login_seller(username=self.status_changer_user.username)
        self.set_seller_authorization_token(token)
        data = {
            "name": "name",
            "status": "up",
        }

        response = self.client.post(self.status_api_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        pk = response.json().get("id")

        update_status_url = reverse(
            'status-api-detail',
            kwargs={"pk": pk},
        )
        response = self.client.patch(update_status_url, data={"name": "name2"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, msg=response.json())

    def test_status_changer_user_can_only_update_status_field_allowed_200(self):
        token, _ = self.login_seller(username=self.status_changer_user.username)
        self.set_seller_authorization_token(token)
        data = {
            "name": "name",
            "status": "up",
        }

        response = self.client.post(self.status_api_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.json())
        pk = response.json().get("id")

        update_status_url = reverse(
            'status-api-detail',
            kwargs={"pk": pk},
        )
        response = self.client.patch(update_status_url, data={"status": "down"})
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())

    def test_admin_user_can_update_status_and_name_fields_allowed_200(self):
        token, _ = self.login_admin()
        self.set_admin_authorization(token)
        data = {
            "name": "name",
            "status": "up",
        }

        response = self.client.post(self.status_api_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.json())
        pk = response.json().get("id")

        update_status_url = reverse(
            'status-api-detail',
            kwargs={"pk": pk},
        )
        response = self.client.patch(update_status_url, data={"status": "down", "name": "name2"})
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())
