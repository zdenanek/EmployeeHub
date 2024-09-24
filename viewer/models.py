from django.db.models import CharField, Model, ForeignKey, DateTimeField, DO_NOTHING


class Function(Model):
    job_function = CharField(max_length=50)
    created = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pozice: {self.job_function}"


class User(Model):
    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)
    user_function = ForeignKey(Function, on_delete=DO_NOTHING, default=1)


    def __str__(self):
        return f"Zaměsnanec: {self.first_name} {self.last_name}"
    

class Customer(Model):
    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)
    created = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Název zákazníka: {self.first_name} {self.last_name}"


class Project(Model):
    product_name = CharField(max_length=100)
    created = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Zakázka: {self.product_name}"
