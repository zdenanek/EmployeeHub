from django.test import TestCase
from viewer.models import EmergencyContact, UserProfile, Position, SecurityQuestion
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


class EmergencyContactCRUDTest(TestCase):
    """
    Testovani crud v emergency_contact.
    """
    def setUp(self):
        # Vytvoření uživatele a uživatelského profilu
        self.user = User.objects.create(username="testuser")
        self.position = Position.objects.create(name="Manager")
        self.security_question = SecurityQuestion.objects.create(question_text="Kolik je ti let?")
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            position=self.position,
            phone_number="123456789",
            security_question=self.security_question,
            security_answer="22?"
        )

        # Vytvoření kontaktu pro případ nouze
        self.emergency_contact = EmergencyContact.objects.create(
            user_profile=self.user_profile,
            name="Petr Petr",
            address="Ulice 123",
            descriptive_number="12",
            postal_code="11000",
            city="Praha",
            phone_number="987654321"
        )

    def test_create_emergency_contact(self):
        """
        Testování vytvoření kontaktu.
        """
        new_emergency_contact = EmergencyContact.objects.create(
            user_profile=self.user_profile,
            name="Jana Test",
            address="Vedlejsi 456",
            descriptive_number="34",
            postal_code="12000",
            city="Brno",
            phone_number="123123123"
        )

        self.assertEqual(EmergencyContact.objects.count(), 2)
        self.assertEqual(new_emergency_contact.name, "Jana Test")
        self.assertEqual(new_emergency_contact.address, "Vedlejsi 456")
        self.assertEqual(new_emergency_contact.descriptive_number, "34")
        self.assertEqual(new_emergency_contact.postal_code, "12000")
        self.assertEqual(new_emergency_contact.city, "Brno")
        self.assertEqual(new_emergency_contact.phone_number, "123123123")

    def test_read_emergency_contact(self):
        """
        Testování čtení kontaktu.
        """
        emergency_contact = EmergencyContact.objects.get(pk=self.emergency_contact.pk)
        self.assertEqual(emergency_contact.name, "Petr Petr")
        self.assertEqual(emergency_contact.address, "Ulice 123")
        self.assertEqual(emergency_contact.descriptive_number, "12")
        self.assertEqual(emergency_contact.postal_code, "11000")
        self.assertEqual(emergency_contact.city, "Praha")
        self.assertEqual(emergency_contact.phone_number, "987654321")

    def test_update_emergency_contact(self):
        """
        Testování úpravy kontaktu.
        """
        self.emergency_contact.name = "Petr Pan"
        self.emergency_contact.address = "Neznam"
        self.emergency_contact.descriptive_number = "10"
        self.emergency_contact.phone_number = "111222333"
        self.emergency_contact.city = "Ostrava"
        self.emergency_contact.save()

        updated_emergency_contact = EmergencyContact.objects.get(pk=self.emergency_contact.pk)

        self.assertEqual(updated_emergency_contact.name, "Petr Pan")
        self.assertEqual(updated_emergency_contact.address, "Neznam")
        self.assertEqual(updated_emergency_contact.descriptive_number, "10")
        self.assertEqual(updated_emergency_contact.phone_number, "111222333")
        self.assertEqual(updated_emergency_contact.city, "Ostrava")

    def test_delete_emergency_contact(self):
        """
        Testování smazání kontaktu.
        """
        emergency_contact_id = self.emergency_contact.pk
        self.emergency_contact.delete()
        with self.assertRaises(EmergencyContact.DoesNotExist):
            EmergencyContact.objects.get(pk=emergency_contact_id)
