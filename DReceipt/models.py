from django.db import models


class Customers(models.Model):
	issue_no = models.IntegerField()
	name = models.CharField(max_length = 100)
	email = models.EmailField()
	platform = models.TextField(max_length = 50)


