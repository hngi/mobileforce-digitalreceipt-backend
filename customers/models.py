from django.contrib.auth.models import User
from django.db import models


class CustomerDetails(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(max_length=200, null=False)
    phoneNumber = models.CharField(max_length=50, null=False)
    address = models.CharField(max_length=150, null=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    saved = models.BooleanField(null=False, default=False)
    active = models.BooleanField(null=True, default=True)
