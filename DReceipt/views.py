import json
from django.shortcuts import render
from django.http import JsonResponse
from .models import Customers
from .serializers import CustomersSerializer


def index(request):
	customers = Customers.objects.all()
	customers_list = list(customers)
	return JsonResponse(customers_list, safe = False)


def single(request, id):
	single =  Customers.object.get(id = id)
	return JsonResponse(single, safe = False)
	
