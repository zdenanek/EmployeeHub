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


# Unit TESTS pro CRUD operace v modelu podrojekty
class SubcontractCrudTest(TestCase):
    """
    Testujeme operace CRUD v modelu subcontract zda fungji spravne.
    """
    def setUp(self):
        # Vytváříme user a userprofile.
        self.user = User.objects.create(username="testuser")
        self.user_profile = UserProfile.objects.create(user=self.user)

        # Vytvoreni zakaznika
        self.customer = Customer.objects.create(
            first_name="Franta",
            last_name="Pepa"
        )

        # Vytvoreni projektu
        self.contract = Contract.objects.create(
            contract_name="Test Contract",
            customer=self.customer,
            user=self.user
        )

        # Vytvoreni podprojektu
        self.subcontract = SubContract.objects.create(
            user=self.user,
            subcontract_name="Test SubContract",
            contract=self.contract,
            subcontract_number=1
        )

    def test_create_subcontract(self):
        """
        Testujeme vytvoreni podprojektu.
        """
        new_subcontract = SubContract.objects.create(
            user=self.user,
            subcontract_name="New SubContract",
            contract=self.contract,
            subcontract_number=2
        )
        self.assertEqual(SubContract.objects.count(), 2)
        self.assertEqual(new_subcontract.subcontract_name, "New SubContract")

    def test_read_subcontract(self):
        """
        Testovani cteni podkontraktu.
        """
        subcontract = SubContract.objects.get(pk=self.subcontract.pk)
        self.assertEqual(subcontract.subcontract_name, "Test SubContract")

    def test_update_subcontract(self):
        """
        Testovani upravy podkontraktu.
        """
        self.subcontract.subcontract_name = "Updated SubContract"
        self.subcontract.save()
        updated_subcontract = SubContract.objects.get(pk=self.subcontract.pk)
        self.assertEqual(updated_subcontract.subcontract_name, "Updated SubContract")

    def test_delete_subcontract(self):
        """
        Testovani smazani podkontraktu.
        """
        subcontract_id = self.subcontract.pk
        self.subcontract.delete()
        with self.assertRaises(SubContract.DoesNotExist):
            SubContract.objects.get(pk=subcontract_id)
