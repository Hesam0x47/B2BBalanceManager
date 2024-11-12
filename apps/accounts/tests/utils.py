from typing import Tuple

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from apps.accounts.models import SellerProfile

User = get_user_model()


class AccountsTestUtils:
    @staticmethod
    def create_user(
            username: str = "seller",
            password: str = "123!@#abcABC",
            email: str = "seller@sample.com",
            balance: float = 100.00,
            is_verified: bool = True,
            group_name: str = "Sellers",
    ):
        seller_user = User.objects.create(username=username, email=email)
        seller_user.set_password(password)
        seller_user.save()

        seller_profile = SellerProfile.objects.create(
            balance=balance,
            user=seller_user,
            is_verified=is_verified,
        )

        seller_group = Group.objects.get(name=group_name)
        seller_user.groups.add(seller_group)
        seller_user.save()
        return seller_user, seller_profile

    @staticmethod
    def create_seller(
            username: str = "seller",
            password: str = "123!@#abcABC",
            email: str = "seller@sample.com",
            balance: float = 100.00,
            is_verified: bool = True,
    ) -> Tuple[User, SellerProfile]:
        return AccountsTestUtils.create_user(
            username,
            password,
            email,
            balance,
            is_verified,
        )

    @staticmethod
    def create_status_changer(
            username: str = "status_changer",
            password: str = "123!@#abcABC",
            email: str = "status_changer@sample.com",
            balance: float = 100.00,
            is_verified: bool = True,
            group_name: str = "StatusChangers",
    ) -> Tuple[User, SellerProfile]:
        return AccountsTestUtils.create_user(
            username,
            password,
            email,
            balance,
            is_verified,
            group_name,
        )
