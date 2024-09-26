from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView


from .models import Contract, Function, Customer
from .forms import SignUpForm

from django.contrib.auth import get_user_model
User = get_user_model()

# @login_required
def homepage(request):
    # Načtení dat pro jednotlivé bloky
    users = User.objects.all()
    contracts = Contract.objects.all()
    functions = Function.objects.all()
    customers = Customer.objects.all()
    context = {
        'users': users,
        'contracts': contracts,
        'functions': functions,
        'customers': customers
    }
    return render(request, 'homepage.html', context)




class ProjectListView(ListView):
    model = Contract
    template_name = 'contracts_homepage.html'


class UserListView(ListView):
    model = User
    template_name = 'users.html'


class FunctionListView(ListView):
    model = Function
    template_name = 'functions.html'


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
    
from django.contrib.auth.views import LoginView

class SubmittableLoginView(LoginView):
    template_name = 'login.html'