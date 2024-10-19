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


class PositionCrudTest(TestCase):
    """
    Test operaci crud v modelu position.
    """
    def setUp(self):
        self.position = Position.objects.create(
            name="Manager"
        )


    def test_create_position(self):
        """
        Test vytvoreni pozice.
        """
        new_position = Position.objects.create(
            name="Kolo"
        )
        self.assertEqual(Position.objects.count(), 2)
        self.assertEqual(new_position.name, "Kolo")


    def test_read_position(self):
        """
        testovani cteni.
        """
        position = Position.objects.get(pk=self.position.pk)
        self.assertEqual(position.name, "Manager")

    def test_update_position(self):
        """
        testovani uprav pozice.
        """
        self.position.name = "Developer"
        self.position.save()
        updated_position = Position.objects.get(pk=self.position.pk)
        self.assertEqual(updated_position.name, "Developer")


    def test_delete_position(self):
        """
        mazani pozice
        """

        position_id = self.position.pk
        self.position.delete()
        with self.assertRaises(Position.DoesNotExist):
            Position.objects.get(pk=position_id)
