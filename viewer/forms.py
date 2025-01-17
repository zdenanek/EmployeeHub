from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, inlineformset_factory, BaseInlineFormSet
from django import forms
from django.core.validators import RegexValidator
from .models import UserProfile, BankAccount, EmployeeInformation, EmergencyContact, SecurityQuestion
from viewer.models import Contract, Customer, SubContract, Comment


class SignUpForm(UserCreationForm):
    """
    Form for registering a new user.

    This form extends the UserCreationForm and includes fields for username, first name, last name and email.
    Newly registered users will be set as inactive (is_active = False) until their account is activated.
    """

    class Meta(UserCreationForm.Meta):
        # Specifies the fields to be included in the form.
        fields = ['username', 'first_name', 'last_name', 'email']

    def save(self, commit=True):
        """
        Saves the user instance.

        Before saving, it sets is_active to False, which means that the newly created user will not be able to access
        the application until the account is activated.

        :param commit: If True, a save to the database is performed.
        :return: An instance of the user is saved.
        """
        self.instance.is_active = False  # Uživatel bude neaktivní
        return super().save(commit)  # Zavolá se metoda save z nadřazené třídy


class ContractForm(ModelForm):
    """
    Form for creating and editing projects (contracts).
    """
    class Meta:
        # Specifies the model to be used for the form.
        model = Contract
        # Includes all fields of the Contract model.
        fields = "__all__"
        # Easier data entry using HTML5
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class CustomerForm(ModelForm):
    """
    Form for creating and editing customers.
    """
    phone_number = forms.CharField(
        max_length=15,
        label='Tel. číslo',
        validators=[RegexValidator(r'^\d+$', 'Pole musí obsahovat pouze číslice')],  # Validator for digits.
        initial="123456789",  # Initial value of the field
        required=True,  # This field is mandatory
        widget=forms.TextInput(attrs={'required': 'required'})  # HTML attribute for obligation.
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
    Form for creating and editing subcontracts.
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
    # Search query field with a maximum length of 256 characters.
    query = forms.CharField(
        label="Search",  # A field label for the user interface.
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
        model = EmergencyContact   # Specifies the model with which the form is associated.
        exclude = ('user_profile',)  # Excludes the ‘user_profile’ field from the form to prevent it from being modified by the user.


class BaseEmergencyContactFormSet(BaseInlineFormSet):
    """
       The form set provides a maximum of 2 contact persons, checks validity and raises an exception for non-valid data.
    """
    def clean(self):
        super().clean()
        total_forms = 0
        for form in self.forms:
            # Checks whether the form has been marked for removal
            if not form.cleaned_data.get('DELETE', False):
                # Checks whether the form is valid
                if not form.is_valid():
                    raise forms.ValidationError("Prosím opravte chyby ve formuláři.")
                total_forms += 1
        # Controls the maximum number of contact persons
        if total_forms > 2:
            raise forms.ValidationError("Můžete mít pouze dvě kontaktní osoby.")


# Definition of inline form set for EmergencyContact
EmergencyContactFormSet = inlineformset_factory(
    UserProfile,
    EmergencyContact,
    form=EmergencyContactForm,
    formset=BaseEmergencyContactFormSet,
    extra=2,  # Number of blank forms that will be displayed
    max_num=2,  # Maximum number of forms that can be added
    can_delete=True,  # Allows users to delete contacts
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
    A form for setting up security questions and answers for a user profile.

    This form allows users to select a security question and enter an answer that will be stored as cipher text.
    The answer is processed using a special method for setting the security answer.

    Form fields:
        - security_question: a selection of available security questions
        - security_answer: the answer to the security question, which is displayed as a password to ensure user privacy.
    """
    security_question = forms.ModelChoiceField(
        queryset=SecurityQuestion.objects.all(),
        label='Bezpečnostní otázka',
        required=True,
        empty_label=None  # Avoids blank question selection
    )
    security_answer = forms.CharField(
        widget=forms.PasswordInput,  # View as password
        label='Odpověď',
        required=True
    )

    class Meta:
        model = UserProfile
        fields = ['security_question', 'security_answer']

    def save(self, commit=True):
        """
        Saves an instance of the user profile with the security question and answer.

        Sets the encrypted answer using the `set_security_answer` method and then saves the profile if `commit` is set to True.
        """
        user_profile = super().save(commit=False)
        user_profile.set_security_answer(self.cleaned_data['security_answer'])
        if commit:
            user_profile.save()
        return user_profile


class SecurityAnswerForm(forms.Form):
    """
    A form for entering an answer to a security question. The answer is encrypted to protect user privacy.
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

# Validate the conditions for a new password on the backend, including confirmation of the new password.
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

    # Coupled clean method for all validation
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        new_password_confirm = cleaned_data.get('new_password_confirm')

        # Validation of new password - length, uppercase, lowercase, numbers
        if new_password:
            if len(new_password) < 8:
                self.add_error('new_password', 'Heslo musí mít alespoň 8 znaků.')
            if not any(char.isupper() for char in new_password):
                self.add_error('new_password', 'Heslo musí obsahovat alespoň jedno velké písmeno.')
            if not any(char.islower() for char in new_password):
                self.add_error('new_password', 'Heslo musí obsahovat alespoň jedno malé písmeno.')
            if not any(char.isdigit() for char in new_password):
                self.add_error('new_password', 'Heslo musí obsahovat alespoň jednu číslici.')

        # Validation of password matching
        if new_password and new_password_confirm and new_password != new_password_confirm:
            self.add_error('new_password_confirm', 'Hesla se neshodují.')

        return cleaned_data
