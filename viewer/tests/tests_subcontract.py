from django.test import TestCase
from viewer.models import SubContract, UserProfile, Contract, Customer
from django.contrib.auth.models import User


# Unit TESTS
class SubcontractStrMethodTest(TestCase):
    """
    Testuje metodu __str__ modelu Subcontract, zda vrací správné řetězce.
    """
    def setUp(self):
        user = User.objects.create(username="testuser")
        user_profile = UserProfile.objects.create(user=user)

        customer = Customer.objects.create(
            first_name="franta",
            last_name="pepa"
        )

        contract = Contract.objects.create(
            contract_name="test",
            customer=customer,
            user=user
        )

        self.subcontract = SubContract.objects.create(
            user=user,
            subcontract_name="neco",
            contract=contract,
            subcontract_number=1
        )

    def test_str_method(self):
        """
        Ověříme zda metoda __str__ vrací 'Název zákazníka: Test Test1'.
        """
        self.assertEqual(str(self.subcontract), "Podprojekt: neco 1-1")
