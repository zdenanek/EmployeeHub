from django.test import TestCase
from viewer.models import Customer


# Unit TESTS
class CustomerStrMethodTest(TestCase):
    """
    Testuje metodu __str__ modelu Customer, zda vrací správné řetězce.
    """
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Test",
            last_name="Test1",
        )

    def test_str_method(self):
        """
        Ověříme zda metoda __str__ vrací 'Název zákazníka: Test Test1'.
        """
        self.assertEqual(str(self.customer), "Název zákazníka: Test Test1")


