from django.test import TestCase
from viewer.models import Contract, UserProfile, Customer
from django.contrib.auth.models import User


# Unit TESTS
class ContractStrMethodTest(TestCase):
    """
    Testuje metodu __str__ modelu Contract, zda vrací správné řetězce.
    """
    def setUp(self):
        User.objects.create(username="testuser")

        customer = Customer.objects.create(
            first_name="Jan",
            last_name="Novák",
            email_address="jan.novak@example.com"
        )

        self.contract = Contract.objects.create(
            contract_name="Škodovka",
            customer=customer
        )

    def test_str_method(self):
        """
        Ověříme správný výsledek metody __str__.
        """
        self.assertEqual(str(self.contract), "Zakázka: Škodovka")
