from django.test import TestCase
from viewer.models import BankAccount, UserProfile
from django.contrib.auth.models import User


# Unit TESTS
class BankAccountStrMethodTest(TestCase):
    """
    Testujeme metodu __str__ modelu BankAccount, zda vrací správné řetězce.
    """
    def setUp(self):
        """
        Musíme vytvořit uživatele a uživatelského profil protože jsou propojeni
        OneToOneField
        """
        user = User.objects.create(username="testuser")
        user_profile = UserProfile.objects.create(user=user)

        # Nastavení instance BankAccount pro testování
        self.bankaccount = BankAccount.objects.create(
            user_profile=user_profile,
            bank_name="Raifka",
            account_prefix="123455",
            account_number="12345544321",
            bank_code="1221"
        )


    def test_str_method(self):
        """
        Ověříme správný výsledek metody __str__.
        """
        self.assertEqual(str(self.bankaccount),"Raifka, 123455 - 12345544321/1221")


# Unit TESTS pro CRUD operace v modelu bank acount
class BankAccountCrudTest(TestCase):
    """
    Testujeme operace CRUD v modelu bankaccount.
    """
    def setUp(self):
        # Vytváříme user a userprofile.
        self.user = User.objects.create(username="testuser")
        self.user_profile = UserProfile.objects.create(user=self.user)

        # Vytvoreni banky
        self.bankaccount = BankAccount.objects.create(
            user_profile=self.user_profile,
            bank_name="Raifka",
            account_prefix="123455",
            account_number="12345544321",
            bank_code="1221"
        )


    def test_create_bankaccount(self):
        """
        Testujeme vytvoreni banovniho uctu.
        """
        new_user = User.objects.create(username="newuser")
        new_user_profile = UserProfile.objects.create(user=new_user)
        new_bankaccount = BankAccount.objects.create(
            user_profile=new_user_profile,
            bank_name="Polka",
            account_prefix="11111",
            account_number="2222",
            bank_code="1221"
        )
        self.assertEqual(BankAccount.objects.count(), 2)
        self.assertEqual(new_bankaccount.bank_name, "Polka")

    def test_read_bankaccount(self):
        """
        Testovani cteni vsech polozek uctu.
        """
        bankaccount = BankAccount.objects.get(pk=self.bankaccount.pk)
        self.assertEqual(bankaccount.bank_name,"Raifka")
        self.assertEqual(bankaccount.account_prefix, "123455")
        self.assertEqual(bankaccount.account_number, "12345544321")
        self.assertEqual(bankaccount.bank_code, "1221")


    def test_update_bankacount(self):
        """
        Testovani upravy uctu.
        """
        self.bankaccount.bank_name = "Raifka Test"
        self.bankaccount.account_prefix = "000111"
        self.bankaccount.account_number = "11111"
        self.bankaccount.bank_code = "3333"
        self.bankaccount.save()
        updated_bankaccount = BankAccount.objects.get(pk=self.bankaccount.pk)
        self.assertEqual(updated_bankaccount.bank_name, "Raifka Test")
        self.assertEqual(updated_bankaccount.account_number, "11111")
        self.assertEqual(updated_bankaccount.account_prefix, "000111")
        self.assertEqual(updated_bankaccount.bank_code, "3333")


    def test_delete_bankaccount(self):
        """
        Testovani mazani uctu.
        """
        bankaccount_id = self.bankaccount.pk
        self.bankaccount.delete()
        with self.assertRaises(BankAccount.DoesNotExist):
            BankAccount.objects.get(pk=bankaccount_id)
