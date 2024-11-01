from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.tests.utils import AccountsTestUtils
from apps.transactions.models import BalanceIncreaseRequestModel
from apps.transactions.tests.utils import IncreaseBalanceTestMixins
from utils.test_mixins import AdminAuthMixins, SellerUserMixins


class BalanceIncreaseRequestsAPITestCase(APITestCase, AdminAuthMixins, IncreaseBalanceTestMixins, SellerUserMixins):

    def setUp(self):
        # Create a seller instance for testing
        self.seller_user, self.seller = AccountsTestUtils.create_seller()

        self.balance_increase_request_url = reverse('balance-increase-requests')

    def test_get_increase_balance_list(self):
        self.login()

        # Create a few recharge instances for testing
        BalanceIncreaseRequestModel.objects.create(seller=self.seller, amount=20.00)
        BalanceIncreaseRequestModel.objects.create(seller=self.seller, amount=50.00)

        # Send GET request to retrieve the list of recharges
        response = self.client.get(self.balance_increase_request_url)

        # Verify the response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # We created 2 recharges
        self.assertEqual(response.data[0]['amount'], '20.00')
        self.assertEqual(response.data[1]['amount'], '50.00')

    def test_increase_balance_success(self):
        token, _ = self.login_seller(self.seller_user.username)
        self.set_seller_authorization_token(token)
        response = self.increase_balance(amount='30.00', expected_status_code=status.HTTP_201_CREATED)

        # Verify the response status and data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.json())
        self.assertEqual(response.data['amount'], '30.00')
        self.assertEqual(response.data['status'], BalanceIncreaseRequestModel.STATUS_PENDING)

        # Check if the seller balance is updated
        self.seller.refresh_from_db()
        self.assertEqual(
            float(self.seller.balance),
            100.00,
            msg="balance should not still change, because is has not yet been approved!",
        )


class BaseBalanceIncreaseApprovalTestCase(APITestCase, IncreaseBalanceTestMixins, SellerUserMixins):
    def setUp(self):
        self.seller_user, self.seller = AccountsTestUtils.create_seller()
        token, _ = self.login_seller(username=self.seller_user.username)
        self.set_seller_authorization_token(token)
        self.increase_balance( amount='30.00', expected_status_code=status.HTTP_201_CREATED)
        self.balance_increase_request = BalanceIncreaseRequestModel.objects.last()


class BalanceIncreaseApprovalWithAuthTestCase(BaseBalanceIncreaseApprovalTestCase, AdminAuthMixins):

    def setUp(self):
        super().setUp()
        self.login()

    def test_approve_as_admin(self):
        self.approve_increase_balance_request(pk=self.balance_increase_request.pk,
                                              expected_status_code=status.HTTP_200_OK)
        self.balance_increase_request.refresh_from_db()
        self.assertEqual(self.balance_increase_request.status, BalanceIncreaseRequestModel.STATUS_ACCEPTED)
        self.seller.refresh_from_db()
        self.assertEqual(float(self.seller.balance), 130.00)  # Original balance + recharge amount

    def test_reject_as_admin(self):
        self.reject_increase_balance_request(pk=self.balance_increase_request.pk,
                                             expected_status_code=status.HTTP_200_OK)

        self.balance_increase_request.refresh_from_db()
        self.assertEqual(self.balance_increase_request.status, BalanceIncreaseRequestModel.STATUS_REJECTED)
        self.seller.refresh_from_db()
        self.assertEqual(float(self.seller.balance), 100.00)  # Original balance, because request rejected


class BalanceIncreaseApprovalNoAuthTestCase(BaseBalanceIncreaseApprovalTestCase):
    def test_approve_as_non_admin_401_unauthorized(self):
        self.approve_increase_balance_request(pk=self.balance_increase_request.pk,
                                              expected_status_code=status.HTTP_403_FORBIDDEN)

    def test_reject_as_non_admin_401_unauthorized(self):
        self.approve_increase_balance_request(pk=self.balance_increase_request.pk,
                                              expected_status_code=status.HTTP_403_FORBIDDEN)
