from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from viewer.models import UserProfile, SecurityQuestion


class PasswordResetValidationTests(TestCase):
    def setUp(self):
        # Nastavení testovacího uživatele a profilu
        self.user = User.objects.create_user(username="testuser", password="oldpassword")

        # Vytvoření bezpečnostní otázky pro uživatele
        security_question = SecurityQuestion.objects.create(question_text="Jak se jmenuje váš mazlíček?")

        # Vytvoření uživatelského profilu s odpovědí na bezpečnostní otázku
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            security_question=security_question,
            security_answer="Fluffy"
        )

        # Definice URL pro jednotlivé kroky procesu resetu hesla
        self.password_reset_step_1_url = reverse('password_reset_step_1')
        self.password_reset_step_2_url = reverse('password_reset_step_2')
        self.password_reset_step_3_url = reverse('password_reset_step_3')


    def test_password_reset_flow(self):
        # Krok 1: Odeslání uživatelského jména
        response = self.client.post(self.password_reset_step_1_url, {'username': 'testuser'})
        self.assertEqual(response.status_code, 302)  # Ověříme, že došlo k přesměrování na krok 2

        # Krok 2: Načtení stránky s bezpečnostní otázkou
        response = self.client.get(self.password_reset_step_2_url)
        self.assertEqual(response.status_code, 200)  # Ověříme, že stránka je načtena úspěšně

        # Krok 2: Odpověď na bezpečnostní otázku
        response = self.client.post(self.password_reset_step_2_url, {'security_answer': 'Fluffy'})
        self.assertEqual(response.status_code, 200)  # Ověříme, že stránka pro krok 3 je načtena úspěšně

        # Krok 3: Testování validace pro krátké heslo
        response = self.client.post(self.password_reset_step_3_url, {
            'new_password': 'Short1',
            'new_password_confirm': 'Short1'
        })
        self.assertContains(response, 'Heslo musí mít alespoň 8 znaků.')  # Ověříme, že se zobrazí chybová zpráva


    def test_password_mismatch(self):
        # Provede kroky 1 a 2
        self.client.post(self.password_reset_step_1_url, {'username': 'testuser'})
        self.client.post(self.password_reset_step_2_url, {'security_answer': 'Fluffy'})

        # Krok 3: Hesla se neshodují
        response = self.client.post(self.password_reset_step_3_url, {
            'new_password': 'Password123',
            'new_password_confirm': 'Password321'
        })
        self.assertContains(response, 'Hesla se neshodují.')  # Ověříme, že se zobrazí chybová zpráva


    def test_password_small_letter(self):
        # Provede kroky 1 a 2
        self.client.post(self.password_reset_step_1_url, {'username': 'testuser'})
        self.client.post(self.password_reset_step_2_url, {'security_answer': 'Fluffy'})

        # Krok 3: Heslo neobsahuje malé písmeno
        response = self.client.post(self.password_reset_step_3_url, {
            'new_password': 'PASSWORD321',
            'new_password_confirm': 'PASSWORD321'
        })
        self.assertContains(response, 'Heslo musí obsahovat alespoň jedno malé písmeno.')  # Ověříme chybovou zprávu


    def test_password_big_letter(self):
        # Provede kroky 1 a 2
        self.client.post(self.password_reset_step_1_url, {'username': 'testuser'})
        self.client.post(self.password_reset_step_2_url, {'security_answer': 'Fluffy'})

        # Krok 3: Heslo neobsahuje velké písmeno
        response = self.client.post(self.password_reset_step_3_url, {
            'new_password': 'password321',
            'new_password_confirm': 'password321'
        })
        self.assertContains(response, 'Heslo musí obsahovat alespoň jedno velké písmeno.')  # Ověříme chybovou zprávu


    def test_password_number(self):
        # Provede kroky 1 a 2
        self.client.post(self.password_reset_step_1_url, {'username': 'testuser'})
        self.client.post(self.password_reset_step_2_url, {'security_answer': 'Fluffy'})

        # Krok 3: Heslo neobsahuje číslici
        response = self.client.post(self.password_reset_step_3_url, {
            'new_password': 'Password',
            'new_password_confirm': 'Password'
        })
        self.assertContains(response, 'Heslo musí obsahovat alespoň jednu číslici.')  # Ověříme chybovou zprávu


    def test_multiple_password_errors(self):
        # Provede kroky 1 a 2
        self.client.post(self.password_reset_step_1_url, {'username': 'testuser'})
        self.client.post(self.password_reset_step_2_url, {'security_answer': 'Fluffy'})

        # Krok 3: Heslo '123' má chyby - krátké, neobsahuje malé ani velké písmeno
        response = self.client.post(self.password_reset_step_3_url, {
            'new_password': '123',
            'new_password_confirm': '123'
        })

        # Ověříme, že se zobrazí všechny tři chybové zprávy
        self.assertContains(response, 'Heslo musí mít alespoň 8 znaků.')
        self.assertContains(response, 'Heslo musí obsahovat alespoň jedno malé písmeno.')
        self.assertContains(response, 'Heslo musí obsahovat alespoň jedno velké písmeno.')


    def test_valid_password(self):
        # Krok 1: Zadání uživatelského jména
        self.client.post(self.password_reset_step_1_url, {'username': 'testuser'})

        # Krok 2: Odpověď na bezpečnostní otázku
        self.client.post(self.password_reset_step_2_url, {'security_answer': 'Fluffy'})

        # Krok 3: Zadání správného hesla
        response = self.client.post(self.password_reset_step_3_url, {
            'new_password': 'Password123',
            'new_password_confirm': 'Password123'
        })
        self.assertEqual(response.status_code, 302)  # Po úspěšné změně hesla očekáváme přesměrování


