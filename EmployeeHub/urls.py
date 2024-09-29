"""EmployeeHub URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import path


from viewer.models import Customer, Contract, Groups, SubContract
from viewer.views import homepage, UserListView, ProjectListView, PositionListView, CustomerListView, ContractListView, ContractAllListView, SignUpView, contract_detail



#admin.site.register(User)
admin.site.register(Customer)
admin.site.register(Contract)
admin.site.register(Groups)
admin.site.register(SubContract)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name='homepage'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('products/', ProjectListView.as_view(), name='product_list'),
    path('positions/', PositionListView.as_view(), name='position_list'),
    path('customers/', CustomerListView.as_view(), name='customer_list'),

    path('navbar_contracts/', ContractListView.as_view(), name='navbar_contracts'),
    path('navbar_contracts_all/', ContractAllListView.as_view(), name='navbar_contracts_all'),
    path('sign-up/', SignUpView.as_view(), name='signup'),
    path('registration/login/', LoginView.as_view(), name='login'),
    path('contract/<int:contract_id>/', contract_detail, name='detail_contract'),
]
