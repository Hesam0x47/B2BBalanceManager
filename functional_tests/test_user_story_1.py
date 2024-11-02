import random
import threading
from concurrent.futures import ThreadPoolExecutor

import requests

# Configurations
BASE_URL = "http://127.0.0.1:8000"  # Update with your actual Gunicorn server URL
SELLER_CREDENTIALS = [
    {"username": "seller1", "password": "seller_password1", "email": "seller1@example.com",
     "company_name": "Seller1 Company"},
    {"username": "seller2", "password": "seller_password2", "email": "seller2@example.com",
     "company_name": "Seller2 Company"},
    # {"username": "seller3", "password": "seller_password3", "email": "seller3@example.com", "company_name": "Seller3 Company"},
    # {"username": "seller4", "password": "seller_password4", "email": "seller4@example.com", "company_name": "Seller4 Company"},
    # {"username": "seller5", "password": "seller_password5", "email": "seller5@example.com", "company_name": "Seller5 Company"},
]
AUTH_TOKENS = {}  # Store tokens for sellers
ADMIN_TOKEN = None  # Store the admin token here after login
NUM_REQUESTS = 1000  # Total number of customer charge requests

# Track charges and balance increases
total_charges = {f"seller{idx}": 0 for idx, _ in enumerate(SELLER_CREDENTIALS, start=1)}
total_increases = {f"seller{idx}": 0 for idx, _ in enumerate(SELLER_CREDENTIALS, start=1)}

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
        AUTH_TOKENS[seller["username"]] = token
        print(f"Logged in {seller['username']} and obtained token.")
    else:
        print(f"Failed to log in {seller['username']}: {response.status_code}, {response.json()}")


# Register sellers
for seller in SELLER_CREDENTIALS:
    register_seller(seller)

# Admin login to verify sellers
admin_username = "admin"
admin_password = "admin"
login_admin(admin_username, admin_password)

initial_balances = {f"seller{idx}": get_seller_balance(idx) for idx, _ in enumerate(SELLER_CREDENTIALS, start=1)}

# Verify each seller by their user ID (you might need to get seller IDs from the user list)
for seller_id in range(1, len(SELLER_CREDENTIALS) + 1):
    verify_seller(seller_id)

# Log in sellers after verification
for seller in SELLER_CREDENTIALS:
    login_seller(seller)


# Define the customer charge function
def charge_customer(amount, seller_username):
    phone_number = f"09{random.randint(100000000, 999999999)}"
    response = requests.post(
        f"{BASE_URL}/transactions/charge-customer/",
        json={
            "phone_number": phone_number,
            "amount": amount
        },
        headers={"Authorization": f"Bearer {AUTH_TOKENS[seller_username]}"}
    )
    if response.status_code == 201:
        with lock:
            total_charges[seller_username] += amount
        print(f"Charged {amount} to customer {phone_number} for seller {seller_username}")
    else:
        print(f"Failed to charge customer with {amount} charge: {response.status_code}, {response.text}")


# Define the balance increase function
def increase_balance(seller_username):
    amount = random.randint(100, 10000)
    response = requests.post(
        f"{BASE_URL}/transactions/balance-increase-requests/",
        json={"amount": amount},
        headers={"Authorization": f"Bearer {AUTH_TOKENS[seller_username]}"}
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


# Run the test with multithreading
def run_performance_test():
    with ThreadPoolExecutor(max_workers=10) as executor:
        for _ in range(NUM_REQUESTS):
            # Randomly select a seller
            seller_username = random.choice(list(AUTH_TOKENS.keys()))
            amount = random.randint(1, 50)

            # Submit customer charge task
            executor.submit(charge_customer, amount, seller_username)

            # Occasionally trigger a balance increase
            if random.random() < 0.1:
                executor.submit(increase_balance, seller_username)

        # Wait for all submitted tasks to complete
        executor.shutdown(wait=True)
    print("All tasks have completed.")


def get_seller_id(username):
    for idx, seller in enumerate(SELLER_CREDENTIALS, start=1):  # Start enumeration from 1 for ID
        if seller["username"] == username:
            return idx
    raise ValueError(f"Seller with username '{username}' not found.")


# Run the test
if __name__ == "__main__":
    run_performance_test()

    # Verify final balances for each seller
    for seller_username, initial_balance in initial_balances.items():
        expected_balance = initial_balance + total_increases[seller_username] - total_charges[seller_username]

        # Get the seller ID based on username
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
