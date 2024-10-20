from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, inlineformset_factory, BaseInlineFormSet
from django import forms
from django.core.validators import RegexValidator
from .models import UserProfile, BankAccount, EmployeeInformation, EmergencyContact, SecurityQuestion
from viewer.models import Contract, Customer, SubContract, Comment


class SignUpForm(UserCreationForm):
    """
    Formulář pro registraci nového uživatele.

    Tento formulář rozšiřuje UserCreationForm a zahrnuje
    pole pro uživatelské jméno, jméno, příjmení a e-mail.
    Nově registrovaní uživatelé budou nastaveni jako neaktivní
    (is_active = False), dokud nebude jejich účet aktivován.
    """

    class Meta(UserCreationForm.Meta):
        # Určuje pole, která budou zahrnuta ve formuláři.
        fields = ['username', 'first_name', 'last_name', 'email']

    def save(self, commit=True):
        """
        Uloží instanci uživatele.

        Před uložením nastaví is_active na False, což znamená,
        že nově vytvořený uživatel nebude moci přistupovat
        k aplikaci, dokud nebude účet aktivován.

        :param commit: Pokud je True, provede se uložení do databáze.
        :return: Uložená instance uživatele.
        """
        self.instance.is_active = False  # Uživatel bude neaktivní
        return super().save(commit)  # Zavolá se metoda save z nadřazené třídy


class ContractForm(ModelForm):
    """
    Formulář pro vytváření a úpravu projektů (kontraktů).
    """
    class Meta:
        # Určuje model, který bude použit pro formulář.
        model = Contract
        # Zahrnuje všechna pole modelu Contract.
        fields = "__all__"
        # Jednodušší zadávání data s použitím HTML5
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class CustomerForm(ModelForm):
    """
    Formulář pro vytváření a úpravu zákazníků.
    """
    phone_number = forms.CharField(
        max_length=15,
        label='Tel. číslo',
        validators=[RegexValidator(r'^\d+$', 'Pole musí obsahovat pouze číslice')],  # Validátor pro číslice.
        initial="123456789",  # Počáteční hodnota pole
        required=True,  # Toto pole je povinné.
        widget=forms.TextInput(attrs={'required': 'required'})  # HTML atribut pro povinnost.
    )
    email_address = forms.EmailField(
        max_length=128,
        required=True
    )

    class Meta:
        model = Customer
        fields = "__all__"


class SubContractForm(ModelForm):
    """
    Formulář pro vytváření a úpravu podprojektů.
    """
    class Meta:
        model = SubContract
        fields = ['subcontract_name', 'user', 'status']


class SubContractFormUpdate(ModelForm):
    class Meta:
        model = SubContract
        fields = '__all__'


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class SearchForm(forms.Form):
    # Pole pro vyhledávací dotaz s maximální délkou 256 znaků.
    query = forms.CharField(
        label="Search",  # Označení pole pro uživatelské rozhraní.
        max_length=256
    )


class BankAccountForm(forms.ModelForm):
    account_number = forms.CharField(
        max_length=20,
        label='Číslo účtu',
        validators=[RegexValidator(r'^\d+$', 'Pole musí obsahovat pouze číslice')],
        required=True
    )
    account_prefix = forms.CharField(
        max_length=6,
        label='Předčíslí účtu',
        initial="000000",
        required=False
    )
    bank_code = forms.CharField(
        max_length=4,
        label='Kód banky',
        validators=[RegexValidator(r'^\d+$', 'Pole musí obsahovat pouze číslice')],
        required=True
    )
    bank_name = forms.CharField(
        max_length=50,
        label='Název banky',
        required=True
    )
    iban = forms.CharField(
        max_length=34,
        label='IBAN',
        required=False
    )
    swift_bic = forms.CharField(
        max_length=11,
        label='SWIFT/BIC',
        required=False
    )

    class Meta:
        model = BankAccount
        exclude = ('user_profile',)



class EmergencyContactForm(forms.ModelForm):
    name = forms.CharField(
        max_length=128,
        label='Jméno a příjmení',
        required=True,
        widget=forms.TextInput(attrs={'required': 'required'})
    )
    address = forms.CharField(
        max_length=128,
        label='Adresa',
        required=True,
        widget=forms.TextInput(attrs={'required': 'required'})
    )
    descriptive_number = forms.CharField(
        max_length=10,
        label='Popisné a orientační č.',
        required=True,
        widget=forms.TextInput(attrs={'required': 'required'})
    )
    postal_code = forms.CharField(
        max_length=10,
        label='PSČ',
        validators=[RegexValidator(r'^\d+$', 'Pole musí obsahovat pouze číslice')],
        required=True,
        widget=forms.TextInput(attrs={'required': 'required'})
    )
    city = forms.CharField(
        max_length=128,
        label='Město',
        required=True,
        widget=forms.TextInput(attrs={'required': 'required'})
    )
    phone_number = forms.CharField(
        max_length=15,
        label='Tel. číslo',
        validators=[RegexValidator(r'^\d+$', 'Pole musí obsahovat pouze číslice')],
        required=True,
        widget=forms.TextInput(attrs={'required': 'required'})
    )

    class Meta:
        model = EmergencyContact   # Určuje model, se kterým je formulář spojen.
        exclude = ('user_profile',)  # Vylučuje pole 'user_profile' z formuláře, aby se zabránilo jeho úpravě uživateli.


