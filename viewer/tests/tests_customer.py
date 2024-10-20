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
        self.assertEqual(str(self.customer), "Zákazník: Test Test1")


class CustomerCrudTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Franta",
            last_name="Pepa",
            phone_number="666555444",
            email_address="nemam@mail.com"
        )


    def test_create_customer(self):
        """
        Vytvoreni zakaznika.
        """
        new_customer = Customer.objects.create(
            first_name= "Pavel",
            last_name= "Petr",
            phone_number="444333222",
            email_address="test@test.com"
        )
        self.assertEqual(Customer.objects.count(), 2)
        self.assertEqual(new_customer.first_name, "Pavel")
        self.assertEqual(new_customer.last_name, "Petr")
        self.assertEqual(new_customer.phone_number, "444333222")
        self.assertEqual(new_customer.email_address, "test@test.com")


    def test_read_customer(self):
        customer = Customer.objects.get(pk=self.customer.pk)
        self.assertEqual(customer.first_name, "Franta")
        self.assertEqual(customer.last_name, "Pepa")
        self.assertEqual(customer.phone_number, "666555444")
        self.assertEqual(customer.email_address, "nemam@mail.com")


    def test_update_customer(self):
        """
        upravy zakaznika
        """
        self.customer.first_name = "Jana"
        self.customer.last_name = "Tada"
        self.customer.phone_number = "121212121"
        self.customer.email_address = "tada@email.com"
        self.customer.save()
        updated_customer = Customer.objects.get(pk=self.customer.pk)
        self.assertEqual(updated_customer.first_name, "Jana")
        self.assertEqual(updated_customer.last_name, "Tada")
        self.assertEqual(updated_customer.phone_number, "121212121")
        self.assertEqual(updated_customer.email_address, "tada@email.com")


    def test_delete_customer(self):
        """
        mazani zakaznika
        """
        customer_id = self.customer.pk
        self.customer.delete()
        with self.assertRaises(Customer.DoesNotExist):
            Customer.objects.get(pk=customer_id)





