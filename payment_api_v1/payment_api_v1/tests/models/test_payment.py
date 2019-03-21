from decimal import Decimal
from unittest import mock

from django.test import TestCase

from payment_api_v1.models import Account, Payment, PaymentStatus


class PaymentTestCase(TestCase):

    def setUp(self):
        self.account_from = Account.objects.create(email='test@example.com')
        self.account_from.create_balance('RUB')
        self.balance_from = self.account_from.create_balance('PHP')
        self.balance_from.money.amount = '1000'
        self.balance_from.save()

        self.account_to = Account.objects.create(email='test@example.com')
        self.balance_to = self.account_to.create_balance('PHP')
        self.balance_to.money = '500'
        self.balance_to.save()

    def make_payment_same_currency_enough_money_mock_processing(self):
        with mock.patch('payment_api_v1.tasks.process_payment') as process_payment_mock:
            payment = Payment.objects.create(
                balance_from=self.balance_from,
                balance_to=self.balance_to,
                amount=Decimal(555.55)
            )
            process_payment_mock.assert_called_once_with(self.balance_from.id, self.balance_to.id, amount)
        self.assertEqual(payment.status, PaymentStatus.PENDING)
        self.assertEqual(self.balance_from.money.amount, Decimal(1000))
        self.assertEqual(self.balance_to.money.amount, Decimal(500))

    def make_payment_same_currency_enough_money_processed(self):
        payment = Payment.objects.create(
            balance_from=self.balance_from,
            balance_to=self.balance_to,
            amount=Decimal(555.55)
        )
        self.assertEqual(payment.status, PaymentStatus.SUCCESS)
        self.assertEqual(self.balance_from.money.amount, Decimal(1000)-Decimal(555.55))
        self.assertEqual(self.balance_to.money.amount, Decimal(500)+Decimal(555.55))

    def make_payment_same_currency_not_enough_money_processed(self):
        payment = Payment.objects.create(
            balance_from=self.balance_from,
            balance_to=self.balance_to,
            amount=Decimal(1555.55)
        )
        self.assertEqual(payment.status, PaymentStatus.NOT_ENOUGH_MONEY)
        self.assertEqual(self.balance_from.money.amount, Decimal(1000))
        self.assertEqual(self.balance_to.money.amount, Decimal(500))