class BaseEmergencyContactFormSet(BaseInlineFormSet):
    """
       Formulářový set zajišťuje max. 2 kontaktní osoby, kontroluje platnost a vyvolává vyjímku při nevalidních datech.
    """
    def clean(self):
        super().clean()
        total_forms = 0
        for form in self.forms:
            # Zkontroluje, zda byl formulář označen k odstranění
            if not form.cleaned_data.get('DELETE', False):
                # Kontroluje, zda je formulář platný
                if not form.is_valid():
                    raise forms.ValidationError("Prosím opravte chyby ve formuláři.")
                total_forms += 1
        # Kontroluje maximální počet kontaktních osob
        if total_forms > 2:
            raise forms.ValidationError("Můžete mít pouze dvě kontaktní osoby.")


# Definice inline formulářového setu pro EmergencyContact
EmergencyContactFormSet = inlineformset_factory(
    UserProfile,
    EmergencyContact,
    form=EmergencyContactForm,
    formset=BaseEmergencyContactFormSet,
    extra=2,  # Počet prázdných formulářů, které se zobrazí
    max_num=2,  # Maximální počet formulářů, které lze přidat
    can_delete=True,  # Umožňuje uživatelům odstraňovat kontaktní osoby
)


class EmployeeInformationForm(forms.ModelForm):
    permament_address = forms.CharField(
        max_length=128,
        label='Adresa',
        required=True
    )
    permament_descriptive_number = forms.CharField(
        max_length=10,
        label='Číslo popisné',
        required=True
    )
    permament_postal_code = forms.CharField(
        max_length=5,
        label='PSČ',
        validators=[RegexValidator(r'^\d+$', 'Pole musí obsahovat pouze číslice')],
        required=True
    )
    city = forms.CharField(
        max_length=128,
        label='Město',
        required=True
    )
    phone_number = forms.CharField(
        max_length=15,
        label='Telefonní číslo',
        validators=[RegexValidator(r'^\d+$', 'Pole musí obsahovat pouze číslice')],
        required=True
    )

    class Meta:
        model = EmployeeInformation
        fields = [
            'permament_address',
            'permament_descriptive_number',
            'permament_postal_code',
            'city',
            'phone_number',
        ]


class SecurityQuestionForm(forms.ModelForm):
    """
    Formulář pro nastavení bezpečnostní otázky a odpovědi uživatelského profilu.

    Tento formulář umožňuje uživatelům vybrat bezpečnostní otázku a
    zadat odpověď, která bude uložena jako šifrovaný text. Odpověď je
    zpracována pomocí speciální metody pro nastavení bezpečnostní odpovědi.

    Políčka formuláře:
    - security_question: Výběr z dostupných bezpečnostních otázek.
    - security_answer: Odpověď na bezpečnostní otázku, která je
      zobrazena jako heslo pro zajištění soukromí uživatele.
    """
    security_question = forms.ModelChoiceField(
        queryset=SecurityQuestion.objects.all(),
        label='Bezpečnostní otázka',
        required=True,
        empty_label=None  # Zabraňuje prázdnému výběru otázky
    )
    security_answer = forms.CharField(
        widget=forms.PasswordInput,  # Zobrazit jako heslo
        label='Odpověď',
        required=True
    )

    class Meta:
        model = UserProfile
        fields = ['security_question', 'security_answer']

    def save(self, commit=True):
        """
        Uloží instanci uživatelského profilu s bezpečnostní otázkou a odpovědí.

        Nastaví šifrovanou odpověď pomocí metody `set_security_answer` a poté uloží profil, pokud je `commit` nastaven na True.
        """
        user_profile = super().save(commit=False)
        user_profile.set_security_answer(self.cleaned_data['security_answer'])
        if commit:
            user_profile.save()
        return user_profile


class SecurityAnswerForm(forms.Form):
    """
    Formulář pro zadání odpovědi na bezpečnostní otázku. Odpověď je šifrována pro ochranu soukromí uživatele.
    """
    security_question = forms.ModelChoiceField(
        queryset=SecurityQuestion.objects.all(),
        label='Bezpečnostní otázka',
        required=True,
        empty_label=None
    )
    security_answer = forms.CharField(
        widget=forms.PasswordInput,
        label='Odpověď',
        required=True
    )

# Validace podmínek pro nové heslo na backendu, včetně potvrzení nového hesla.
class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput,
        label='Nové heslo',
        required=True
    )
    new_password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label='Potvrzení nového hesla',
        required=True
    )

    # Spojená metoda clean pro veškerou validaci
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        new_password_confirm = cleaned_data.get('new_password_confirm')

        # Validace nového hesla - délka, velká písmena, malá písmena, číslice
        if new_password:
            if len(new_password) < 8:
                self.add_error('new_password', 'Heslo musí mít alespoň 8 znaků.')
            if not any(char.isupper() for char in new_password):
                self.add_error('new_password', 'Heslo musí obsahovat alespoň jedno velké písmeno.')
            if not any(char.islower() for char in new_password):
                self.add_error('new_password', 'Heslo musí obsahovat alespoň jedno malé písmeno.')
            if not any(char.isdigit() for char in new_password):
                self.add_error('new_password', 'Heslo musí obsahovat alespoň jednu číslici.')

        # Validace shody hesel
        if new_password and new_password_confirm and new_password != new_password_confirm:
            self.add_error('new_password_confirm', 'Hesla se neshodují.')

        return cleaned_data
