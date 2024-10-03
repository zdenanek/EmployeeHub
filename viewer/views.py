from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.template.base import kwarg_re
from django.urls import reverse_lazy
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, FormView, DetailView

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
    subcontract = get_object_or_404(SubContract, id=subcontract_id)
    contract = subcontract.contract
    return render(request, 'detail_subcontract.html', {'subcontract': subcontract, 'contract': contract})


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
    # success_url = reverse_lazy('navbar_contracts_all')

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

    def get_success_url(self):
        return reverse_lazy('contract_detail', kwargs={'pk': self.kwargs['param']})



class SubContractUpdateView(UpdateView):
    template_name = "form.html"
    model = SubContract
    form_class = SubContractForm
    # success_url = reverse_lazy("navbar_contracts")
    def get_success_url(self):
        subcontract = self.get_object()
        contract_id = subcontract.contract.pk
        return reverse_lazy("contract_detail", kwargs={"pk": contract_id})


class SubContractDeleteView(DeleteView):
    template_name = "form.html"
    model = SubContract
    # success_url = reverse_lazy('navbar_contracts')

    def get_success_url(self):
        contract_id = self.object.contract.id
        return reverse_lazy('contract_detail', kwargs={'pk': contract_id})


class CommentCreateView(CreateView):
    template_name = "form.html"
    form_class = CommentForm
    success_url = reverse_lazy('detail_contract')

    def form_valid(self, form):
        new_comment = form.save(commit=False)
        new_comment.subcontract = SubContract.objects.get(pk=int(self.kwargs["pk"]))
        new_comment.save()
        return super().form_valid(form)


from django.http import JsonResponse
from .models import Event  # Předpokládejme, že máš model pro události
import json
def events_feed(request):
    events = Event.objects.all()
    events_list = []
    for event in events:
        events_list.append({
            'title': event.name,
            'start': event.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'end': event.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
        })
    return JsonResponse(events_list, safe=False)


@csrf_exempt
def create_event(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            start = parse_datetime(data.get('start_time'))
            end = parse_datetime(data.get('end_time'))

            Event.objects.create(
                name=title,
                start_time=start,
                end_time=end
            )
            return JsonResponse({'status': 'success'},status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def calendar_view(request):
    return render(request, 'calendar.html')

def update_event(request, event_id):
    if request.method == 'POST':
        try:
            event = Event.objects.get(pk=event_id)
            data = json.loads(request.body)
            event.start_time = data.get('start_time')
            event.end_time = data.get('end_time')
            event.save()
            return JsonResponse({'status': 'success'})
        except Event.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


class ContractView(DetailView):
    model = Contract
    template_name = "detail_contract.html"
