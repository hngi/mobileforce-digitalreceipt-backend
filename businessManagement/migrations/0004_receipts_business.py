# Generated by Django 3.0.7 on 2020-07-31 14:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('businessManagement', '0003_auto_20200731_1901'),
    ]

    operations = [
        migrations.AddField(
            model_name='receipts',
            name='business',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='businessManagement.BusinessInfo'),
        ),
    ]
