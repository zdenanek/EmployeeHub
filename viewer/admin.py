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


# Registering models for Django administration
# These models will be available in the administration interface,
# making it easier to manage data in the application.
admin.site.register(Position)               # Model for positions
admin.site.register(Customer)               # Model for customers
admin.site.register(Contract)               # Model for contracts
admin.site.register(SubContract)            # Model for subcontracts
admin.site.register(Comment)                # Model for comments
admin.site.register(Event)                  # Model for events
admin.site.register(SecurityQuestion)       # Model for security questions
admin.site.register(Permission)             # Model for permissions
