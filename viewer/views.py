from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic import ListView
from .models import Project, User, Function, Customer

def homepage(request):
    # Načtení dat pro jednotlivé bloky
    users = User.objects.all()
    products = Project.objects.all()
    functions = Function.objects.all()
    customers = Customer.objects.all()
    context = {
        'users': users,
        'products': products,
        'functions': functions,
        'customers': customers
    }
    return render(request, 'homepage.html', context)




class ProjectListView(ListView):
    model = Project
    template_name = 'projects.html'


class UserListView(ListView):
    model = User
    template_name = 'users.html'


class FunctionListView(ListView):
    model = Function
    template_name = 'functions.html'


class CustomerListView(ListView):
    model = Customer
    template_name = 'customers.html'


class MyProjectsListView(ListView):
    model = Project
    template_name = 'navbar_list.html'



