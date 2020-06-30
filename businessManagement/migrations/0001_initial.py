# Generated by Django 3.0.7 on 2020-06-30 13:41

import businessManagement.models
import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customers', '0001_initial'),
        ('userManagement', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Receipts',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('receipt_number', models.CharField(max_length=1000, null=True)),
                ('date', models.DateTimeField(blank=True, default=datetime.datetime.now, null=True)),
                ('font', models.CharField(max_length=1000, null=True)),
                ('color', models.CharField(max_length=1000, null=True)),
                ('preset', models.BooleanField(default=False, null=True)),
                ('paid_stamp', models.BooleanField(default=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('issued', models.BooleanField(default=False, null=True)),
                ('deleted', models.BooleanField(default=False, null=True)),
                ('signature', models.FileField(null=True, upload_to=businessManagement.models.user_directory_path)),
                ('partPayment', models.BooleanField(default=False, null=True)),
                ('partPaymentDateTime', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.CustomerDetails')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userManagement.User')),
            ],
        ),
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('quantity', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('unit_price', models.FloatField(validators=[django.core.validators.MinValueValidator(0)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('receipt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='businessManagement.Receipts')),
            ],
        ),
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivered', models.BooleanField(default=False)),
                ('title', models.CharField(max_length=100, null=True)),
                ('message', models.CharField(max_length=100, null=True)),
                ('date_to_deliver', models.DateField(max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userManagement.User')),
            ],
        ),
        migrations.CreateModel(
            name='BusinessInfo',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=150, unique=True)),
                ('phone_number', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=200)),
                ('slogan', models.CharField(max_length=50)),
                ('logo', models.FileField(null=True, upload_to=businessManagement.models.logo_directory_path)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userManagement.User')),
            ],
        ),
    ]
