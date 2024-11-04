import argparse
import dataclasses
import random
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import List, Final, Type

import requests

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Load test for B2B Balance Manager transactions.")
parser.add_argument("--sellers", type=int, default=2, help="Number of sellers to create.")
parser.add_argument("--num-requests", type=int, default=1000, help="Number of customer charge requests.")
parser.add_argument("--executor", choices=["process", "thread"], default="thread",
                    help="Type of executor to use: 'process' for ProcessPoolExecutor, 'thread' for ThreadPoolExecutor.")
parser.add_argument("--workers", type=int, default=10, help="Number of workers to use.")

args = parser.parse_args()

# Configurations based on parsed arguments
NUM_SELLERS = args.sellers
NUM_REQUESTS = args.num_requests
BASE_URL = "http://127.0.0.1:8000"
EXECUTOR_CLASS: Final[Type[ProcessPoolExecutor] | Type[ThreadPoolExecutor]] = (
    ProcessPoolExecutor if args.executor == "process" else ThreadPoolExecutor
)
WORKERS = args.workers


@dataclasses.dataclass
class User:
    username: str
    password: str
    password2: str
    email: str
    company_name: str

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


class BalanceManagerAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.auth_tokens = {}
        self.admin_token = None

        self.login_admin()

    def register_seller(self, seller: User):
        response = requests.post(f"{self.base_url}/accounts/seller/register/", json=seller.to_dict())
        if response.status_code == 201:
            print(f"Registered {seller.username} successfully.")
        else:
            print(f"Failed to register {seller.username}: {response.status_code}, {response.text}")

    def login_admin(self, username="admin", password="admin"):
        response = requests.post(f"{self.base_url}/accounts/admin/login/",
                                 json={"username": username, "password": password})
        if response.status_code == 200:
            self.admin_token = response.json().get("access")
            print("Admin logged in successfully.")
        else:
            print(f"Admin login failed: {response.status_code}, {response.json()}")

    def verify_seller(self, seller: User):
        if not self.admin_token:
            print("Admin token missing.")
            return
        response = requests.put(
            f"{self.base_url}/accounts/admin/verify-seller/{seller.username}/",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json={"is_verified": True}
        )
        if response.status_code == 200:
            print(f"Verified seller '{seller.username}'")
        else:
            print(f"Failed to verify seller '{seller.username}': {response.status_code}, {response.json()}")

    def login_seller(self, seller: User):
        response = requests.post(
            f"{self.base_url}/accounts/seller/login/",
            json={"username": seller.username, "password": seller.password}
        )
        if response.status_code == 200:
            token = response.json().get("access")
            self.auth_tokens[seller.username] = token
            print(f"Logged in {seller.username}")
        else:
            print(f"Failed to log in {seller.username}: {response.status_code}, {response.json()}")

    def charge_customer(self, amount: float, seller_username: str) -> float:
        phone_number = f"09{random.randint(100000000, 999999999)}"
        response = requests.post(
            f"{self.base_url}/transactions/charge-customer/",
            json={"phone_number": phone_number, "amount": amount},
            headers={"Authorization": f"Bearer {self.auth_tokens[seller_username]}"}
        )
        if response.status_code == 201:
            print(f"Charged {amount} to customer {phone_number} for {seller_username}")
            return amount
        else:
            print(f"Charge failed for {seller_username}: {response.status_code}, {response.text}")
            return 0

    def increase_balance(self, seller_username):
        amount = random.randint(100, 10000)
        response = requests.post(
            f"{self.base_url}/transactions/balance-increase-requests/",
            json={"amount": amount},
            headers={"Authorization": f"Bearer {self.auth_tokens[seller_username]}"}
        )
        if response.status_code == 201:
            print(f"Requested balance increase of {amount} for {seller_username}")
            pk = response.json().get("id")
            self.approve_increase(pk)
            return amount  # return the increase amount for tracking
        else:
            print(f"Balance increase request failed for {seller_username}: {response.status_code}, {response.json()}")
            return 0  # return 0 if increase request failed

    def approve_increase(self, pk):
        response = requests.patch(
            f"{self.base_url}/transactions/balance-increase-requests/{pk}/accepted/",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        if response.status_code == 200:
            print(f"Approved balance increase with ID {pk}")
        else:
            print(f"Approval failed: {response.status_code}, {response.json()}")

    def get_seller_info(self, seller_username):
        response = requests.get(
            f"{self.base_url}/accounts/sellers/{seller_username}/",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        if response.status_code == 200:
            return response.json().get("balance", 0)
        else:
            print(f"Failed to get info for {seller_username}: {response.status_code}, {response.text}")
        return 0

    def create_and_register_sellers(self, NUM_SELLERS) -> List[User]:
        # Register and verify sellers
        sellers: List[User] = [
            User(
                username=f"seller{i + 1}",
                password=f"seller_password{i + 1}",
                password2=f"seller_password{i + 1}",
                email=f"seller{i + 1}@example.com",
                company_name=f"Seller{i + 1} Company"
            ) for i in range(NUM_SELLERS)
        ]

        for seller in sellers:
            self.register_seller(seller)

        # for seller in sellers:
        #     self.verify_seller(seller)
        #     self.login_seller(seller)

        return sellers

    def verify_and_login_sellers(self, sellers: List[User]) -> List[User]:
        for seller in sellers:
            self.register_seller(seller)

        for seller in sellers:
            self.verify_seller(seller)
            self.login_seller(seller)

        return sellers


class Tester:
    def __init__(self, client_obj: BalanceManagerAPIClient, num_sellers: int):
        self.total_charges = {}
        self.total_increases = {}
        self.sellers: List[User] = []
        self.client: BalanceManagerAPIClient = client_obj

        self.create_sellers(num_sellers)
        self.register_sellers()
        self.verify_sellers()
        self.login_sellers()

    def track_charge(self, seller_username, amount):
        self.total_charges[seller_username] = self.total_charges.get(seller_username, 0) + amount

    def track_increase(self, seller_username, amount):
        self.total_increases[seller_username] = self.total_increases.get(seller_username, 0) + amount

    def assert_final_balances(self, client: BalanceManagerAPIClient):
        print("All tasks completed. Final balances:")
        for seller_username, expected_charge in self.total_charges.items():
            actual_balance = client.get_seller_info(seller_username)
            expected_balance = self.total_increases.get(seller_username, 0) - expected_charge
            print(f"{seller_username} - Expected Balance: {expected_balance}, Actual Balance: {actual_balance}")

    def create_sellers(self, num_sellers: int) -> List[User]:
        sellers: List[User] = [
            User(
                username=f"seller{i + 1}",
                password=f"seller_password{i + 1}",
                password2=f"seller_password{i + 1}",
                email=f"seller{i + 1}@example.com",
                company_name=f"Seller{i + 1} Company"
            ) for i in range(num_sellers)
        ]
        self.sellers = sellers
        return sellers

    def register_sellers(self):
        for seller in self.sellers:
            self.client.register_seller(seller)

    def verify_sellers(self):
        for seller in self.sellers:
            self.client.verify_seller(seller)

    def login_sellers(self):
        for seller in self.sellers:
            self.client.login_seller(seller)

    def run(self):
        with ProcessPoolExecutor(max_workers=WORKERS) as executor:
            futures = []
            for _ in range(NUM_REQUESTS):
                seller: User = random.choice(list(self.sellers))
                amount = random.randint(1, 50)

                # Submit the charge_customer task and store future for callback
                future = executor.submit(self.client.charge_customer, amount, seller.username)
                future.add_done_callback(lambda f: charge_callback(f, seller.username))
                futures.append(future)

                # Occasionally trigger a balance increase and track results
                if random.random() < 0.01:
                    increase_future = executor.submit(self.client.increase_balance, seller.username)
                    increase_future.add_done_callback(
                        lambda f: tester.track_increase(seller.username, f.result())
                    )
                    futures.append(increase_future)

            # Ensure all futures have completed
            for future in futures:
                future.result()  # Block until each future is complete


def charge_callback(future, seller_username):
    # Get the result from the future and pass it to track_charge
    result = future.result()
    tester.track_charge(seller_username, result)


if __name__ == "__main__":
    client = BalanceManagerAPIClient(base_url=BASE_URL)
    tester = Tester(client, NUM_SELLERS)

    tester.run()
    tester.assert_final_balances(client)
