
import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0013_alter_contract_deadline_employeeinformation_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SecurityQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(max_length=255)),
                ('security_question', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='userprofile',
            name='security_answer',
            field=models.CharField(default=1, blank=True, max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='contract',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2024, 11, 12, 17, 1, 6, 266094)),
        ),
        migrations.AlterField(
            model_name='subcontract',
            name='contract',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subcontracts', to='viewer.contract'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='security_question',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='viewer.securityquestion'),
        ),
    ]
