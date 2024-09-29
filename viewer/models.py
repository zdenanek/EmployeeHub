from django.db.models import CharField, Model, ForeignKey, DateTimeField, DO_NOTHING, ManyToManyField, IntegerField, \
    EmailField

from django.contrib.auth import get_user_model
User = get_user_model()

class Function(Model):
    job_function = CharField(max_length=50)
    created = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pozice: {self.job_function}"

from django.contrib.auth.models import User


class Groups(Model):
    groups_name = CharField(max_length=64)
    created = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Skupiny: {self.groups_name}"


class Customer(Model):
    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)
    created = DateTimeField(auto_now_add=True)
    phone_number = CharField(max_length=16, default="123456789")
    email_address = EmailField(max_length=128, default="jan@novak.cz")


    def __str__(self):
        return f"Název zákazníka: {self.first_name} {self.last_name}"

#from EmployeeHub import settings
#from django.contrib.auth.models import User


class Contract(Model):
    contract_name = CharField(max_length=100)
    created = DateTimeField(auto_now_add=True)
    user = ForeignKey(User, on_delete=DO_NOTHING, default=1)    #TODO nevyplněno? výchozí user?
    customer = ForeignKey(Customer, on_delete=DO_NOTHING, default=1)    #TODO
    status_choices = [("0","V procesu"), ("1","Dokončeno"), ("2","Zrušeno")]
    status = CharField(max_length=64, choices=status_choices, default=status_choices[0])

    def __str__(self):
        return f"Zakázka: {self.contract_name}"


class SubContract(Model):
    subcontract_name = CharField(max_length=128)
    created = DateTimeField(auto_now_add=True)
    contract = ForeignKey(Contract, on_delete=DO_NOTHING)
    #status = ForeignKey(User, on_delete=DO_NOTHING, default=1)    #TODO


    def __str__(self):
        return f"Podzakázka: {self.subcontract_name} Primary key: {self.contract.pk}-{self.pk}"


from django.db import models
from django.contrib.auth import get_user_model


class Position(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.position.name if self.position else 'No position'}"



