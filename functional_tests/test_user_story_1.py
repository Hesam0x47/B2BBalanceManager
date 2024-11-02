import random
import threading
from concurrent.futures import ThreadPoolExecutor

import requests

# Configurations
BASE_URL = "http://127.0.0.1:8000"
number_of_sellers = 2
SELLER_CREDENTIALS = [
    {
        "username": f"seller{idx}",
        "password": f"seller_password{idx}",
        "email": f"seller{idx}@example.com",
        "company_name": f"Seller{idx} Company"
    } for idx in range(1, number_of_sellers + 1)
]

SELLERS_AUTH_TOKENS = {}
ADMIN_TOKEN = None
NUM_OF_CUSTOMER_CHARGE_REQUESTS = 1000

admin_username = "admin"
admin_password = "admin"

# Track charges and balance increases
total_charges = {f"seller{idx}": 0 for idx, _ in enumerate(SELLER_CREDENTIALS, start=1)}
total_increases = {f"seller{idx}": 0 for idx, _ in enumerate(SELLER_CREDENTIALS, start=1)}
initial_balances = {}

# Initialize lock for thread-safe operations
lock = threading.Lock()


def get_seller_balance(seller_id):
    response = requests.get(
        f"{BASE_URL}/accounts/sellers/{seller_id}/",
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
    )

    if response.status_code == 200:
        return float(response.json().get("balance"))
    else:
        print(f"Failed to retrieve balance for seller {seller_id}: {response.status_code}, {response.text}")
    return 0


def register_seller(seller):
    response = requests.post(
        f"{BASE_URL}/accounts/seller/register/",
        json={
            "username": seller["username"],
            "password": seller["password"],
            "password2": seller["password"],
            "email": seller["email"],
            "company_name": seller["company_name"]
        }
    )
    if response.status_code == 201:
        print(f"Registered {seller['username']} successfully.")
    else:
        print(f"Failed to register {seller['username']}: {response.status_code}, {response.text}")


def login_admin(username, password):
    global ADMIN_TOKEN
    response = requests.post(
        f"{BASE_URL}/accounts/admin/login/",
        json={"username": username, "password": password}
    )
    if response.status_code == 200:
        ADMIN_TOKEN = response.json().get("access")
        print("Admin logged in successfully.")
    else:
        print(f"Admin login failed: {response.status_code}, {response.json()}")


def verify_seller(seller_id):
    if not ADMIN_TOKEN:
        print("Admin token is missing. Admin must be logged in first.")
        return
    response = requests.put(
        f"{BASE_URL}/accounts/admin/verify-seller/{seller_id}/",
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
        json={"is_verified": True}
    )
    if response.status_code == 200:
        print(f"Verified seller with ID {seller_id} successfully.")
    else:
        print(f"Failed to verify seller {seller_id}: {response.status_code}, {response.json()}")


def login_seller(seller):
    response = requests.post(
        f"{BASE_URL}/accounts/seller/login/",
        json={"username": seller["username"], "password": seller["password"]}
    )
    if response.status_code == 200:
        token = response.json().get("access")
        SELLERS_AUTH_TOKENS[seller["username"]] = token
        print(f"Logged in {seller['username']} and obtained token.")
    else:
        print(f"Failed to log in {seller['username']}: {response.status_code}, {response.json()}")


def charge_customer(amount, seller_username):
    phone_number = f"09{random.randint(100000000, 999999999)}"
    response = requests.post(
        f"{BASE_URL}/transactions/charge-customer/",
        json={
            "phone_number": phone_number,
            "amount": amount
        },
        headers={"Authorization": f"Bearer {SELLERS_AUTH_TOKENS[seller_username]}"}
    )
    if response.status_code == 201:
        with lock:
            total_charges[seller_username] += amount
        print(f"Charged {amount} to customer {phone_number} for seller {seller_username}")
    else:
        print(f"Failed to charge customer with {amount} charge: {response.status_code}, {response.text}")


def increase_balance(seller_username):
    amount = random.randint(100, 10000)
    response = requests.post(
        f"{BASE_URL}/transactions/balance-increase-requests/",
        json={"amount": amount},
        headers={"Authorization": f"Bearer {SELLERS_AUTH_TOKENS[seller_username]}"}
    )
    if response.status_code == 201:
        with lock:
            total_increases[seller_username] += amount
        pk = response.json().get("id")
        response = requests.patch(
            f"{BASE_URL}/transactions/balance-increase-requests/{pk}/accepted/",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
        )
        if response.status_code == 200:
            print(f"Approved increased balance by {amount} for seller {seller_username}")
        else:
            print(f"Failed to approve increase balance: {response.status_code}, {response.json()}")


def get_seller_id(username):
    for idx, seller in enumerate(SELLER_CREDENTIALS, start=1):  # Start enumeration from 1 for ID
        if seller["username"] == username:
            return idx
    raise ValueError(f"Seller with username '{username}' not found.")


def run_performance_test():
    for seller in SELLER_CREDENTIALS:
        register_seller(seller)

    login_admin(admin_username, admin_password)
    global initial_balances
    initial_balances = {f"seller{idx}": get_seller_balance(idx) for idx, _ in enumerate(SELLER_CREDENTIALS, start=1)}

    for seller_id in range(1, len(SELLER_CREDENTIALS) + 1):
        verify_seller(seller_id)

    for seller in SELLER_CREDENTIALS:
        login_seller(seller)

    with ThreadPoolExecutor(max_workers=9) as executor:
        for _ in range(NUM_OF_CUSTOMER_CHARGE_REQUESTS):
            random_seller_username = random.choice(list(SELLERS_AUTH_TOKENS.keys()))
            amount = random.randint(1, 50)

            executor.submit(charge_customer, amount, random_seller_username)

            # Occasionally trigger a balance increase
            if random.random() < 0.1:
                executor.submit(increase_balance, random_seller_username)

        # Wait for all submitted tasks to complete
        executor.shutdown(wait=True)
    print("All tasks have completed.")


# Run the test
if __name__ == "__main__":
    run_performance_test()

    # Verify final balances for each seller
    for seller_username, initial_balance in initial_balances.items():
        expected_balance = initial_balance + total_increases[seller_username] - total_charges[seller_username]

        seller_id = get_seller_id(seller_username)
        response = requests.get(
            f"{BASE_URL}/accounts/sellers/{seller_id}/",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
        )

        if response.status_code == 200:
            actual_balance = float(response.json().get("balance"))
            print(f"{seller_username} - Expected Balance: {expected_balance}, Actual Balance: {actual_balance}")
            assert abs(expected_balance - actual_balance) < 1, f"Balance mismatch for {seller_username}!"
        else:
            print(f"Failed to retrieve balance for {seller_username}: {response.status_code}, {response.text}")
