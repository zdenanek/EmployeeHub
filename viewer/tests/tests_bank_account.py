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


