import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.db.models import Max, Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, FormView, DetailView


from .models import *
from .forms import *
from .models import Contract, Customer, SubContract, Event, Comment, UserProfile, BankAccount, \
    EmployeeInformation, EmergencyContact
from .forms import SecurityQuestionForm, SecurityAnswerForm, SetNewPasswordForm, SignUpForm, ContractForm, \
    CustomerForm, SubContractForm, CommentForm, SearchForm, EmployeeInformationForm, BankAccountForm, \
    BaseEmergencyContactFormSet, EmergencyContactForm
from datetime import datetime, date
import json

logger = logging.getLogger(__name__)

User = get_user_model()


class HomepageView(LoginRequiredMixin, TemplateView):
    """
    View for the homepage, which requires a logged-in user.

    This view fetches and displays contracts, subcontracts, events,
    and comments related to the logged-in user. It limits subcontracts
    to a maximum of 5 and shows only today's events.
    """
    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        """
        Fetches the context data to be displayed on the homepage.
        """
        contracts = Contract.objects.filter(user=self.request.user)
        subcontracts = SubContract.objects.filter(user=self.request.user)
        sorted_contracts = sorted(contracts, key=lambda contract: contract.delta())
        sorted_subcontracts = sorted(subcontracts, key=lambda subcontract: subcontract.delta)
        limited_subcontracts = sorted_subcontracts[:5]
        today = date.today()

        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.all().order_by('-created')[:5]
        context['users'] = User.objects.all()
        context['contracts'] = sorted_contracts
        context['subcontracts'] = limited_subcontracts

        context['events'] = Event.objects.filter(
            Q(start_time__date=today) |
            Q(end_time__date=today) |
            Q(start_time__date__lt=today, end_time__date__gt=today)
        ).order_by('start_time')
        return context


class ContractView(PermissionRequiredMixin, LoginRequiredMixin, DetailView):
    """
    Displays the detail view of a specific contract.
    Access is limited to logged-in users with the ‘view_contract’ permission.
    """
    model = Contract
    template_name = "detail_contract.html"
    permission_required = 'viewer.view_contract'


class ContractCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    """
    View to handle creating a new contract.
    Only users with the `add_contract` permission can access this view.
    """
    template_name = 'form.html'
    form_class = ContractForm
    success_url = reverse_lazy('navbar_contracts_all')
    permission_required = 'viewer.add_contract'

    def get_form_kwargs(self):
        """
        Customizes the form kwargs to ensure a default customer is created if no customers exist.
        """
        kwargs = super().get_form_kwargs()
        if Customer.objects.count() == 0:
            Customer.objects.create(first_name="John", last_name="Doe")
        return kwargs


class ContractUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    """
    View to handle updating an existing contract.
    Only users with the `change_contract` permission can access this view.
    """
    template_name = "form.html"
    model = Contract
    form_class = ContractForm
    success_url = reverse_lazy("navbar_contracts_all")
    permission_required = 'viewer.change_contract'


class ContractDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    """
    View to handle the deletion of a contract.
    Only users with the `delete_contract` permission can access this view.
    """
    template_name = "delete_confirmation.html"
    model = Contract
    permission_required = 'viewer.delete_contract'

    def post(self, request, *args, **kwargs):
        """
        Custom delete logic to prevent deletion if the contract has active subcontracts.
        Args:   request: The HTTP request object.
        Returns:    HttpResponseRedirect: Redirects back to the contracts page or shows a warning message.
        """
        self.object = self.get_object()
        if self.object.subcontracts.exists():
            messages.warning(request, "You can't delete this contract because it has active subcontracts.")
            return redirect('navbar_contracts_all')
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        """
        Determines the success URL after deletion, falling back to a default if no referer is provided.
        """
        referer = self.request.POST.get('referer', None)
        if referer:
            return referer
        return reverse_lazy('navbar_contracts_all')

    def get_context_data(self, **kwargs):
        """
        Passes another context to the template and passes the current request to it.
        """
        context = super().get_context_data(**kwargs)
        context['request'] = self.request
        return context


class ContractListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    """
    View to list contracts for the logged-in user.
    The user must have the `view_contract` permission. The contracts are filtered by the logged-in user and sorted by a custom delta method.
    """
    model = Contract
    template_name = 'navbar_contracts.html'
    context_object_name = "contracts"
    permission_required = 'viewer.view_contract'

    def get_queryset(self):
        """
        Filters contracts by the logged-in user and applies a search query if provided.
        If the user is authenticated, it filters out the contracts associated with the current user.
        The user can also search for contracts by name using the GET 'query' parameter.
        Contracts are sorted using the `delta()` method.
        Returns:    querySet: A filtered and sorted list of contracts for the current user.
        """
        if self.request.user.is_authenticated:
            queryset = Contract.objects.filter(user=self.request.user)
            query = self.request.GET.get("query")
            if query:
                queryset = queryset.filter(contract_name__icontains=query)
            return sorted(queryset, key=lambda contract: contract.delta())
        return Contract.objects.none()

    def get_context_data(self, **kwargs):
        """
        Adds additional context data to the view, such as the search form.
        Adds a search form and a search URL to the context, which are used to filter orders.
        It also includes a 'show_search' flag to indicate that the search function should be displayed.
        Args:   **kwargs: additional contextual information.
        Returns:    dict: The contextual data to pass to the template.
        """
        context = super().get_context_data(**kwargs)
        context["search_form"] = SearchForm()
        context["search_url"] = "navbar_contracts"
        context["show_search"] = True
        return context


class ContractAllListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    """
    View a list of all contracts regardless of the user.
    Only users with the ‘view_contract’ permission can access this view.
    Includes a search function that allows you to filter contracts by name.
    """
    model = Contract
    template_name = 'navbar_contracts_all.html'
    context_object_name = "contracts"
    permission_required = 'viewer.view_contract'

    def get_queryset(self):
        """
        Returns a set of all jobs, optionally filtered by the search query.
        If the GET parameter 'query' is specified, it filters the jobs by name.
        The jobs are sorted using the `delta()` method.
        Returns:    querySet: a filtered and sorted list of all jobs.
        """
        queryset = Contract.objects.all()
        query = self.request.GET.get("query")
        if query:
            queryset = queryset.filter(contract_name__icontains=query)
        return sorted(queryset, key=lambda contract: contract.delta())

    def get_context_data(self, **kwargs):
        """
        Passes additional search context to the template.
        """
        context = super().get_context_data(**kwargs)
        context["search_form"] = SearchForm(self.request.GET or None)
        context["search_url"] = "navbar_contracts_all"
        context["show_search"] = True
        return context


@login_required
def contract_detail(request, contract_id):
    """
    Displays a detailed view of a specific contract.
    """
    contract = get_object_or_404(Contract, id=contract_id)
    return render(request, 'detail_contract.html', {'contract': contract})


class SubContractAllListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    """
    This view loads and displays a list of all sub-deliveries.
    It supports filtering by subcontract name or parent contract.
    Results are sorted by custom method (delta).
    Users must be authenticated and have the necessary 'view_subcontract' permissions.
    Methods:
        get_queryset(): retrieves subcontracts and applies filtering based on the search query.
            The result is sorted using the delta subcontract method.
        get_context_data(**kwargs): Adds additional context to the template, including the search form.
    """
    model = SubContract
    template_name = 'navbar_subcontracts.html'
    context_object_name = 'subcontracts'
    permission_required = 'viewer.view_subcontract'

    def get_queryset(self):
        queryset = SubContract.objects.all()
        query = self.request.GET.get("query")
        if query:
            queryset = queryset.filter(
                Q(subcontract_name__icontains=query) |
                Q(contract__contract_name__icontains=query)
            )
        sorted_queryset = sorted(queryset, key=lambda subcontract: subcontract.delta)
        return sorted_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = SearchForm(self.request.GET or None)
        context["search_url"] = "navbar_subcontracts"
        context["show_search"] = True
        return context


class SubContractView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    """
    Displays a list of sub-orders. User must be authenticated and have ‘view_subcontract’ permission
    """
    model = SubContract
    template_name = 'subcontracts_homepage.html'
    permission_required = 'viewer.view_subcontract'


