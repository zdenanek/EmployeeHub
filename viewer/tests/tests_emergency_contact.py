from django.test import TestCase
from viewer.models import EmergencyContact, UserProfile
from django.contrib.auth.models import User


# Unit TESTS
class EmergencyContractrStrMethodTest(TestCase):
    """
    Testuje metodu __str__ modelu EmergencyContractr, zda vrací správné řetězce.
    """

    def setUp(self,):
        user = User.objects.create(username="testuser")
        user_profile = UserProfile.objects.create(user=user)

        self.emergencycontact = EmergencyContact.objects.create(
            user_profile=user_profile,
            name="Test",
            phone_number="555444333",
        )

    def test_str_method(self):
        """
        Ověříme správný výsledek metody __str__.
        """
        self.assertEqual(str(self.emergencycontact), "Test - 555444333")
