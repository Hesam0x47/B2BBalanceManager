from rest_framework import status
from rest_framework.reverse import reverse

from apps.transactions.models import BalanceIncreaseRequestModel

BALANCE_INCREASE_REQUESTS_URL = reverse('balance-increase-requests')


class IncreaseBalanceTestMixins:

    def increase_balance(self, amount: str, expected_status_code=status.HTTP_201_CREATED):
        payload = {
            'amount': amount
        }

        response = self.client.post(BALANCE_INCREASE_REQUESTS_URL, payload, format='json')
        self.assertEqual(response.status_code, expected_status_code, msg=response.json())

        return response

    def approve_increase_balance_request(self, pk: int, expected_status_code=status.HTTP_200_OK):
        balance_increase_request_approval_url = reverse(
            'balance-increase-requests-approval',
            kwargs={"pk": pk, "action": BalanceIncreaseRequestModel.STATUS_ACCEPTED},
        )
        response = self.client.patch(balance_increase_request_approval_url)

        self.assertEqual(response.status_code, expected_status_code, msg=response.json())

        return response

    def reject_increase_balance_request(self, pk: int, expected_status_code=status.HTTP_200_OK):
        recharge_status_change_rejected_url = reverse(
            'balance-increase-requests-approval',
            kwargs={"pk": pk , "action": BalanceIncreaseRequestModel.STATUS_REJECTED},
        )
        response = self.client.patch(recharge_status_change_rejected_url)

        self.assertEqual(response.status_code, expected_status_code, msg=response.json())

        return response
