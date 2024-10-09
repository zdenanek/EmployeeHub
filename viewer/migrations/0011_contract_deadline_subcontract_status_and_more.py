# Generated by Django 4.1.1 on 2024-10-08 16:42

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('viewer', '0010_alter_event_group_alter_event_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2024, 11, 7, 18, 42, 3, 887230)),
        ),
        migrations.AddField(
            model_name='subcontract',
            name='status',
            field=models.CharField(choices=[('0', 'V procesu'), ('1', 'Dokončeno'), ('2', 'Zrušeno')], default=('0', 'V procesu'), max_length=64),
        ),
        migrations.AddField(
            model_name='subcontract',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='comment',
            name='subcontract',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='viewer.subcontract'),
        ),
    ]
