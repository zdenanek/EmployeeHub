from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import Contract, Customer, Position
from .forms import SignUpForm, ContractForm

from django.contrib.auth import get_user_model
User = get_user_model()

# @login_required
def homepage(request):
    # Načtení dat pro jednotlivé bloky
    users = User.objects.all()
    contracts = Contract.objects.all()
    positions = Position.objects.all()
    customers = Customer.objects.all()
    context = {
        'users': users,
        'contracts': contracts,
        'positions': positions,
        'customers': customers
    }
    return render(request, 'homepage.html', context)




class ProjectListView(ListView):
    model = Contract
    template_name = 'contracts_homepage.html'



# from logging import getLogger
# LOGGER = getLogger()
class ContractCreateView(CreateView):
    template_name = 'form.html'
    form_class = ContractForm
    success_url = reverse_lazy('navbar_contracts_all')

    # def form_invalid(self, form):
    #     LOGGER.warning(f'User provided invalid data. {form.errors}')
    #     return super().form_invalid(form)


class ContractUpdateView(UpdateView):
    template_name = "form.html"
    model = Contract
    form_class = ContractForm
    success_url = reverse_lazy("homepage")



class ContractDeleteView(DeleteView):
    template_name = "form.html"
    model = Contract
    success_url = reverse_lazy('navbar_contracts_all')


class UserListView(ListView):
    model = User
    template_name = 'users.html'


class PositionListView(ListView):
    model = Position
    template_name = 'positions.html'


class CustomerListView(ListView):
    model = Customer
    template_name = 'customers.html'


class ContractListView(ListView):
    model = Contract
    template_name = 'navbar_contracts.html'


class ContractAllListView(ListView):
    model = Contract
    template_name = 'navbar_contracts_all.html'



class SignUpView(CreateView):
    template_name = 'form.html'
    form_class = SignUpForm
    success_url = reverse_lazy('homepage')
    
from django.contrib.auth.views import LoginView, PasswordChangeView

class SubmittableLoginView(LoginView):
    template_name = 'login.html'


class SubmittablePasswordChangeView(PasswordChangeView):
  template_name = 'form.html'
  success_url = reverse_lazy('homepage')


def contract_detail(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    return render(request, 'detail_contract.html', {'contract': contract})


def user_list(request):
    users = User.objects.all()
    return render(request, "user_list.html", {"users": users})
