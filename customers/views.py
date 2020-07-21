import json
import datetime

from rest_framework import viewsets, status
from django.shortcuts import render
from django.http import JsonResponse
from .models import CustomerDetails
from businessManagement.models import Receipts
from .serializers import CustomersSerializer
from rest_framework.decorators import api_view


@api_view(["POST"])
def create_customer(request):
    if request.method == "POST":
        print(request.user_id)
        request.data._mutable = True
        request.data["user"] = request.user_id
        request.data._mutable = False
        print(request.data)
        serializer = CustomersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "DELETE"])
def get_customer(request, id):
    if request.method == "GET":
        try:
            customer = CustomerDetails.objects.get(id=id)
            customers = CustomersSerializer(customer, many=False).data
            return JsonResponse({"data": customers}, status=status.HTTP_200_OK)
        except Exception as error:
            return JsonResponse(
                {"error": "customer does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )

    if request.method == "DELETE":
        try:
            customer = CustomerDetails.objects.filter(user=request.user_id, id=id)
            customer_receipts = Receipts.objects.filter(
                user=request.user_id, customer=id
            )
            if customer:
                customer.active = False
                customer.save()

                if len(customer_receipts) == 0:
                    customer.delete()
                    return JsonResponse(
                        {"data": "customer deleted successfully"},
                        status=status.HTTP_200_OK,
                    )

                else:
                    return JsonResponse(
                        {"error": "Could not delete, Customer still has receipts"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            return JsonResponse(
                {"error": "Could not delete, no customer found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except CustomerDetails.DoesNotExist:
            return JsonResponse(
                {"error": "Could not delete, no customer found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as error:
            return JsonResponse({"error": error}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def all_customers(request):
    if request.method == "GET":
        try:
            customer = CustomerDetails.objects.filter(user=request.user_id).order_by(
                "name"
            )
            customers = CustomersSerializer(customer, many=True).data
            return JsonResponse({"data": customers}, status=status.HTTP_200_OK)
        except CustomerDetails.DoesNotExist:
            return JsonResponse(
                {"error": "No customers created yet"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as error:
            return JsonResponse({"error": error}, status=status.HTTP_400_BAD_REQUEST)
