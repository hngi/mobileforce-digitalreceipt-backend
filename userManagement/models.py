from django.db import models

# Create your models here.


from django.db import models
import uuid


# Create your models here

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=False, null=False)
    email_address = models.CharField(unique=True, max_length=50, null=False)
    password = models.CharField(max_length=1000, null=False)
    registration_id = models.CharField(max_length=10000, null=True)
    deviceType = models.CharField(max_length=10000, null=True, default=None)
    active = models.BooleanField(default=False, null=True)
    is_premium_user = models.BooleanField(default=False, null=True)