class EmployeeInformationValidationTests(TestCase):
    """
    testujeme validaci dat uzivatele u zamestnaneckych informaci
    """
    def setUp(self):
        # Vytvoření uživatele a přihlášení
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username='testuser', password='password')
        # URL pro editační režim profilu zaměstnance
        self.profile_url = reverse('employee_profile') + '?edit=information'

    def test_valid_phone_number_and_postal_code(self):
        """
        Testuje validní telefonní číslo pro Employee Information.
        """
        # Pošleme validní data s parametrem edit=information
        response = self.client.post(self.profile_url, {
            'permament_address': 'Nějaká adresa',
            'permament_descriptive_number': '12',
            'permament_postal_code': '11111',
            'city': 'Praha',
            'phone_number': '123456789',
            'employee_information_submit': 'Uložit',  # Přidání tlačítka pro submit
        })
        # Očekáváme přesměrování, protože validace prošla
        self.assertEqual(response.status_code, 302)  # Ověříme, že došlo k přesměrování po úspěšném odeslání

    def test_invalid_postal_code(self):
        """
        Testuje neplatné PSČ v Employee Information.
        """
        # Pošleme data s neplatným PSČ
        response = self.client.post(self.profile_url, {
            'permament_address': 'Nějaká adresa',
            'permament_descriptive_number': '12',
            'permament_postal_code': 'abcde',  # Neplatné PSČ
            'city': 'Praha',
            'phone_number': '123456789',
            'employee_information_submit': 'Uložit',  # Přidání tlačítka pro submit
        })
        self.assertContains(response, 'Pole musí obsahovat pouze číslice')  # Očekávaná chybová zpráva

    def test_invalid_phone_number(self):
        """
        Testuje neplatné telefonní číslo v Employee Information.
        """
        # Pošleme data s neplatným telefonním číslem
        response = self.client.post(self.profile_url, {
            'permament_address': 'Nějaká adresa',
            'permament_descriptive_number': '12',
            'permament_postal_code': '11111',
            'city': 'Praha',
            'phone_number': 'phone123',  # Neplatné telefonní číslo
            'employee_information_submit': 'Uložit',  # Přidání tlačítka pro submit
        })
        # Zkontrolujeme chyby
        self.assertContains(response, 'Pole musí obsahovat pouze číslice')  # Očekávaná chybová zpráva


class BankAccountValidationTests(TestCase):
    """
    testujeme validaci dat uzivatele u b.u.
    """
    def setUp(self):
        """
        Nastavení testu: Vytvoří testovacího uživatele a přihlásí ho.
        """
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username='testuser', password='password')
        # Získání URL profilu zaměstnance pro použití v testech
        self.profile_url = reverse('employee_profile')

    def test_valid_bank_account(self):
        """
        Testuje validní (správně zadané) údaje bankovního účtu.
        """
        # Načteme stránku s formulářem pro bankovní údaje (sekce bankovního účtu)
        self.client.get(f"{self.profile_url}?edit=account")

        # Pošleme POST požadavek s validními údaji
        response = self.client.post(self.profile_url, {
            'account_number': '123456789012',
            'bank_code': '1234',
            'bank_name': 'Moje banka',
            'bank_account_submit': 'true',
        })

        # Ověříme, že proběhne přesměrování po úspěšném uložení (status code 302)
        self.assertEqual(response.status_code, 302)

    def test_invalid_account_number(self):
        """
        Testuje neplatné číslo účtu (obsahuje nepovolené znaky).
        """
        # Načteme stránku s formulářem pro bankovní údaje
        self.client.get(f"{self.profile_url}?edit=account")

        # Pošleme POST požadavek s neplatným číslem účtu (obsahuje písmena)
        response = self.client.post(self.profile_url, {
            'account_number': 'abc123',
            'bank_code': '1234',
            'bank_name': 'Moje banka',
            'bank_account_submit': 'true',     # Potvrzení, že formulář odesíláme
        })

        # Ověříme, že se zobrazí chybová zpráva "Pole musí obsahovat pouze číslice"
        self.assertContains(response, 'Pole musí obsahovat pouze číslice')

    def test_invalid_bank_code(self):
        """
        Testuje neplatný kód banky (obsahuje nepovolené znaky).
        """
        # Načteme stránku s formulářem pro bankovní údaje
        self.client.get(f"{self.profile_url}?edit=account")

        # Pošleme POST požadavek s neplatným kódem banky (obsahuje písmena)
        response = self.client.post(self.profile_url, {
            'account_number': '123456789012',
            'bank_code': 'abcd',
            'bank_name': 'Moje banka',
            'bank_account_submit': 'true',
        })

        # Ověříme, že se zobrazí chybová zpráva "Pole musí obsahovat pouze číslice"
        self.assertContains(response, 'Pole musí obsahovat pouze číslice')


