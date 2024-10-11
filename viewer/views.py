from django.contrib.auth.decorators import login_required
from django.db.models import Max, Q
from django.forms import inlineformset_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, FormView, DetailView

from .models import Contract, Customer, Position, SubContract, Event, Comment, UserProfile, BankAccount, \
    EmployeeInformation, EmergencyContact
from .forms import SignUpForm, ContractForm, CustomerForm, SubContractForm, CommentForm, \
    SearchForm, EmployeeInformationForm, BankAccountForm, EmergencyContactFormSet, BaseEmergencyContactFormSet, \
    EmergencyContactForm

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.mixins import LoginRequiredMixin

@login_required
def contract_detail(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    return render(request, 'detail_contract.html', {'contract': contract})

@login_required
def show_subcontracts(request):
    subcontracts = SubContract.objects.filter(user=request.user)
    return render(request, 'subcontract.html', {'subcontracts': subcontracts})

@login_required
def subcontract_detail(request, subcontract_id):
    subcontract = get_object_or_404(SubContract, pk=subcontract_id)
    contract = subcontract.contract
    return render(request, 'detail_subcontract.html', {'subcontract': subcontract, 'contract': contract})


class HomepageView(LoginRequiredMixin, TemplateView):
    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.all()
        context['users'] = User.objects.all()
        context['subcontracts'] = SubContract.objects.filter(user=self.request.user)
        contracts = Contract.objects.filter(user=self.request.user)
        sorted_contracts = sorted(contracts, key=lambda contract: contract.delta())
        context['contracts'] = sorted_contracts
        today = date.today()
        context['events'] = Event.objects.filter(
            Q(start_time__date=today) |
            Q(end_time__date=today) |
            Q(start_time__date__lt=today, end_time__date__gt=today)
        ).order_by('start_time')
        return context


class ContractCreateView(LoginRequiredMixin, CreateView):
    template_name = 'form.html'
    form_class = ContractForm
    success_url = reverse_lazy('navbar_contracts_all')


class ContractUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "form.html"
    model = Contract
    form_class = ContractForm
    success_url = reverse_lazy("navbar_contracts_all")


class ContractDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "form.html"
    model = Contract
    success_url = reverse_lazy('navbar_contracts_all')


class CustomerView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'customers.html'


class CustomerCreateView(LoginRequiredMixin, CreateView):
    template_name = 'form.html'
    form_class = CustomerForm
    success_url = reverse_lazy('navbar_customers')


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'form.html'
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy('navbar_customers')


class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'form.html'
    model = Customer
    success_url = reverse_lazy('navbar_customers')


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'employees.html'
    context_object_name = "employees"

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("query")
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(username__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = SearchForm()
        return context


class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'customers.html'


class ContractListView(LoginRequiredMixin, ListView):
    model = Contract
    template_name = 'navbar_contracts.html'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            contracts = Contract.objects.filter(user=self.request.user)
        else:
            contracts = Contract.objects.none()
        return sorted(contracts, key=lambda contract: contract.delta())


class ContractAllListView(LoginRequiredMixin, ListView):
    model = Contract
    template_name = 'navbar_contracts_all.html'

    def get_queryset(self):
        contracts = Contract.objects.all()
        return sorted(contracts, key=lambda contract: contract.delta())


class SignUpView(LoginRequiredMixin, CreateView):
    template_name = 'form.html'
    form_class = SignUpForm
    success_url = reverse_lazy('homepage')
    
from django.contrib.auth.views import LoginView, PasswordChangeView


class SubmittableLoginView(LoginView):
    template_name = 'login.html'


class SubmittablePasswordChangeView(LoginRequiredMixin, PasswordChangeView):
  template_name = 'form.html'
  success_url = reverse_lazy('homepage')


class SubContractView(LoginRequiredMixin, ListView):
    model = SubContract
    template_name = 'subcontracts_homepage.html'


class SubContractCreateView(LoginRequiredMixin, FormView):
    template_name = 'form.html'
    form_class = SubContractForm

    def form_valid(self, form):
        new_sub_contract = form.save(commit=False)
        new_sub_contract.contract = Contract.objects.get(pk=int(self.kwargs["param"]))
        max_subcontract_number = SubContract.objects.filter(contract=new_sub_contract.contract).aggregate(Max('subcontract_number'))['subcontract_number__max']
        new_sub_contract.subcontract_number = (max_subcontract_number or 0) + 1
        new_sub_contract.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('contract_detail', kwargs={'pk': self.kwargs['param']})


class SubContractUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "form.html"
    model = SubContract
    form_class = SubContractForm

    def get_object(self):
        contract_pk = self.kwargs.get("contract_pk")
        subcontract_number = self.kwargs.get("subcontract_number")
        return SubContract.objects.get(contract__pk=contract_pk, subcontract_number=subcontract_number)

    def get_success_url(self):
        return reverse_lazy('contract_detail', kwargs={'pk': self.kwargs['contract_pk']})


class SubContractDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "form.html"
    model = SubContract

    def get_success_url(self):
        contract_id = self.object.contract.id
        return reverse_lazy('contract_detail', kwargs={'pk': contract_id})


class CommentCreateView(LoginRequiredMixin, CreateView):
    template_name = "form.html"
    form_class = CommentForm

    def form_valid(self, form):
        new_comment = form.save(commit=False)
        new_comment.subcontract = SubContract.objects.get(pk=int(self.kwargs["pk"]))
        new_comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        subcontract = SubContract.objects.get(pk=int(self.kwargs["pk"]))
        contract_id = subcontract.contract.pk
        return reverse_lazy('subcontract_detail', kwargs={'contract_pk': contract_id, "subcontract_number": subcontract.subcontract_number })


class CommentListView(LoginRequiredMixin, ListView):
    model = Comment
    template_name = "comments_homepage.html"



from django.http import JsonResponse
from .models import Event # Předpokládejme, že máš model pro události
import json
from datetime import datetime, date
from django.contrib.auth.models import Group


@login_required
def calendar_view(request):
    return render(request, 'calendar.html')


@login_required
def events_feed(request):
    events = Event.objects.all()
    events_data = [
        {
            'id': event.id,
            'title': event.title,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat(),
            'extendedProps': {
                'group': event.group.name if event.group else 'No Group'
            }
        } for event in events
    ]
    return JsonResponse(events_data, safe=False)


@login_required
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


@login_required
def get_groups(request):
    groups = Group.objects.all()
    groups_data = [{'name': group.name} for group in groups]
    return JsonResponse(groups_data, safe=False)


@login_required
def delete_event(request, event_id):
    if request.method == 'DELETE':
        try:
            event = Event.objects.get(pk=event_id)
            event.delete()
            return JsonResponse({'status': 'success'})
        except Event.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@login_required
@csrf_exempt
def update_event(request, event_id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        try:
            event = Event.objects.get(pk=event_id)
            event.title = data.get('title', event.title)
            event.start_time = datetime.strptime(data['start_time'], '%Y-%m-%dT%H:%M')
            event.end_time = datetime.strptime(data['end_time'], '%Y-%m-%dT%H:%M')
            group_name = data.get('group')
            if group_name:
                group = Group.objects.filter(name=group_name).first()
                if group:
                    event.group = group
            event.save()
            return JsonResponse({'status': 'success'})
        except Event.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


class ContractView(LoginRequiredMixin, DetailView):
    model = Contract
    template_name = "detail_contract.html"


class SubContractDetailView(LoginRequiredMixin, DetailView):
    template_name = "detail_subcontract.html"
    model = SubContract

    def get_object(self):
        contract_pk = self.kwargs.get("contract_pk")
        subcontract_number = self.kwargs.get("subcontract_number")
        return SubContract.objects.get(contract__pk=contract_pk, subcontract_number=subcontract_number)


@login_required
def employee_profile(request):
    user = request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    edit_section = request.GET.get('edit')

    # Initialize variables
    bank_account_form = None
    employee_information_form = None
    emergency_contact_formset = None

    # Handle POST requests
    if request.method == 'POST':
        if 'employee_information_submit' in request.POST:
            # Process Employee Information form
            try:
                employee_information = user_profile.employeeinformation
            except EmployeeInformation.DoesNotExist:
                employee_information = None

            employee_information_form = EmployeeInformationForm(request.POST, instance=employee_information)
            if employee_information_form.is_valid():
                employee_information = employee_information_form.save(commit=False)
                employee_information.user_profile = user_profile
                employee_information.save()
                return redirect('employee_profile')
        elif 'bank_account_submit' in request.POST:
            # Process Bank Account form
            try:
                bank_account = user_profile.bankaccount
            except BankAccount.DoesNotExist:
                bank_account = None

            bank_account_form = BankAccountForm(request.POST, instance=bank_account)
            if bank_account_form.is_valid():
                bank_account = bank_account_form.save(commit=False)
                bank_account.user_profile = user_profile
                bank_account.save()
                return redirect('employee_profile')
        elif 'emergency_contact_submit' in request.POST:
            # Process Emergency Contact formset
            EmergencyContactFormSetAdjusted = inlineformset_factory(
                UserProfile,
                EmergencyContact,
                form=EmergencyContactForm,
                formset=BaseEmergencyContactFormSet,
                extra=1,
                max_num=2,
                can_delete=True,
            )
            emergency_contact_formset = EmergencyContactFormSetAdjusted(request.POST, instance=user_profile)
            if emergency_contact_formset.is_valid():
                emergency_contact_formset.save()
                return redirect('employee_profile')

    else:
        # Handle GET requests
        if edit_section == 'information':
            # Initialize Employee Information form
            try:
                employee_information = user_profile.employeeinformation
            except EmployeeInformation.DoesNotExist:
                employee_information = None
            employee_information_form = EmployeeInformationForm(instance=employee_information)
        elif edit_section == 'account':
            # Initialize Bank Account form
            try:
                bank_account = user_profile.bankaccount
            except BankAccount.DoesNotExist:
                bank_account = None
            bank_account_form = BankAccountForm(instance=bank_account)
        elif edit_section == 'emergency_contacts':
            # Initialize Emergency Contact formset
            EmergencyContactFormSetAdjusted = inlineformset_factory(
                UserProfile,
                EmergencyContact,
                form=EmergencyContactForm,
                formset=BaseEmergencyContactFormSet,
                extra=1 if user_profile.emergency_contacts.count() == 0 else 0,
                max_num=2,
                can_delete=True,
            )
            emergency_contact_formset = EmergencyContactFormSetAdjusted(instance=user_profile)
        # Else, do nothing special for GET request

    # Retrieve data to display in read-only mode
    try:
        employee_information = user_profile.employeeinformation
    except EmployeeInformation.DoesNotExist:
        employee_information = None

    try:
        bank_account = user_profile.bankaccount
    except BankAccount.DoesNotExist:
        bank_account = None

    context = {
        'user': user,
        'user_profile': user_profile,
        'employee_information_form': employee_information_form,
        'bank_account_form': bank_account_form,
        'emergency_contact_formset': emergency_contact_formset,
        'employee_information': employee_information,
        'bank_account': bank_account,
    }
    return render(request, 'employee_profile.html', context)

