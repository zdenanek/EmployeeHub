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


class ContractCrudTest(TestCase):
    """
    Testujeme operace CRUD v modelu subcontract zda fungji spravne.
    """
    def setUp(self):
        # Vytváříme user a userprofile.
        self.user = User.objects.create(username="testuser")
        # self.user_profile = UserProfile.objects.create(user=self.user)

        # Vytvoreni zakaznika
        self.customer = Customer.objects.create(
            first_name="Franta",
            last_name="Pepa"
        )

        # Vytvoreni projektu
        self.contract = Contract.objects.create(
            user=self.user,
            customer=self.customer,
            contract_name= "Tasky",
            status= "0"
        )



    def test_create_contract(self):
        """
        Testujeme vytvoreni projektu.
        """
        new_contract = Contract.objects.create(
            user=self.user,
            customer=self.customer,
            contract_name="Eshop",
            status="0"
        )
        self.assertEqual(Contract.objects.count(), 2)
        self.assertEqual(new_contract.contract_name, "Eshop")


    def test_read_contract(self):
        contract = Contract.objects.get(pk=self.contract.pk)
        self.assertEqual(contract.contract_name, "Tasky")
        self.assertEqual(contract.status, "0")


    def test_update_conract(self):
        """
        Testovani uprav projektu.
        """
        self.contract.contract_name = "Test projekt"
        self.contract.status = "1"
        self.contract.save()
        updated_contract = Contract.objects.get(pk=self.contract.pk)
        self.assertEqual(updated_contract.contract_name, "Test projekt")
        self.assertEqual(updated_contract.status, "1")


    def test_delete_contract(self):
        """
        Mazani contractu.
        """
        contract_id = self.contract.pk
        self.contract.delete()
        with self.assertRaises(Contract.DoesNotExist):
            Contract.objects.get(pk=contract_id)
