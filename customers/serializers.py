from .models import Customers
from rest_framework import serializers


class CustomersSerializer(serializers.ModelSerializer):
	class Meta:
		model = Customers
		fields = ('id', 'issue_no', 'name', 'email', 'paltform')