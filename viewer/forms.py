import re

from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db.models import CharField
from django.forms import ModelForm, Form, CharField, inlineformset_factory, BaseInlineFormSet
from django import forms
from django.core.validators import RegexValidator
from .models import UserProfile, BankAccount, EmployeeInformation, EmergencyContact, SecurityQuestion

from viewer.models import Contract, Customer, SubContract, Comment


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ['username', 'first_name', 'last_name', 'email']

    def save(self, commit=True):
        self.instance.is_active = False
        return super().save(commit)


class ContractForm(ModelForm):
    class Meta:
        model = Contract
        fields = "__all__"


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"


class SubContractForm(ModelForm):
    class Meta:
        model = SubContract
        fields = ['subcontract_name', 'user', 'status']
        # fields = '__all__'


class SubContractFormUpdate(ModelForm):
    class Meta:
        model = SubContract
        fields = '__all__'


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class SearchForm(forms.Form):
    query = forms.CharField(label="Search", max_length=256)


class BankAccountForm(forms.ModelForm):
    account_number = forms.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\d+$', 'Pole musí obsahovat pouze číslice')],
        required=True
    )
    account_prefix = forms.CharField(
        max_length=6,
        initial="000000",
        required=False
    )
    bank_code = forms.CharField(
        max_length=4,
        validators=[RegexValidator(r'^\d+$', 'Pole musí obsahovat pouze číslice')],
        required=True
    )
    bank_name = forms.CharField(
        max_length=50,
        required=True
    )
    iban = forms.CharField(
        max_length=34,
        required=False
    )
    swift_bic = forms.CharField(
        max_length=11,
        required=False
    )

    class Meta:
        model = BankAccount
        exclude = ('user_profile',)


class EmergencyContactForm(forms.ModelForm):
    class EmergencyContactForm(forms.ModelForm):
        name = forms.CharField(
            max_length=128,
            required=True
        )
        address = forms.CharField(
            max_length=128,
            required=True
        )
        descriptive_number = forms.CharField(
            max_length=10,
            required=True
        )
        postal_code = forms.CharField(
            max_length=10,
            required=True
        )
        city = forms.CharField(
            max_length=128,
            required=True
        )
        phone_number = forms.CharField(
            max_length=15,
            required=True
        )

        class Meta:
            model = EmergencyContact
            exclude = ('user_profile',)

    class Meta:
        model = EmergencyContact
        exclude = ('user_profile',)

class BaseEmergencyContactFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        total_forms = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                # Check if any field is filled
                filled = any(value for key, value in form.cleaned_data.items() if key != 'DELETE' and value)
                if filled:
                    total_forms += 1
        if total_forms > 2:
            raise forms.ValidationError("You can only have up to two emergency contacts.")

EmergencyContactFormSet = inlineformset_factory(
    UserProfile,
    EmergencyContact,
    form=EmergencyContactForm,
    formset=BaseEmergencyContactFormSet,
    extra=2,
    max_num=2,
    can_delete=True,
)


class EmployeeInformationForm(forms.ModelForm):
    permament_postal_code = forms.CharField(
        max_length=5,
        validators=[RegexValidator(r'^\d+$', 'Pole musí obsahovat pouze číslice')],
        required=True
    )
    phone_number = forms.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\d+$', 'Pole musí obsahovat pouze číslice')],
        required=True
    )
    permament_address = forms.CharField(
        max_length=128,
        required=True
    )
    permament_descriptive_number = forms.CharField(
        max_length=10,
        required=True
    )
    city = forms.CharField(
        max_length=128,
        required=True
    )


    class Meta:
        model = EmployeeInformation
        # exclude = ('user_profile',)
        fields = [
            'permament_address',
            'permament_descriptive_number',
            'permament_postal_code',
            'city',
            'phone_number',
        ]


class SecurityQuestionForm(forms.ModelForm):
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

    class Meta:
        model = UserProfile
        fields = ['security_question', 'security_answer']

    def save(self, commit=True):
        user_profile = super().save(commit=False)
        user_profile.set_security_answer(self.cleaned_data['security_answer'])
        if commit:
            user_profile.save()
        return user_profile


class SecurityAnswerForm(forms.Form):
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

    # Validation password conditions on beckend
    def clean_new_password(self):
        password = self.cleaned_data.get('new_password')


        if len(password) < 8:
            raise ValidationError('Heslo musí mít alespoň 8 znaků.')
        if not any(char.isupper() for char in password):
            raise ValidationError('Heslo musí obsahovat alespoň jedno velké písmeno.')
        if not any(char.islower() for char in password):
            raise ValidationError('Heslo musí obsahovat alespoň jedno malé písmeno.')
        if not any(char.isdigit() for char in password):
            raise ValidationError('Heslo musí obsahovat alespoň jednu číslici.')

        return password


    # validation password match on beckend
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        new_password_confirm = cleaned_data.get('new_password_confirm')

        if new_password and new_password_confirm and new_password != new_password_confirm:
            self.add_error('new_password_confirm', 'Hesla se neshodují')

        return cleaned_data
