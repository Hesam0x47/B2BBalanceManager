from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import SellerProfile, User
from apps.transactions.models import BalanceIncreaseRequestModel
from utils.test_mixins import AdminAuthMixins


class RechargeAPITestCase(APITestCase, AdminAuthMixins):

    def setUp(self):
        # Create a seller instance for testing
        self.seller_username = "seller"
        self.seller_user = User.objects.create(username=self.seller_username, email="sellar@sample.com")
        self.seller = SellerProfile.objects.create(balance=100.00, user=self.seller_user)
        self.recharge_url = reverse('balance-increase-requests')
        self.login()
        self.set_admin_authorization()

    def test_get_recharge_list(self):
        # Create a few recharge instances for testing
        BalanceIncreaseRequestModel.objects.create(seller=self.seller, amount=20.00)
        BalanceIncreaseRequestModel.objects.create(seller=self.seller, amount=50.00)

        # Send GET request to retrieve the list of recharges
        response = self.client.get(self.recharge_url)

        # Verify the response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # We created 2 recharges
        self.assertEqual(response.data[0]['amount'], '20.00')
        self.assertEqual(response.data[1]['amount'], '50.00')

    def test_create_recharge_success(self):
        # Prepare payload for a new recharge
        payload = {
            'seller': self.seller.user.username,
            'amount': '30.00'
        }

        # Send POST request to create a new recharge
        response = self.client.post(self.recharge_url, payload, format='json')

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

    def test_create_recharge_invalid_seller(self):
        # Prepare payload with an invalid seller_id
        payload = {
            'seller': 'invalid-server-id',  # Non-existent seller ID
            'amount': '30.00'
        }

        # Send POST request with invalid data
        response = self.client.post(self.recharge_url, payload, format='json')

        # Verify the response status and error message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, msg=response.json())
        self.assertIn('seller', response.data)  # Check that the error message mentions the seller field


class BaseRechargeStatusChangeTestCase(APITestCase):
    def setUp(self):
        # Create a seller and admin user
        self.seller_username = "seller"
        self.seller_user = User.objects.create(username=self.seller_username, email="sellar@sample.com")
        self.seller = SellerProfile.objects.create(user=self.seller_user, balance=100.00)
        self.recharge = BalanceIncreaseRequestModel.objects.create(seller=self.seller, amount=30.00)
        self.recharge_status_change_accepted_url = reverse(
            'balance-increase-requests-approval',
            kwargs={"pk": self.recharge.id,
                    "action": BalanceIncreaseRequestModel.STATUS_ACCEPTED},
        )
        self.recharge_status_change_rejected_url = reverse(
            'balance-increase-requests-approval',
            kwargs={"pk": self.recharge.id,
                    "action": BalanceIncreaseRequestModel.STATUS_REJECTED},
        )


class RechargeStatusChangeWithAuthTestCase(BaseRechargeStatusChangeTestCase, AdminAuthMixins):

    def setUp(self):
        self.login()
        self.set_admin_authorization()
        return super().setUp()

    def test_approve_recharge_as_admin(self):
        response = self.client.patch(self.recharge_status_change_accepted_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())
        self.recharge.refresh_from_db()
        self.assertEqual(self.recharge.status, BalanceIncreaseRequestModel.STATUS_ACCEPTED)
        self.seller.refresh_from_db()
        self.assertEqual(float(self.seller.balance), 130.00)  # Original balance + recharge amount

    def test_reject_recharge_as_admin(self):
        response = self.client.patch(self.recharge_status_change_rejected_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())
        self.recharge.refresh_from_db()
        self.assertEqual(self.recharge.status, BalanceIncreaseRequestModel.STATUS_REJECTED)
        self.seller.refresh_from_db()
        self.assertEqual(float(self.seller.balance), 100.00)  # Original balance, because request rejected


class RechargeStatusChangeNoAuthTestCase(BaseRechargeStatusChangeTestCase):

    def test_approve_recharge_as_non_admin_401_unauthorized(self):
        # Attempt to approve without admin privileges
        response = self.client.patch(self.recharge_status_change_accepted_url)

        # Verify that access is forbidden
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, msg=response.json())
