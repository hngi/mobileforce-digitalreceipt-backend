import os
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
# middleware -to verify token present in headers and pass user in request object
# create/update bussiness ,receipt details
from rest_framework import status
from rest_framework.decorators import api_view
from customers.models import CustomerDetails
from customers.serializers import CustomersSerializer
from userManagement.models import User
from userManagement.serializers import UserSerializer
from .models import Receipts, Products, BusinessInfo
from .serializers import ReceiptSerializer, ProductSerializer, BusinessInfoSerializer


def add_one_to_receipt_number(user):
    """
    Returns the next default value for the `ones` field, starts with
    1
    """
    largest = (
        Receipts.objects.filter(receipt_number__startswith="R-").count()
    )
    print(largest)
    if not largest:
        return 'R-' + str(1)
    return "R-" + str(largest + 1)


@api_view(["POST"])
def create_receipt(request):
    if request.method == "POST":
        if "customerId" not in request.data:
            return JsonResponse(
                {"error": "Enter customerId"}, status=status.HTTP_400_BAD_REQUEST
            )
        data = {
            "user": request.user_id,
            "customer": request.data["customerId"],
            "receipt_number": 1,
            "signature": request.FILES['signature']
        }
        serializer = ReceiptSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def add_product_info_to_receipt(request):
    # send the receipt id
    if request.method == "POST":
        if "receiptId" not in request.data:
            return JsonResponse(
                {"error": "Enter receiptId"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "name" not in request.data:
            return JsonResponse(
                {"error": "Enter product name"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "quantity" not in request.data:
            return JsonResponse(
                {"error": "Enter quantity"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "unit_price" not in request.data:
            return JsonResponse(
                {"error": "Enter unit_price"}, status=status.HTTP_400_BAD_REQUEST
            )
        # user
        data = {
            "receipt": request.data["receiptId"],
            "name": request.data["name"],
            "quantity": request.data["quantity"],
            "unit_price": request.data["unit_price"],
        }
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_all_receipt(request):
    # send the receipt id
    if request.method == "GET":
        try:
            recipt = Receipts.objects.filter(user=request.user_id, issued=True)
            if recipt:
                user = User.objects.get(id=request.user_id)
                userData = UserSerializer(user, many=False).data
                receipts = ReceiptSerializer(recipt, many=True).data
                for data in receipts:
                    data["user"] = {
                        "id": userData["id"],
                        "name": userData["name"],
                        "email_address": userData["email_address"],
                    }
                    products = Products.objects.filter(receipt=data["id"])
                    products_data = ProductSerializer(products, many=True).data
                    data["products"] = products_data
                    print(data["products"])
                    customer = CustomerDetails.objects.get(pk=data["customer"])
                    data["customer"] = CustomersSerializer(customer, many=False).data
                    data["total"] = sum(
                        c["unit_price"] * c["quantity"] for c in data["products"]
                    )
                return JsonResponse(
                    {"message": "Retreived all receipts", "data": receipts},
                    status=status.HTTP_200_OK,
                )
            else:
                return JsonResponse(
                    {"message": "There are no receipts created"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as error:
            return JsonResponse({"message": error}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_all_draft_receipt(request):
    # send the receipt id
    if request.method == "GET":
        try:
            draftReceipt = Receipts.objects.filter(user=request.user_id, issued=False)
            if draftReceipt:
                user = User.objects.get(id=request.user_id)
                userData = UserSerializer(user, many=False).data
                draftReceipts = ReceiptSerializer(draftReceipt, many=True).data
                for data in draftReceipts:
                    data["user"] = {
                        "id": userData["id"],
                        "name": userData["name"],
                        "email_address": userData["email_address"],
                    }
                    products = Products.objects.filter(receipt=data["id"])
                    products_data = ProductSerializer(products, many=True).data
                    data["products"] = products_data
                    print(data["products"])
                    customer = CustomerDetails.objects.get(pk=data["customer"])
                    data["customer"] = CustomersSerializer(customer, many=False).data
                    data["total"] = sum(
                        c["unit_price"] * c["quantity"] for c in data["products"]
                    )
                return JsonResponse(
                    {
                        "message": "Retreived all drafted receipts",
                        "data": draftReceipts,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return JsonResponse(
                    {"message": "There are no draft receipts created"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as error:
            return JsonResponse({"message": error}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def customize_receipt(request):
    if request.method == "POST":
        try:
            customerData = request.data["customer"]
            customerData['user'] = request.user_id

            customerSerializer = CustomersSerializer(data=customerData)

            receiptData = request.data['receipt']
            receiptData['user'] = request.user_id
            productData = request.data["products"]

            is_customer_valid = customerSerializer.is_valid()

            if is_customer_valid:
                customerSerializer.save()

                if "receipt_number" in receiptData:
                    receiptData['receipt_number'] = "AG-" + receiptData['receipt_number']
                else:
                    receiptData['receipt_number'] = add_one_to_receipt_number(request.user_id)

                receiptData['customer'] = customerSerializer.data['id']

                receiptSerailizer = ReceiptSerializer(data=receiptData)

                if receiptSerailizer.is_valid():
                    receiptSerailizer.save()

                else:
                    errorsDict = {}
                    errorsDict.update(receiptSerailizer.errors)

                    return JsonResponse(errorsDict, status=status.HTTP_400_BAD_REQUEST)

                for product in productData:
                    product['receipt'] = receiptSerailizer.data['id']

                productSerializer = ProductSerializer(data=productData, many=True)

                if productSerializer.is_valid():
                    productSerializer.save()

                else:
                    errorsDict = {}
                    errorsDict.update(productSerializer.errors)

                    return JsonResponse(errorsDict, status=status.HTTP_400_BAD_REQUEST)

                return JsonResponse({
                    'productData': productSerializer.data,
                    'receiptData': receiptSerailizer.data,
                    'customerData': customerSerializer.data
                }, status=status.HTTP_200_OK)

            else:
                errorsDict = {}
                errorsDict.update(customerSerializer.errors)

                return JsonResponse(errorsDict, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            return JsonResponse(error, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def upload_receipt_signature(request):
    if request.method == "PUT":
        try:
            receipt = Receipts.objects.get(id=request.data['receiptId'])
            receipt.signature = request.FILES['signature']
            receipt.save()
            receiptData = ReceiptSerializer(receipt)
            data = {
                'message': 'Signature updated successfully',
                "data": receiptData.data,
                "status": status.HTTP_200_OK
            }
            return JsonResponse(data, status=status.HTTP_200_OK)
        except Receipts.DoesNotExist:
            return JsonResponse({
                'error': "Receipts Does not exist"
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_business(request):
    if request.method == 'POST':
        data = {
            'name': request.data['name'],
            'phone_number': request.data['phone_number'],
            'address': request.data['address'],
            'slogan': request.data['slogan'],
            'logo': request.FILES['logo'],
            'user':request.user_id
        }
        serializer = BusinessInfoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_business(request):
    if request.method == 'GET':
        try:
            bus = BusinessInfo.objects.all().order_by('name')
            business = BusinessInfoSerializer(bus, many=True)
            return JsonResponse({
                'data': business
            }, status=status.HTTP_200_OK)
        except BusinessInfo.DoesNotExist:
            return JsonResponse({
                'error': 'No Business created yet'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return JsonResponse({
                'error': error
            }, status=status.HTTP_400_BAD_REQUEST)
