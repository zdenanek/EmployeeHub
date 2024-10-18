from django.test import TestCase
from viewer.models import UserProfile, Position
from django.contrib.auth.models import User


# Unit TESTS
class UserProfileStrMethodTest(TestCase):
    """
    Testuje metodu __str__ modelu Customer, zda vrací správné řetězce.
    """
    def setUp(self):
        user = User.objects.create(username="testuser")
        posititon = Position.objects.create(name="manager")

        self.userprofile = UserProfile.objects.create(
            user=user,
            position=posititon,
            phone_number="111222333"
        )

    def test_str_method(self):
        """
        Ověříme zda metoda __str__ vrací 'Název zákazníka: Test Test1'.
        """
        self.assertEqual(str(self.userprofile), "testuser - manager - 111222333")
