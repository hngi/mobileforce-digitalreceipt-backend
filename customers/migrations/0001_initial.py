# Generated by Django 3.0.7 on 2020-06-23 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerDetails',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=200)),
                ('platform', models.CharField(max_length=50, null=True)),
                ('phoneNumber', models.CharField(max_length=50)),
                ('user', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='customers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issue_no', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('platform', models.TextField(max_length=50)),
            ],
        ),
    ]