class SubContractCreateView(PermissionRequiredMixin, LoginRequiredMixin, FormView):
    """
    Creates new sub-orders within a specific contract.
    The user must be authenticated and have 'add_subcontract' permission.
    Uses the template 'form.html'.
    Methods:
        form_valid(form):
            handles saving a valid subcontract form, assigns the new subcontract to the correct contract,
            assigns the appropriate subcontract number based on other existing subcontracts.
        get_success_url():
            specifies the URL to redirect to after successfully creating a subcontract and returns the address of
            the details page for the associated subcontract.
    """
    template_name = 'form.html'
    form_class = SubContractForm
    permission_required = 'viewer.add_subcontract'

    def form_valid(self, form):
        new_sub_contract = form.save(commit=False)
        new_sub_contract.contract = get_object_or_404(Contract, pk=int(self.kwargs["param"]))
        new_sub_contract.subcontract_number = SubContract.get_next_subcontract_number(new_sub_contract.contract)
        new_sub_contract.save()
        messages.success(self.request, 'Podzakázka byla úspěšně vytvořena.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('contract_detail', kwargs={'pk': self.kwargs['param']})


class SubContractUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    """
    Subcontract update. The user must be logged in and have permission to change subcontract data.
    """
    template_name = "form.html"
    model = SubContract
    form_class = SubContractForm
    permission_required = 'viewer.change_subcontract'

    def get_object(self):
        """
        Finds a subcontract object based on the contract primary key and subcontract number specified in the URL.
        """
        contract_pk = self.kwargs.get("contract_pk")
        subcontract_number = self.kwargs.get("subcontract_number")
        return SubContract.objects.get(contract__pk=contract_pk, subcontract_number=subcontract_number)

    def get_success_url(self):
        """
        Defines the URL to redirect to after a successful update. Works with job id and custom subcontract number.
        """
        return reverse_lazy('contract_detail', kwargs={'pk': self.kwargs['contract_pk']})


class SubContractDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    """
    Removal of the subcontract. The user must be logged in and have permission to delete subcontract data.
    """
    template_name = "delete_confirmation.html"
    model = SubContract
    permission_required = 'viewer.delete_subcontract'

    def get_success_url(self):
        """
        Specifies the URL to redirect to after the successful removal of the subcontract.
        If a referrer is specified in the POST data, it redirects to this URL;
        otherwise, it redirects to the contract detail page.
        """
        referer = self.request.POST.get('referer', None)
        if referer:
            return referer
        contract_id = self.object.contract.id
        return reverse_lazy('contract_detail', kwargs={'pk': contract_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['request'] = self.request
        return context


class SubContractDetailView(PermissionRequiredMixin, LoginRequiredMixin, DetailView):
    """
    View subcontract details. The user will be logged in and will have permission to view the details of the subcontract.
    """
    template_name = "detail_subcontract.html"
    model = SubContract
    permission_required = 'viewer.view_subcontract'

    def get_object(self):
        """
        Finds a subcontract object based on the contract primary key and subcontract number specified in the URL.
        """
        contract_pk = self.kwargs.get("contract_pk")
        subcontract_number = self.kwargs.get("subcontract_number")
        return SubContract.objects.get(contract__pk=contract_pk, subcontract_number=subcontract_number)


@login_required
def show_subcontracts(request):
    """
    This function takes care of displaying the subcontracts that belong to the logged-in user.
    It supports filtering based on the search query entered by the user.
    The subcontracts are sorted based on the delta() method of the related contract.
    The view uses a search form and displays the results in a template.
    """
    query = request.GET.get("query", "")
    subcontracts = SubContract.objects.filter(user=request.user)
    if query:
        subcontracts = subcontracts.filter(
            Q(subcontract_name__icontains=query)
        )
    sorted_subcontracts = sorted(subcontracts, key=lambda subcontract: subcontract.contract.delta())
    search_form = SearchForm(initial={'query': query})
    search_url = 'navbar_show_subcontracts'
    show_search = True

    return render(request, 'subcontract.html', {
        'subcontracts': sorted_subcontracts,
        'search_form': search_form,
        'search_url': search_url,
        'show_search': show_search,
    })


@login_required
def subcontract_detail(request, subcontract_id):
    """
    This function searches for a subcontract and its parent contract based on the specified subcontract_id.
    If the subcontract does not exist, a 404 error is displayed.
    """
    subcontract = get_object_or_404(SubContract, pk=subcontract_id)
    contract = subcontract.contract
    return render(request, 'detail_subcontract.html', {'subcontract': subcontract, 'contract': contract})


class CustomerView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    """
    View the list of customers. The user will be logged in and will have permission to view customer details.
    """
    model = Customer
    template_name = 'navbar_customers.html'
    context_object_name = "customers"
    permission_required = 'viewer.view_customer'

    def get_queryset(self):
        """
        Gets a filtered list of customers based on a search query.
        """
        queryset = super().get_queryset()
        query = self.request.GET.get("query")
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        """
        Adds a search form and related context to the template.
        """
        context = super().get_context_data(**kwargs)
        context["search_form"] = SearchForm()
        context["search_url"] = "navbar_customers"
        context["show_search"] = True
        return context


class CustomerCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    """
    Creating a new customer. The user will be logged in and will have permission to add customers.
    """
    template_name = 'form.html'
    form_class = CustomerForm
    success_url = reverse_lazy('navbar_customers')
    permission_required = 'viewer.add_customer'


class CustomerUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    """
    Updating an existing customer. The user will be logged in and will have permission to change the customer details.
    """
    template_name = 'form.html'
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy('navbar_customers')
    permission_required = 'viewer.change_customer'


class CustomerDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    """
    Customer removal. The user will be logged in and will have permission to delete customers.
    """
    template_name = 'delete_confirmation.html'
    model = Customer
    permission_required = 'viewer.delete_customer'

    def get_success_url(self):
        """
        Specifies the URL to redirect to after a successful customer removal.
        If a referrer is specified in the POST data, it redirects to this URL;
        otherwise, it redirects to the customer list page.
        """
        referer = self.request.POST.get('referer', None)
        if referer:
            return referer
        return reverse_lazy('navbar_customers')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['request'] = self.request
        return context


class UserListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = User
    template_name = 'employees.html'
    context_object_name = "employees"
    permission_required = 'auth.view_user'

    def get_queryset(self):
        """
        Based on the search query, it retrieves a filtered list of users.
        """
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
        """
        Adds a search form and additional context to the template.
        """
        context = super().get_context_data(**kwargs)
        context["search_form"] = SearchForm()
        context["search_url"] = "employees"
        context["show_search"] = True
        return context


class CommentListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    """
    View the last five comments, in descending order from the most recent, after login and permissions.
    """
    model = Comment
    template_name = "comments_homepage.html"
    permission_required = 'viewer.view_comment'
    context_object_name = 'comments'

    def get_queryset(self):
        queryset = Comment.objects.all().order_by('-created')[:5]
        return queryset


class CommentCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    """
    View to create a comment on a subcontract that requires a login and permissions.
    """
    template_name = "form.html"
    form_class = CommentForm
    permission_required = 'viewer.add_comment'

    def form_valid(self, form):
        """
        Assigns a comment to the subcontract before saving.
        """
        new_comment = form.save(commit=False)
        new_comment.subcontract = SubContract.objects.get(pk=int(self.kwargs["pk"]))
        new_comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        subcontract = SubContract.objects.get(pk=int(self.kwargs["pk"]))
        contract_id = subcontract.contract.pk
        return reverse_lazy('subcontract_detail', kwargs={'contract_pk': contract_id, "subcontract_number": subcontract.subcontract_number})


@login_required
def calendar_view(request):
    """
    Renders a calendar for logged in users.
    """
    return render(request, 'calendar.html')


@login_required
def events_feed(request):
    """
    Returns a JSON response with all events formatted for calendar display.
    """
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
    """
    Creates a new event based on the POSTed JSON data and returns success or error.
    """
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
    """
    Returns a JSON response with all available groups including their names.
    """
    groups = Group.objects.all()
    groups_data = [{'name': group.name} for group in groups]
    return JsonResponse(groups_data, safe=False)


@login_required
@csrf_exempt
def update_event(request, event_id):
    """
    Updates the details of an existing event based on the PUT request data and returns a success or error response.
    """
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


@login_required
def delete_event(request, event_id):
    """
    Removes the event, if any, based on its event_id and returns a success or error response.
    """
    if request.method == 'DELETE':
        try:
            event = Event.objects.get(pk=event_id)
            event.delete()
            return JsonResponse({'status': 'success'})
        except Event.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@login_required
def employee_profile(request):
    """
    Displays and manages the employee profile page and allows users to view and edit employee information,
    bank account details and emergency contacts.
    Handles both GET and POST requests with enhanced error handling:
        - GET: Retrieves and displays user profile information with edit forms for various sections
        - POST: Handles form submissions for employee, bank account or emergency contact information.
    Enhanced error handling includes exception logging and notifying the user of problems and redirecting them back to
    the profile page if errors occur.
    """
    user = request.user

    try:
        user_profile, created = UserProfile.objects.get_or_create(user=user)
    except Exception as e:
        logger.error(f"Error fetching/creating UserProfile for user {user.id}: {e}")
        messages.error(request, 'An error occurred while fetching your profile. Please try again later.')
        return redirect('home')

    edit_section = request.GET.get('edit')

    # Initialize forms as None
    bank_account_form = None
    employee_information_form = None
    emergency_contact_formset = None

    # Processing POST requests
    if request.method == 'POST':
        if 'employee_information_submit' in request.POST:
            try:
                employee_information = user_profile.employeeinformation
            except EmployeeInformation.DoesNotExist:
                employee_information = None
            employee_information_form = EmployeeInformationForm(request.POST, instance=employee_information)

            if employee_information_form.is_valid():
                try:
                    employee_information = employee_information_form.save(commit=False)
                    employee_information.user_profile = user_profile
                    employee_information.save()
                    messages.success(request, 'Informace o zaměstnanci úspěšně upraveny.')
                    return redirect('employee_profile')
                except Exception as e:
                    logger.error(f"Error saving EmployeeInformation for user {user.id}: {e}")
                    messages.error(request, 'An error occurred while saving employee information.')
            else:
                messages.error(request, 'Opravte prosím níže uvedené chyby.')

        elif 'bank_account_submit' in request.POST:
            try:
                bank_account = user_profile.bankaccount
            except BankAccount.DoesNotExist:
                bank_account = None
            bank_account_form = BankAccountForm(request.POST, instance=bank_account)

            if bank_account_form.is_valid():
                try:
                    bank_account = bank_account_form.save(commit=False)
                    bank_account.user_profile = user_profile
                    bank_account.save()
                    messages.success(request, 'Bankovní údaje úspěšně upraveny.')
                    return redirect('employee_profile')
                except Exception as e:
                    logger.error(f"Error saving BankAccount for user {user.id}: {e}")
                    messages.error(request, 'An error occurred while saving bank account details.')
            else:
                messages.error(request, 'Opravte prosím níže uvedené chyby.')

        elif 'emergency_contact_submit' in request.POST:
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
                try:
                    emergency_contact_formset.save()
                    messages.success(request, 'Kontaktní osoby úspěšně upraveny.')
                    return redirect('employee_profile')
                except Exception as e:
                    logger.error(f"Error saving EmergencyContact for user {user.id}: {e}")
                    messages.error(request, 'An error occurred while updating emergency contacts.')
            else:
                messages.error(request, 'Opravte prosím níže uvedené chyby.')

    # GET request processing
    else:
        if edit_section == 'information':
            try:
                employee_information = user_profile.employeeinformation
            except EmployeeInformation.DoesNotExist:
                employee_information = None
            employee_information_form = EmployeeInformationForm(instance=employee_information)

        elif edit_section == 'account':
            try:
                bank_account = user_profile.bankaccount
            except BankAccount.DoesNotExist:
                bank_account = None
            bank_account_form = BankAccountForm(instance=bank_account)

        elif edit_section == 'emergency_contacts':
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

    # Getting data to display in read-only mode
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


class SignUpView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    """
    View for processing user registration and account creation.
    Displays the form for logging users into an account.
    Only users with `view_userprofile` permission have access.
    After successful login, users are redirected to the home page.
    """
    template_name = 'form.html'
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    permission_required = "viewer.view_userprofile"


class SubmittableLoginView(LoginView):
    """
    Custom login view.
    """
    template_name = 'login.html'


class SubmittablePasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    Display password change with login request and redirect to home page if successful.
    """
    template_name = 'form.html'
    success_url = reverse_lazy('homepage')


@login_required
def change_security_question_view(request):
    user_profile = request.user.userprofile
    if request.method == 'POST':
        form = SecurityQuestionForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bezpečnostní otázka a odpověď byly úspěšně změněny.')
            return redirect('employee_profile')
    else:
        form = SecurityQuestionForm(instance=user_profile)
    return render(request, 'form.html', {'form': form})


def password_reset_step_1(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            request.session['reset_user_id'] = user.id
            return redirect('password_reset_step_2')
        except User.DoesNotExist:
            return render(request, 'password_reset_step_1.html', {'error': 'Uživatel nebyl nalezen'})
    return render(request, 'password_reset_step_1.html')


def password_reset_step_2(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('password_reset_step_1')
    user = get_object_or_404(User, id=user_id)
    profile = user.userprofile

    if request.method == 'POST':
        form = SecurityAnswerForm(request.POST)
        if form.is_valid():
            security_answer = form.cleaned_data['security_answer']
            if profile.check_security_answer(security_answer):
                return redirect('password_reset_step_3')
            else:
                error = 'Nesprávná odpověď nebo špatná otázka'
                return render(request, 'password_reset_step_2.html', {'form': form, 'error': error, 'security_question': profile.security_question})
    else:
        form = SecurityAnswerForm()
    return render(request, 'password_reset_step_2.html', {'form': form, 'security_question': profile.security_question})


def password_reset_step_3(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('password_reset_step_1')
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            new_password_confirm = form.cleaned_data['new_password_confirm']
            if new_password == new_password_confirm:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Vaše heslo bylo úspěšně změněno.')
                del request.session['reset_user_id']
                return redirect('login')
            else:
                form.add_error(None, 'Hesla se neshodují')
    else:
        form = SetNewPasswordForm()
    return render(request, 'password_reset_step_3.html', {'form': form})
