from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.transactions.models import Seller, Recharge


class RechargeAPITestCase(APITestCase):

    def setUp(self):
        # Create a seller instance for testing
        self.seller = Seller.objects.create(name="Test Seller", balance=100.00, email="sellar@sample.com")
        self.recharge_url = reverse('recharge-list-create')

    def test_get_recharge_list(self):
        # Create a few recharge instances for testing
        Recharge.objects.create(seller=self.seller, amount=20.00, is_successful=True)
        Recharge.objects.create(seller=self.seller, amount=50.00, is_successful=True)

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
            'seller': self.seller.email,
            'amount': '30.00'
        }

        # Send POST request to create a new recharge
        response = self.client.post(self.recharge_url, payload, format='json')

        # Verify the response status and data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.json())
        self.assertEqual(response.data['amount'], '30.00')
        self.assertEqual(response.data['status'], Recharge.STATUS_PENDING)

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
            'seller_id': 999,  # Non-existent seller ID
            'amount': '30.00'
        }

        # Send POST request with invalid data
        response = self.client.post(self.recharge_url, payload, format='json')

        # Verify the response status and error message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('seller', response.data)  # Check that the error message mentions the seller field


class RechargeStatusChangeTestCase(APITestCase):

    def setUp(self):
        # Create a seller and admin user
        self.seller = Seller.objects.create(name="Test Seller", balance=100.00)
        self.admin_user = User.objects.create_superuser(username='admin', password='adminpass')
        self.recharge = Recharge.objects.create(seller=self.seller, amount=30.00)
        # self.recharge_status_change_accepted_url = reverse('recharge-change-status', kwargs={"recharge_id":self.recharge.id, "action": Recharge.STATUS_ACCEPTED })
        self.recharge_status_change_accepted_url = reverse('recharge-change-status', args=[self.recharge.id, Recharge.STATUS_ACCEPTED ])
        # self.recharge_status_change_rejected_url = reverse('recharge-change-status', kwargs={"recharge_id":self.recharge.id, "action": Recharge.STATUS_REJECTED })

    def test_approve_recharge_as_admin(self):
        self.client.login(username='admin', password='adminpass')

        response = self.client.post(self.recharge_status_change_accepted_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.recharge.refresh_from_db()
        self.assertEqual(self.recharge.status, Recharge.STATUS_ACCEPTED)
        self.seller.refresh_from_db()
        self.assertEqual(float(self.seller.balance), 130.00)  # Original balance + recharge amount

    def test_approve_recharge_as_non_admin(self):
        # Attempt to approve without admin privileges
        response = self.client.post(self.recharge_status_change_accepted_url)

        # Verify that access is forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
