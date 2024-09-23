from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic import ListView
from .models import Product, User, Function, Customer

def base(request):
    # Načtení dat pro jednotlivé bloky
    users = User.objects.all()
    products = Product.objects.all()
    functions = Function.objects.all()
    context = {
        'users': users,
        'products': products,
        'functions': functions
    }
    return render(request, 'base.html', context)




class ProductListView(ListView):
    model = Product
    template_name = 'products.html'

class UserListView(ListView):
    model = User
    template_name = 'users.html'

class FunctionListView(ListView):
    model = Function
    template_name = 'functions.html'

class CustomerListView(ListView):
    model = Customer
    template_name = 'customers.html'
