from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, FormView

from .models import Contract, Customer, Position, SubContract
from .forms import SignUpForm, ContractForm, CustomerForm, SubContractForm, SubContractFormUpdate, CommentForm

from django.contrib.auth import get_user_model
User = get_user_model()

# Funkce, která slouží k zobrazení konkrétního detailu kontraktu
def contract_detail(request, contract_id):# Tato funkce přijímá 2 argumenty (request: HTTP požadavek a ontract_id: Parametr, který představuje ID konkrétního kontraktu, který chceme načíst.
    contract = get_object_or_404(Contract, id=contract_id) # get_object_or_404: Tato funkce se pokusí načíst kontrakt z databáze podle zadaného contract_id
    return render(request, 'detail_contract.html', {'contract': contract}) # Funkce render kombinuje šablonu s kontextovými daty (contract). Šablona 'detail_contract.html' se použije k zobrazení detailů kontraktu. Objekt contract se předává do šablony pomocí kontextového slovníku {'contract': contract}, aby šablona mohla přistupovat k detailům kontraktu a zobrazit je.

# Funkce pro získání všech subcontraktů
def show_subcontracts(request):
    subcontracts = SubContract.objects.all()
    return render(request, 'subcontract.html', {'subcontracts': subcontracts})


def subcontract_detail(request, subcontract_id):
    subcontracts = get_object_or_404(SubContract, id=subcontract_id)
    return render(request, 'detail_subcontract.html', {'subcontracts': subcontracts})


class HomepageView(TemplateView):
    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customers'] = Customer.objects.all()
        context['users'] = User.objects.all()
        context['contracts'] = Contract.objects.all()
        context['positions'] = Position.objects.all()
        return context


class ContractListView(ListView):
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


class CustomerView(ListView):
    model = Customer
    template_name = 'customers.html'


class CustomerCreateView(CreateView):
    template_name = 'form.html'
    form_class = CustomerForm
    success_url = reverse_lazy('navbar_customers')


class CustomerUpdateView(UpdateView):
    template_name = 'form.html'
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy('navbar_customers')


class CustomerDeleteView(DeleteView):
    template_name = 'form.html'
    model = Customer
    success_url = reverse_lazy('navbar_customers')


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


class SubContractView(ListView):
    model = SubContract
    template_name = 'subcontract.html'


class SubContractCreateView(FormView):
    template_name = 'form.html'
    form_class = SubContractForm
    success_url = reverse_lazy('navbar_contracts_all')

    def form_valid(self, form):
        new_sub_contract = form.save(commit=False)
        new_sub_contract.contract = Contract.objects.get(pk=int(self.kwargs["param"]))
        #TODO - ze SubContractForm "smažte" contract field. (místo __all__ dáte jen ['subcontract_name'])
        #TODO subcontract_number bych smazal z modelu a nahradil ho pomocí .pk, které již má každý model
        #alternativně zde můžete použít toto:
        #new_sub_contract.subcontract_number = 7
        new_sub_contract.subcontract_number = SubContract.objects.filter(contract=new_sub_contract.contract).count() + 1

        new_sub_contract.save()
        #pomocí self.request.user zkontroluji, že jsou práva OK
        return super().form_valid(form)


class SubContractUpdateView(UpdateView):
    template_name = "form.html"
    model = SubContract
    form_class = SubContractForm
    success_url = reverse_lazy("navbar_contracts")


class SubContractDeleteView(DeleteView):
    template_name = "form.html"
    model = SubContract
    success_url = reverse_lazy('navbar_contracts')


class CommentCreateView(CreateView):
    template_name = "form.html"
    form_class = CommentForm
    success_url = reverse_lazy('detail_contract')

    def form_valid(self, form):
        new_comment = form.save(commit=False)
        new_comment.subcontract = SubContract.objects.get(pk=int(self.kwargs["pk"]))
        new_comment.save()
        return super().form_valid(form)

    pass


from django.http import JsonResponse
from .models import Event # Předpokládejme, že máš model pro události
import json
from datetime import datetime
from django.contrib.auth.models import Group


def calendar_view(request):
    return render(request, 'calendar.html')


@csrf_exempt
def create_event(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        group_name = data.get('group')

        group = Group.objects.filter(name=group_name).first()
        if group:
            event = Event.objects.create(
                title=title,
                start_time=datetime.strptime(start_time, '%Y-%m-%dT%H:%M'),
                end_time=datetime.strptime(end_time, '%Y-%m-%dT%H:%M'),
                group=group
            )
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Group not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def events_feed(request):
    events = Event.objects.all()
    events_data = [
        {
            'title': getattr(event, 'title', 'Untitled Event'),
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat(),
            'group': getattr(event.group, 'name', 'No Group')
        } for event in events
    ]
    return JsonResponse(events_data, safe=False)

def get_groups(request):
    groups = Group.objects.all()
    groups_data = [{'name': group.name} for group in groups]
    return JsonResponse(groups_data, safe=False)

def delete_event(request, event_id):
    if request.method == 'DELETE':
        try:
            event = Event.objects.get(pk=event_id)
            event.delete()
            return JsonResponse({'status': 'success'})
        except Event.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})



@csrf_exempt
def update_event(request, event_id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        try:
            event = Event.objects.get(pk=event_id)
            event.title = data.get('title', event.title)
            event.start_time = datetime.strptime(data['start_time'], '%Y-%m-%dT%H:%M')
            event.end_time = datetime.strptime(data['end_time'], '%Y-%m-%dT%H:%M')
            event.save()
            return JsonResponse({'status': 'success'})
        except Event.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
