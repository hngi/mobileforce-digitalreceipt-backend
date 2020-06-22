from django.db import models


class Customers(models.Model):
	issue_no = models.CharField(max_length = 10)
	name = models.CharField(max_length = 100)
	email = models.EmailField()
	platform = models.TextField(max_length = 50)


