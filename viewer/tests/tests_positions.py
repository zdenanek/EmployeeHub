from django.test import TestCase
from viewer.models import Position


# Unit TESTS
class PositionStrMethodTest(TestCase):
    """
    Testuje metodu __str__ modelu Position, zda vrací správné řetězce.
    """
    def setUp(self):
        self.position = Position.objects.create(
            name="produkt manager"
        )

    def test_str_method(self):
        """
        Ověříme správný výsledek metody __str__.
        """
        self.assertEqual(str(self.position), "produkt manager")


