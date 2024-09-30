from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from viewer.models import Contract


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