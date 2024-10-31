from django.test import TestCase

from apps.accounts.models import SellerProfile, User


class SellerProfileModelTest(TestCase):

    def setUp(self):
        self.seller_username = "seller"
        self.seller_user = User.objects.create(username=self.seller_username, email="seller@example.com")
        self.seller_profile = SellerProfile.objects.create(user=self.seller_user, balance=100.00)

    def test_create_seller(self):
        self.assertEqual(self.seller_profile.user.email, "seller@example.com")
        self.assertEqual(self.seller_profile.balance, 100.00)

    def test_delete_seller(self):
        self.assertEqual(SellerProfile.objects.all().count(), 1)
        # self.seller_profile.delete()
        self.seller_user.delete()
        self.assertEqual(SellerProfile.objects.all().count(), 0)
        self.assertEqual(User.objects.filter(username=self.seller_username).count(), 0)

    def test_update_seller_balance(self):
        self.assertEqual(self.seller_profile.balance, 100.00)
        self.seller_profile.balance = 200.00
        self.seller_profile.save()
        self.assertEqual(self.seller_profile.balance, 200.00)
        self.seller_profile.balance = 3000.00
        self.seller_profile.save()
        self.assertEqual(self.seller_profile.balance, 3000.00)

    def test_update_seller_email(self):
        self.seller_profile.user.email = "seller_new@example.com"
        self.seller_profile.user.save()
        self.assertEqual(self.seller_profile.user.email, "seller_new@example.com")
