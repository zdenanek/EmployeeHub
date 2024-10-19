from django.contrib import admin
from django.contrib.auth.models import Permission

from .models import Position, UserProfile, EmployeeInformation, BankAccount, EmergencyContact, Contract, Customer, \
    SubContract, Comment, Event, SecurityQuestion


class EmergencyContactInline(admin.TabularInline):
    model = EmergencyContact
    extra = 1  # Number of empty forms to display


class BankAccountInline(admin.StackedInline):
    model = BankAccount
    can_delete = False
    verbose_name_plural = 'Bank Account'


class EmployeeInformationInline(admin.StackedInline):
    model = EmployeeInformation
    can_delete = False
    verbose_name_plural = 'Employee Information'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'position', 'phone_number']
    inlines = [EmployeeInformationInline, BankAccountInline, EmergencyContactInline]


# Registrace modelů pro administraci Django
# Tyto modely budou dostupné v administračním rozhraní,
# což usnadní správu dat v aplikaci.
admin.site.register(Position)            # Model pro pozice
admin.site.register(Customer)             # Model pro zákazníky
admin.site.register(Contract)             # Model pro smlouvy
admin.site.register(SubContract)          # Model pro podmínky smluv
admin.site.register(Comment)              # Model pro komentáře
admin.site.register(Event)                # Model pro události
admin.site.register(SecurityQuestion)     # Model pro bezpečnostní otázky
admin.site.register(Permission)           # Model pro oprávnění
