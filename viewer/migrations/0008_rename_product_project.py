# Generated by Django 4.1.1 on 2024-09-24 16:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0007_customer_product_alter_user_first_name_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Product',
            new_name='Project',
        ),
    ]