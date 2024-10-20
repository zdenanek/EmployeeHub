from django.test import TestCase, Client
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from viewer.models import Contract, Customer
from django.contrib.contenttypes.models import ContentType


class PermissionRequiredViewTests(TestCase):
    """
    Testy pro kontrolu přístupových oprávnění u pohledů ContractCreateView, CustomerCreateView a UserListView.
    """
    def setUp(self):
        # Vytvoření uživatele
        self.user = User.objects.create_user(username="testuser", password="password")

        # Vytvoření klienta pro simulaci požadavků
        self.client = Client()

        # Definice oprávnění pro model Contract a jejich přiřazení uživateli
        contract_content_type = ContentType.objects.get_for_model(Contract)  # Získání typu obsahu pro model Contract
        add_contract_permission = Permission.objects.get(  # Získání oprávnění pro přidání smlouvy
            codename='add_contract',
            content_type=contract_content_type
        )

        # Definice oprávnění pro model Customer
        customer_content_type = ContentType.objects.get_for_model(Customer)  # Získání typu obsahu pro model Customer
        add_customer_permission = Permission.objects.get(  # Získání oprávnění pro přidání zákazníka
            codename='add_customer',
            content_type=customer_content_type
        )

        # Definice oprávnění pro model User
        user_content_type = ContentType.objects.get_for_model(User)  # Získání typu obsahu pro model User
        auth_user_permission = Permission.objects.get(  # Získání oprávnění pro zobrazení uživatelů
            codename='view_user',
            content_type=user_content_type
        )

        # Definice URL adres pro testování
        self.contract_create_url = reverse('contract_create')  # URL pro vytvoření smlouvy
        self.customer_create_url = reverse('customer_create')  # URL pro vytvoření zákazníka
        self.user_list_url = reverse('employees')  # URL pro zobrazení seznamu zaměstnanců

        # Vytvoření testovacích uživatelů s různými oprávněními
        self.user_with_contract_permission = User.objects.create_user(username="contractuser", password="password")
        self.user_with_contract_permission.user_permissions.add(add_contract_permission)  # Přiřazení oprávnění pro přidání smlouvy

        self.user_with_customer_permission = User.objects.create_user(username="customeruser", password="password")
        self.user_with_customer_permission.user_permissions.add(add_customer_permission)  # Přiřazení oprávnění pro přidání zákazníka

        self.user_with_user_view_permission = User.objects.create_user(username="viewuser", password="password")
        self.user_with_user_view_permission.user_permissions.add(auth_user_permission)  # Přiřazení oprávnění pro zobrazení uživatelů

    def test_contract_create_view_no_permission(self):
        """
        Test, že uživatel bez oprávnění nemůže přistoupit k vytvoření smlouvy.
        """
        self.client.login(username="testuser", password="password")  # Přihlášení uživatele bez oprávnění
        response = self.client.get(self.contract_create_url)  # Pokus o přístup k vytvoření smlouvy
        self.assertEqual(response.status_code, 403)  # Očekáváme stav 403 - přístup odepřen

    def test_contract_create_view_with_permission(self):
        """
        Test, že uživatel s oprávněním může přistoupit k vytvoření smlouvy.
        """
        self.client.login(username="contractuser", password="password")  # Přihlášení uživatele s oprávněním
        response = self.client.get(self.contract_create_url)  # Pokus o přístup k vytvoření smlouvy
        self.assertEqual(response.status_code, 200)  # Očekáváme stav 200 - přístup povolen

    def test_customer_create_view_no_permission(self):
        """
        Test, že uživatel bez oprávnění nemůže přistoupit k vytvoření zákazníka.
        """
        self.client.login(username="testuser", password="password")  # Přihlášení uživatele bez oprávnění
        response = self.client.get(self.customer_create_url)  # Pokus o přístup k vytvoření zákazníka
        self.assertEqual(response.status_code, 403)  # Očekáváme stav 403 - přístup odepřen

    def test_customer_create_view_with_permission(self):
        """
        Test, že uživatel s oprávněním může přistoupit k vytvoření zákazníka.
        """
        self.client.login(username="customeruser", password="password")  # Přihlášení uživatele s oprávněním
        response = self.client.get(self.customer_create_url)  # Pokus o přístup k vytvoření zákazníka
        self.assertEqual(response.status_code, 200)  # Očekáváme stav 200 - přístup povolen

    def test_user_list_view_no_permission(self):
        """
        Test, že uživatel bez oprávnění nemůže přistoupit k zobrazení seznamu uživatelů.
        """
        self.client.login(username="testuser", password="password")  # Přihlášení uživatele bez oprávnění
        response = self.client.get(self.user_list_url)  # Pokus o přístup k zobrazení seznamu uživatelů
        self.assertEqual(response.status_code, 403)  # Očekáváme stav 403 - přístup odepřen

    def test_user_list_view_with_permission(self):
        """
        Test, že uživatel s oprávněním může přistoupit k zobrazení seznamu uživatelů.
        """
        self.client.login(username="viewuser", password="password")  # Přihlášení uživatele s oprávněním
        response = self.client.get(self.user_list_url)  # Pokus o přístup k zobrazení seznamu uživatelů
        self.assertEqual(response.status_code, 200)  # Očekáváme stav 200 - přístup povolen

    def test_views_with_other_permission(self):
        """
        Test, že uživatel s jiným oprávněním nemá přístup ke stránkám pro vytváření smlouvy, zákazníka ani ke seznamu uživatelů.
        """
        self.user.user_permissions.add(Permission.objects.get(codename='delete_customer'))  # Přiřazení oprávnění pro smazání zákazníka
        self.client.login(username="testuser", password="password")  # Přihlášení uživatele

        # Zkontrolujeme, že uživatel s oprávněním pro smazání zákazníka nemá přístup k ostatním pohledům
        response_contract = self.client.get(self.contract_create_url)  # Pokus o přístup k vytvoření smlouvy
        response_customer = self.client.get(self.customer_create_url)  # Pokus o přístup k vytvoření zákazníka
        response_user_list = self.client.get(self.user_list_url)  # Pokus o přístup k zobrazení seznamu uživatelů

        self.assertEqual(response_contract.status_code, 403)  # Očekáváme stav 403 - přístup odepřen
        self.assertEqual(response_customer.status_code, 403)  # Očekáváme stav 403 - přístup odepřen
        self.assertEqual(response_user_list.status_code, 403)  # Očekáváme stav 403 - přístup odepřen

