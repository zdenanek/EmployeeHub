from django.contrib.auth.forms import UserCreationForm
from django.db.models import CharField
from django.forms import ModelForm, Form, CharField, inlineformset_factory, BaseInlineFormSet
from django import forms
from django.core.validators import RegexValidator
from .models import UserProfile, BankAccount, EmployeeInformation, EmergencyContact

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
        validators=[RegexValidator(r'^\d+$', 'Pole musí obsahovat pouze číslice')]
    )
    account_prefix = forms.CharField(
        max_length=6,
        validators=[RegexValidator(r'^\d+$', 'Pole musí obsahovat pouze číslice')]
    )
    bank_code = forms.CharField(
        max_length = 4,
        validators = [RegexValidator(r'^\d+$', 'Pole musí obsahovat pouze číslice')]

)

    class Meta:
        model = BankAccount
        exclude = ('user_profile',)


class EmergencyContactForm(forms.ModelForm):
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
        validators=[RegexValidator(r'^\d+$', 'Pole musí obsahovat pouze číslice')]
    )
    phone_number = forms.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\d+$', 'Pole musí obsahovat pouze číslice')]
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