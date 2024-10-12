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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path


from viewer.models import Customer, Contract, Groups, SubContract, Comment, Event
from viewer.views import HomepageView, UserListView, CustomerListView, ContractListView, \
    ContractAllListView, SignUpView, contract_detail, ContractCreateView, ContractUpdateView, ContractDeleteView, \
    CustomerCreateView, CustomerUpdateView, CustomerDeleteView, SubContractCreateView, \
    SubmittablePasswordChangeView, show_subcontracts, SubContractUpdateView, SubContractDeleteView, CommentCreateView, \
    subcontract_detail, events_feed, calendar_view, update_event, create_event, ContractView, SubContractDetailView, \
    SubmittablePasswordChangeView, show_subcontracts, SubContractUpdateView, SubContractDeleteView, CommentCreateView, \
    subcontract_detail, events_feed, calendar_view, update_event, create_event, get_groups, delete_event, \
    employee_profile


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomepageView.as_view(), name='homepage'),
    path('users/', UserListView.as_view(), name='user_list'),


# path for navbar/homepage
    path('navbar_contracts/', ContractListView.as_view(), name='navbar_contracts'),
    path('navbar_contracts_all/', ContractAllListView.as_view(), name='navbar_contracts_all'),

# path for authentication
    path('sign-up/', SignUpView.as_view(), name='signup'),
    path('registration/login/', LoginView.as_view(), name='login'),
    path('accounts/login/', LoginView.as_view(), name='login2'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-change/', SubmittablePasswordChangeView.as_view(),name='password_change'),

# path for contract
    path('contract/<int:pk>/', ContractView.as_view(), name='contract_detail'),
    path('contract/create/', ContractCreateView.as_view(), name='contract_create'),
    path('contract/update/<pk>', ContractUpdateView.as_view(), name='contract_update'),
    path('contract/delete/<pk>', ContractDeleteView.as_view(), name='contract_delete'),

# path fot customers
    path('customers/', CustomerListView.as_view(), name='navbar_customers'),
    path('customer/create/', CustomerCreateView.as_view(), name='customer_create'),
    path('customer/update/<pk>', CustomerUpdateView.as_view(), name='customer_update'),
    path('customer/delete/<pk>', CustomerDeleteView.as_view(), name='customer_delete'),

# path for subcontracts
    path('subcontracts/', show_subcontracts, name='navbar_show_subcontracts'),
    path('subcontract/<int:contract_pk>/<int:subcontract_number>/', SubContractDetailView.as_view(),
         name='subcontract_detail'),
    path('subcontract/<subcontract_id>/', subcontract_detail, name='detail_subcontract'),
    path('subcontract/<int:subcontract_id>/', subcontract_detail, name='detail_subcontract'),
    path('subcontract/create/<param>', SubContractCreateView.as_view(), name='subcontract_create'),
    # path("subcontract/<int:pk>/update/", SubContractUpdateView.as_view(), name="subcontract_update"),
    path("subcontract/<int:contract_pk>/<int:subcontract_number>/update/", SubContractUpdateView.as_view(), name="subcontract_update"),
    path('subcontract/delete/<pk>', SubContractDeleteView.as_view(), name='subcontract_delete'),

# paths for comments
    path('comment/create/<pk>', CommentCreateView.as_view(), name='comment_add'),

#path for calendar
    path('calendar/', calendar_view, name='calendar'),
    path('events-feed/', events_feed, name='events_feed'),
    path('create-event/', create_event, name='create_event'),
    path('get-groups/', get_groups, name='get_groups'),
    path('update-event/<int:event_id>/', update_event, name='update_event'),
    path('delete-event/<int:event_id>/', delete_event, name='delete_event'),

    path('employees/', UserListView.as_view(), name='employees'),

    path('employee-profile/', employee_profile, name='employee_profile'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)