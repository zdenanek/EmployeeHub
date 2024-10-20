from django.test import TestCase
from viewer.models import UserProfile, Position, SecurityQuestion
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


class UserProfileCRUDTest(TestCase):
    """
    Testovani crud v user_profile
    """
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.position = Position.objects.create(name="Manager")
        self.security_question = SecurityQuestion.objects.create(question_text="Kolik je ti let?")
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            position=self.position,
            phone_number="123456789",
            security_question=self.security_question,
            security_answer="22"
        )

    def test_create_user_profile(self):
        """
        Vytvoreni user profilu.
        """
        new_user = User.objects.create(username="newuser")
        new_position = Position.objects.create(name="Developer")
        new_security_question = SecurityQuestion.objects.create(question_text="Oblibena barva?")

        new_user_profile = UserProfile.objects.create(
            user=new_user,
            position=new_position,
            phone_number="987654321",
            security_question=new_security_question,
            security_answer="Modra"
        )

        self.assertEqual(UserProfile.objects.count(), 2)
        self.assertEqual(new_user_profile.position.name, "Developer")
        self.assertEqual(new_user_profile.phone_number, "987654321")
        self.assertEqual(new_user_profile.security_question.question_text, "Oblibena barva?")
        self.assertEqual(new_user_profile.security_answer, "Modra")

    def test_read_user_profile(self):
        """
        Cteni user profilu.
        """
        user_profile = UserProfile.objects.get(pk=self.user_profile.pk)
        self.assertEqual(user_profile.phone_number, "123456789")
        self.assertEqual(user_profile.position.name, "Manager")
        self.assertEqual(user_profile.security_question.question_text, "Kolik je ti let?")
        self.assertEqual(user_profile.security_answer, "22")

    def test_update_user_profile(self):
        """
        upravy user profilu.
        """
        new_position = Position.objects.create(name="Developer")
        new_security_question = SecurityQuestion.objects.create(question_text="Oblibene jidlo?")

        self.user_profile.phone_number = "111222333"
        self.user_profile.security_question = new_security_question
        self.user_profile.security_answer = "Cina"
        self.user_profile.position = new_position
        self.user_profile.save()

        updated_user_profile = UserProfile.objects.get(pk=self.user_profile.pk)

        self.assertEqual(updated_user_profile.phone_number, "111222333")
        self.assertEqual(updated_user_profile.security_question.question_text, "Oblibene jidlo?")
        self.assertEqual(updated_user_profile.security_answer, "Cina")
        self.assertEqual(updated_user_profile.position.name, "Developer")

    def test_delete_user_profile(self):
        """
        smazani user profilu.
        """
        user_profile_id = self.user_profile.pk
        self.user_profile.delete()
        with self.assertRaises(UserProfile.DoesNotExist):
            UserProfile.objects.get(pk=user_profile_id)
