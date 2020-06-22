import json
from rest_framework import viewsets
from django.shortcuts import render
from django.http import JsonResponse
from .models import Customers
from .serializers import CustomersSerializer


class indexViewSet(viewsets.ModelViewSet):
	queryset = Customers.objects.all().order_by('name')
	serializer_class = CustomersSerializer

def single(request, id):
	customer = Customers.objects.get(id = id)
	return JsonResponse(customer, safe = False)

