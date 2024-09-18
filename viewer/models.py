from django.db.models import CharField, Model

class Users(Model):
    first_name = CharField(max_length=128)
    last_name = CharField(max_length=128)