class EmergencyContactValidationTests(TestCase):
    """
    testujeme validaci dat uzivatele u kontaktni osoby
    """
    def setUp(self):
        # Vytvoříme testovacího uživatele a přihlásíme ho
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username='testuser', password='password')
        # URL profilu zaměstnance
        self.profile_url = reverse('employee_profile') + '?edit=emergency_contacts'

    def test_valid_emergency_contact(self):
        """
        Testuje validní údaje pro nouzový kontakt.
        """
        response = self.client.post(self.profile_url, {
            'emergency_contacts-TOTAL_FORMS': '1',
            'emergency_contacts-INITIAL_FORMS': '0',
            'emergency_contacts-MIN_NUM_FORMS': '0',
            'emergency_contacts-MAX_NUM_FORMS': '2',
            'emergency_contacts-0-name': 'Pavel Novák',
            'emergency_contacts-0-address': 'Nějaká adresa',
            'emergency_contacts-0-descriptive_number': '12',
            'emergency_contacts-0-postal_code': '11111',
            'emergency_contacts-0-city': 'Praha',
            'emergency_contacts-0-phone_number': '123456789',
            'emergency_contact_submit': 'Uložit',  # Potvrzení odeslání formuláře
        })

        # Ověříme, že proběhne přesměrování po úspěšném uložení (status code 302)
        self.assertEqual(response.status_code, 302)

    def test_invalid_phone_number(self):
        """
        Testuje neplatné telefonní číslo v nouzových kontaktech.
        """
        response = self.client.post(self.profile_url, {
            'emergency_contacts-TOTAL_FORMS': '1',
            'emergency_contacts-INITIAL_FORMS': '0',
            'emergency_contacts-MIN_NUM_FORMS': '0',
            'emergency_contacts-MAX_NUM_FORMS': '2',
            'emergency_contacts-0-name': 'Pavel Novák',
            'emergency_contacts-0-address': 'Nějaká adresa',
            'emergency_contacts-0-descriptive_number': '12',
            'emergency_contacts-0-postal_code': '11111',
            'emergency_contacts-0-city': 'Praha',
            'emergency_contacts-0-phone_number': 'phone123',  # Neplatné telefonní číslo
            'emergency_contact_submit': 'Uložit',  # Potvrzení odeslání formuláře
        })

        # Ověříme, že formulář vrátí očekávanou chybovou zprávu
        self.assertContains(response, 'Pole musí obsahovat pouze číslice')

    def test_invalid_postal_code(self):
        """
        Testuje neplatné PSČ v nouzových kontaktech.
        """
        response = self.client.post(self.profile_url, {
            'emergency_contacts-TOTAL_FORMS': '1',
            'emergency_contacts-INITIAL_FORMS': '0',
            'emergency_contacts-MIN_NUM_FORMS': '0',
            'emergency_contacts-MAX_NUM_FORMS': '2',
            'emergency_contacts-0-name': 'Pavel Novák',
            'emergency_contacts-0-address': 'Nějaká adresa',
            'emergency_contacts-0-descriptive_number': '12',
            'emergency_contacts-0-postal_code': 'abcde',  # Neplatné PSČ
            'emergency_contacts-0-city': 'Praha',
            'emergency_contacts-0-phone_number': '123456789',
            'emergency_contact_submit': 'Uložit',  # Potvrzení odeslání formuláře
        })

        # Ověříme, že formulář vrátí očekávanou chybovou zprávu
        self.assertContains(response, 'Pole musí obsahovat pouze číslice')