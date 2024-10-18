from django.test import TestCase
from viewer.models import Comment, Movie, Genre
from datetime import date

from django.contrib.auth import get_user_model
from viewer.models import Building

from viewer.models import Actor, Movie, Genre
from datetime import date


class ActorModelTest(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Drama")
        self.movie = Movie.objects.create(
            title="Sad Movie",
            genre=self.genre,
            rating=9,
            released=date(2020, 8, 22)
        )
        self.actor = Actor.objects.create(first_name="John", last_name="Doe")
        self.actor.movies.add(self.movie)

    def test_actor_creation(self):
        self.assertEqual(self.actor.first_name, "John")
        self.assertEqual(self.actor.last_name, "Doe")
        self.assertEqual(self.actor.movies.count(), 1)
        self.assertIn(self.movie, self.actor.movies.all())

    def test_actor_str(self):
        self.assertEqual(str(self.actor), "John Doe")


User = get_user_model()


class BuildingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.building = Building.objects.create(company="TechCorp", floors=5, user=self.user)

    def test_building_creation(self):
        self.assertEqual(self.building.company, "TechCorp")
        self.assertEqual(self.building.floors, 5)
        self.assertEqual(self.building.user.username, "testuser")


class CommentModelTest(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Horror")
        self.movie = Movie.objects.create(
            title="Scary Movie",
            genre=self.genre,
            rating=7,
            released=date(2022, 10, 1)
        )
        self.comment = Comment.objects.create(movie=self.movie, text="Terrifying!")

    def test_comment_creation(self):
        self.assertEqual(self.comment.text, "Terrifying!")
        self.assertEqual(self.comment.movie.title, "Scary Movie")

    def test_comment_str(self):
        self.assertEqual(str(self.comment), "Komentář: Terrifying! k filmu Scary Movie")


from django.test import TestCase


class GenreModelTest(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Action")

    def test_genre_creation(self):
        self.assertEqual(self.genre.name, "Action")
        self.assertEqual(Genre.objects.count(), 2)


# pip install selenium
# tests.py
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User
import time


class MySeleniumTests(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set up the WebDriver (make sure the path is correct if needed)
        cls.selenium = webdriver.Chrome()
        cls.selenium.implicitly_wait(10)

        cls.admin_user = User.objects.create_superuser(
            username='admin',
            password='admin',
            email='admin@example.com'
        )

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_login(self):
        # Access the live server URL
        self.selenium.get(f'{self.live_server_url}/accounts/login/')
        time.sleep(2)
        # Find the username and password input fields and fill them
        username_input = self.selenium.find_element(By.NAME, "username")
        password_input = self.selenium.find_element(By.NAME, "password")
        username_input.send_keys('admin')
        password_input.send_keys('admin')
        time.sleep(2)
        # Submit the form
        self.selenium.find_element(By.XPATH, '//input[@type="submit"]').click()
        time.sleep(2)

        # Test that we successfully logged in (check for a successful redirect or message)
        self.assertIn("User logged in: admin - Logout", self.selenium.page_source)


