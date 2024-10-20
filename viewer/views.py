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
    View pro homepage, uživatel musí být přihlášen.
    Zobrazuje projekty, podprojekty, události a komentáře ve vztahu k právě přihlášenému uživateli.
    Zobrazuje se jen 5 nejaktuálnějších položek a pouze události aktuálního dne.
    """
    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        """
        Načte kontextová data, která se zobrazí na domovské stránce.
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
    Zobrazení podrobností konkrétní zakázky.
    Přístup je omezen na přihlášené uživatele s oprávněním 'view_contract'.
    """
    model = Contract
    template_name = "detail_contract.html"
    permission_required = 'viewer.view_contract'


class ContractCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    """
    Zobrazení pro vytvoření nové zakázky.
    K tomuto zobrazení mají přístup pouze uživatelé s oprávněním `add_contract`.
    """
    template_name = 'form.html'
    form_class = ContractForm
    success_url = reverse_lazy('navbar_contracts_all')
    permission_required = 'viewer.add_contract'

    def get_form_kwargs(self):
        """
        Zajišťuje vytvoření výchozího zákazníka, pokud ještě žádný neexistuje.
        """
        kwargs = super().get_form_kwargs()
        if Customer.objects.count() == 0:
            Customer.objects.create(first_name="John", last_name="Doe")
        return kwargs


class ContractUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    """
    Zobrazení pro aktualizaci existující smlouvy.
    K tomuto zobrazení mají přístup pouze uživatelé s oprávněním `change_contract`.
    """
    template_name = "form.html"
    model = Contract
    form_class = ContractForm
    success_url = reverse_lazy("navbar_contracts_all")
    permission_required = 'viewer.change_contract'


class ContractDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    """
    Zobrazení pro vymazání zakázky.
    Přístup mají pouze uživatelé s oprávněním 'delete_contract'.
    """
    template_name = "delete_confirmation.html"
    model = Contract
    permission_required = 'viewer.delete_contract'

    def post(self, request, *args, **kwargs):
        """
        Úprava, která předchází smazání zakázky, která má podzakázky.
        Args: request: objekt HTTP request
        Vrací: Přesměruje zpět na stránku všech zakázek, nebo zobraz varovnou zprávu.
        """
        self.object = self.get_object()
        if self.object.subcontracts.exists():
            messages.warning(request, "You can't delete this contract because it has active subcontracts.")
            return redirect('navbar_contracts_all')
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        """
        Určuje adresu přesměrování po úspěšném vymazání, jinak se vrátí zpět dle výchozího nastavení.
        """
        referer = self.request.POST.get('referer', None)
        if referer:
            return referer
        return reverse_lazy('navbar_contracts_all')

    def get_context_data(self, **kwargs):
        """
        Předá šabloně další kontext a do něj předá aktuální požadavek (request).
        """
        context = super().get_context_data(**kwargs)
        context['request'] = self.request
        return context


class ContractListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    """
    Zobrazení seznamu zakázek přidružených k aktuálně ověřenému uživateli.
    Přístup mají pouze uživatelé s oprávněním 'view_contract'.
    Obsahuje funkci vyhledávání, která umožňuje filtrovat smlouvy podle názvu.
    """
    model = Contract
    template_name = 'navbar_contracts.html'
    context_object_name = "contracts"
    permission_required = 'viewer.view_contract'

    def get_queryset(self):
        """
        Vrací filtrovanou sadu dotazů na zakázky pro ověřeného uživatele.
        Pokud je uživatel ověřen, vyfiltruje smlouvy spojené s aktuálním uživatelem.
        Uživatel může také vyhledávat smlouvy podle názvu pomocí parametru GET 'query'.
        Smlouvy jsou seřazeny pomocí metody `delta()`.
        Vrací:
            QuerySet: Vyfiltrovaný a setříděný seznam smluv pro aktuálního uživatele.
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
        Předá do šablony další kontext.
        Do kontextu přidá vyhledávací formulář a vyhledávací adresu URL, které se používají pro filtrování zakázek.
        Obsahuje také příznak 'show_search', který označuje, že se má zobrazit funkce vyhledávání.
        Args:
            **kwargs: Další kontextové údaje.
        Vrací:
            dict: Kontextová data, která se předají šabloně.
        """
        context = super().get_context_data(**kwargs)
        context["search_form"] = SearchForm()
        context["search_url"] = "navbar_contracts"
        context["show_search"] = True
        return context


class ContractAllListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    """
    Zobrazení seznamu všech smluv bez ohledu na uživatele.
    K tomuto zobrazení mají přístup pouze uživatelé s oprávněním 'view_contract'.
    Obsahuje funkci vyhledávání, která umožňuje filtrovat smlouvy podle názvu.
    """
    model = Contract
    template_name = 'navbar_contracts_all.html'
    context_object_name = "contracts"
    permission_required = 'viewer.view_contract'

    def get_queryset(self):
        """
        Vrátí množinu všech zakázek, volitelně filtrovanou podle vyhledávacího dotazu.
        Pokud je zadán parametr GET 'query', filtruje zakázky podle názvu.
        Zakázky jsou seřazeny pomocí metody `delta()`.
        Vrací:
            QuerySet: filtrovaný a setříděný seznam všech zakázek.
        """
        queryset = Contract.objects.all()
        query = self.request.GET.get("query")
        if query:
            queryset = queryset.filter(contract_name__icontains=query)
        return sorted(queryset, key=lambda contract: contract.delta())

    def get_context_data(self, **kwargs):
        """
        Předá do šablony další kontext pro vyhledávání.
        """
        context = super().get_context_data(**kwargs)
        context["search_form"] = SearchForm(self.request.GET or None)
        context["search_url"] = "navbar_contracts_all"
        context["show_search"] = True
        return context


@login_required
def contract_detail(request, contract_id):
    """
    Zobrazí detailní zobrazení konkrétní zakázky.
    """
    contract = get_object_or_404(Contract, id=contract_id)
    return render(request, 'detail_contract.html', {'contract': contract})


class SubContractAllListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    """
    Toto zobrazení načte a zobrazí seznam všech subdodávek.
    Podporuje filtrování podle názvu subdodávky, nebo mateřské zakázky.
    Výsledky jsou seřazeny podle vlastní metody (delta).
    Uživatelé musí být ověřeni a mít potřebné oprávnění 'view_subcontract'.
    Metody:
        get_queryset():
            Získá podzakázky a použije filtrování na základě vyhledávacího dotazu.
            Výsledek je seřazen pomocí metody delta subkontraktů.
        get_context_data(**kwargs):
            Přidá do šablony další kontext, včetně vyhledávacího formuláře.
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
    Zobrazí seznam podzakázek. Uživatel musí být ověřen a mít oprávnění 'view_subcontract'
    """
    model = SubContract
    template_name = 'subcontracts_homepage.html'
    permission_required = 'viewer.view_subcontract'


class SubContractCreateView(PermissionRequiredMixin, LoginRequiredMixin, FormView):
    """
    Vytvoří nové podzakázky v rámci konkrétní zakázky.
    Uživatel musí být ověřen a mít oprávnění 'add_subcontract'.
    Využívá šablonu 'form.html'.
    Metody:
        form_valid(form):
            Obsluhuje uložení platného formuláře podzakázky, přiřadí novou podzakázku ke správné zakázce,
            přiřadí příslušné číslo podzakázky na základě dalších existujících podzakázek.
        get_success_url():
            Určuje adresu URL, na kterou se má přesměrovat po úspěšném vytvoření podzakázky a vrací adresu
            stránku s podrobnostmi pro přidruženou zakázku.
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
    Aktualizace podzakzky. Uživatel musí být přihlášen a mít oprávnění měnit údaje podzakázky.
    """
    template_name = "form.html"
    model = SubContract
    form_class = SubContractForm
    permission_required = 'viewer.change_subcontract'

    def get_object(self):
        """
        Vyhledá objekt podzakázky na základě primárního klíče zakázky a čísla subdodávky uvedeného v adrese URL.
        """
        contract_pk = self.kwargs.get("contract_pk")
        subcontract_number = self.kwargs.get("subcontract_number")
        return SubContract.objects.get(contract__pk=contract_pk, subcontract_number=subcontract_number)

    def get_success_url(self):
        """
        Definuje adresu URL, kam přesměrovat po úspěšné aktualizaci. Pracuje s id zakázky a vlastním číslem podzakázky.
        """
        return reverse_lazy('contract_detail', kwargs={'pk': self.kwargs['contract_pk']})


class SubContractDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    """
    Odstranění podzakázky. Uživatel musí být přihlášen a mít oprávnění k mazání údajů o podzakázce.
   """
    template_name = "delete_confirmation.html"
    model = SubContract
    permission_required = 'viewer.delete_subcontract'

    def get_success_url(self):
        """
        Určuje adresu URL pro přesměrování po úspěšném odstranění podzakázky.
        Pokud je v údajích POST uveden referer, přesměruje se na tuto adresu URL;
        v opačném případě se přesměruje na stránku s detailem smlouvy.
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
    Zobrazení podrobností podzakázky. Uživatel bude přihlášen a bude mít oprávnění k zobrazení podrobností podzakázky.
    """
    template_name = "detail_subcontract.html"
    model = SubContract
    permission_required = 'viewer.view_subcontract'

    def get_object(self):
        """
        Vyhledá objekt podzakázky na základě primárního klíče zakázky a čísla podzakázky uvedeného v adrese URL.
        """
        contract_pk = self.kwargs.get("contract_pk")
        subcontract_number = self.kwargs.get("subcontract_number")
        return SubContract.objects.get(contract__pk=contract_pk, subcontract_number=subcontract_number)


@login_required
def show_subcontracts(request):
    """
    Tato funkce se stará o zobrazení podzakázek, které patří přihlášenému uživateli.
    Podporuje filtrování na základě vyhledávacího dotazu zadaného uživatelem.
    Podzakázky jsou seřazeny na základě metody delta() související zakázky.
    Zobrazení používá formulář pro vyhledávání a zobrazuje výsledky v šabloně.
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
    Tato funkce vyhledá na základě zadaného subcontract_id podzakázku a její mateřskou zakázku.
    Pokud podzakázka neexistuje, zobrazí se chyba 404.
    """
    subcontract = get_object_or_404(SubContract, pk=subcontract_id)
    contract = subcontract.contract
    return render(request, 'detail_subcontract.html', {'subcontract': subcontract, 'contract': contract})


class CustomerView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    """
    Zobrazení seznamu zákazníků. Uživatel bude přihlášen a bude mít oprávnění k zobrazení údajů o zákaznících.
    """
    model = Customer
    template_name = 'navbar_customers.html'
    context_object_name = "customers"
    permission_required = 'viewer.view_customer'

    def get_queryset(self):
        """
        Získá filtrovaný seznam zákazníků na základě vyhledávacího dotazu.
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
        Přidává do šablony vyhledávací formulář a související kontext.
        """
        context = super().get_context_data(**kwargs)
        context["search_form"] = SearchForm()
        context["search_url"] = "navbar_customers"
        context["show_search"] = True
        return context


class CustomerCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    """
    Vytvoření nového zákazníka. Uživatel bude přihlášen a bude mít oprávnění přidávat zákazníky.
    """
    template_name = 'form.html'
    form_class = CustomerForm
    success_url = reverse_lazy('navbar_customers')
    permission_required = 'viewer.add_customer'


class CustomerUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    """
    Aktualizace stávajícího zákazníka. Uživatel bude přihlášen a bude mít oprávnění měnit údaje o zákazníkovi.
    """
    template_name = 'form.html'
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy('navbar_customers')
    permission_required = 'viewer.change_customer'


class CustomerDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    """
    Odstranění zákazníka. Uživatel bude přihlášen a bude mít oprávnění mazat zákazníky.
    """
    template_name = 'delete_confirmation.html'
    model = Customer
    permission_required = 'viewer.delete_customer'

    def get_success_url(self):
        """
        Určuje adresu URL, na kterou se má přesměrovat po úspěšném odstranění zákazníka.
        Pokud je v údajích POST uveden referer, přesměruje se na tuto adresu URL;
        v opačném případě se přesměruje na stránku se seznamem zákazníků.
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
        Na základě vyhledávacího dotazu získává fltrovaný seznam uživatelů.
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
        Přidá do šablony vyhledávací formulář a další kontext.
        """
        context = super().get_context_data(**kwargs)
        context["search_form"] = SearchForm()
        context["search_url"] = "employees"
        context["show_search"] = True
        return context


class CommentListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    """
    Zobrazení posledních pěti komentářů, řazených sestupně od nejnovějšího, za přihlášením a oprávněním.
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
    Zobrazení pro vytvoření komentáře k podzakázce, které vyžaduje přihlášení a oprávnění.
    """
    template_name = "form.html"
    form_class = CommentForm
    permission_required = 'viewer.add_comment'

    def form_valid(self, form):
        """
        Přiřadí komentář podzakázce před uložením.
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
    Vykresluje kalendář pro přihlášené uživatele.
    """
    return render(request, 'calendar.html')


@login_required
def events_feed(request):
    """
    Vrací odpověď JSON se všemi událostmi naformátovanými pro zobrazení kalendáře.
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
    Vytvoří novou událost na základě POSTnutých dat JSON a vrátí úspěch nebo chybu.
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
    Vrátí odpověď JSON se všemi dostupnými skupinami včetně jejich názvů.
    """
    groups = Group.objects.all()
    groups_data = [{'name': group.name} for group in groups]
    return JsonResponse(groups_data, safe=False)


@login_required
@csrf_exempt
def update_event(request, event_id):
    """
    Aktualizuje podrobnosti existující události na základě dat požadavku PUT a vrátí úspěšnou nebo chybovou odpověď.
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
    Odstraní událost, pokud existuje, na základě jejího event_id a vrátí úspěšnou nebo chybovou odpověď.
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
    Zobrazuje a spravuje stránku profilu zaměstnance a umožňuje uživatelům zobrazovat a upravovat informace
        o zaměstnanci, údaje o bankovním účtu a kontakty pro případ nouze.
    Zpracovává požadavky GET i POST s vylepšeným zpracováním chyb:
        - GET: Získává a zobrazuje informace o profilu uživatele s editačními formuláři pro různé sekce.
        - POST: Zpracovává odeslání formulářů pro informace o zaměstnancích, bankovním účtu nebo nouzových kontaktech.
    Vylepšené zpracování chyb zahrnuje protokolování výjimek a upozornění uživatele na problémy a přesměrování zpět
        na stránku profilu, pokud se vyskytnou chyby.
    """
    user = request.user

    try:
        user_profile, created = UserProfile.objects.get_or_create(user=user)
    except Exception as e:
        logger.error(f"Error fetching/creating UserProfile for user {user.id}: {e}")
        messages.error(request, 'An error occurred while fetching your profile. Please try again later.')
        return redirect('home')

    edit_section = request.GET.get('edit')

    # Inicializovat formuláře jako None
    bank_account_form = None
    employee_information_form = None
    emergency_contact_formset = None

    # Zpracování požadavků POST
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

    # Zpracování požadavků GET
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

    # Získání dat pro zobrazení v režimu pouze pro čtení
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
    Zobrazení pro zpracování registrace uživatelů a vytváření účtů.
    Zobrazí formulář pro přihlášení uživatelů k účtu.
    Přístup mají pouze uživatelé s oprávněním `view_userprofile`.
    Po úspěšném přihlášení jsou uživatelé přesměrováni na domovskou stránku.
    """
    template_name = 'form.html'
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    permission_required = "viewer.view_userprofile"


class SubmittableLoginView(LoginView):
    """
    Vlastní zobrazení přihlášení.
    """
    template_name = 'login.html'


class SubmittablePasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    Zobrazení změny hesla s požadavkem na přihlášení a přesměrováním na domovskou stránku v případě úspěchu.
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
