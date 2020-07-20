from django.db import models

# Create your models here.
class Promotions(models.Model):
    imageUrl = models.CharField(null=True, max_length=1000)
    text = models.CharField(null=True, max_length=1000)
    link = models.CharField(null=True, max_length=1000)
