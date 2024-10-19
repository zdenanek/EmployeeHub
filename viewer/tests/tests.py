from django.test import TestCase, LiveServerTestCase
from viewer.models import Contract, User, Customer
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User
import time


# Tento test ověřuje, že model Contract se správně inicializuje s požadovanými hodnotami při jeho vytváření.
class ContractModelTest(TestCase):
    def setUp(self):
        # Vytvoření uživatele a zákazníka
        self.user = User.objects.create(username="testuser")
        self.customer = Customer.objects.create(last_name="testcustomer")

    def test_contract_creation(self):
        # Vytvoření kontraktu
        contract = Contract.objects.create(
            contract_name="Test Contract",
            user=self.user,
            customer=self.customer,
            status="0",  # V procesu
        )

        # assertEqual metody kontrolují, zda jsou hodnoty nastavené na kontraktu správně
        self.assertEqual(contract.contract_name, "Test Contract")
        self.assertEqual(contract.user, self.user)
        self.assertEqual(contract.customer, self.customer)
        self.assertEqual(contract.status, "0")  # V procesu


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
        self.selenium.get(f'{self.live_server_url}/registration/login/')
        time.sleep(2)
        # Find the username and password input fields and fill them
        username_input = self.selenium.find_element(By.NAME, "username")
        password_input = self.selenium.find_element(By.NAME, "password")
        username_input.send_keys('admin')
        password_input.send_keys('admin')
        time.sleep(2)
        # Submit the form
        self.selenium.find_element(By.XPATH, '//button[@type="submit"]').click()
        time.sleep(2)

        # Test that we successfully logged in (check for a successful redirect or message)
        self.assertIn("Vítejte, admin!", self.selenium.page_source)
