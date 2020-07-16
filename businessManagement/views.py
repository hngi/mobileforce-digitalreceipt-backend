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
from .models import Receipts, Products, BusinessInfo, Notifications, Inventory, Category
from .serializers import (
    ReceiptSerializer,
    ProductSerializer,
    BusinessInfoSerializer,
    NotificationsSerializer,
    InventorySerializer,
    CategorySerializer,
)


def add_one_to_receipt_number(user):
    """
    Returns the next default value for the `ones` field, starts with
    1
    """
    largest = Receipts.objects.filter(
        receipt_number__startswith="R-", user=user
    ).count()
    print(largest)
    if not largest:
        return "R-" + str(1)
    return "R-" + str(largest + 1)


@api_view(["POST"])
def create_receipt(request):
    if request.method == "POST":
        data = {
            "user": request.user_id,
        }
        if "receipt_number" in request.data:
            data["receipt_number"] = "AG-" + request.data["receipt_number"]
        else:
            data["receipt_number"] = add_one_to_receipt_number(request.user_id)
        print(data["receipt_number"])
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
            "discount": request.data.get("discount", 0.00),
            "tax_amount": request.data.get("tax_amount", 0.00),
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
                        c["unit_price"] * (100 - c["discount"]) * c["quantity"]
                        + c["tax_amount"]
                        for c in data["products"]
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
                        c["unit_price"] * (100 - c["discount"]) * c["quantity"]
                        + c["tax_amount"]
                        for c in data["products"]
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


@api_view(["PUT"])
def update_draft_receipt(request):
    if request.method == "PUT":
        try:
            if "receiptId" not in request.data:
                return JsonResponse(
                    {"error": "Enter Receipt Id"}, status=status.HTTP_400_BAD_REQUEST,
                )

            receiptId = request.data["receiptId"]
            draftReceipt = Receipts.objects.get(id=receiptId, issued=False)
            draftReceipt.issued = True
            draftReceipt.save()
            updateReceipt = ReceiptSerializer(draftReceipt)
            return JsonResponse({"data": updateReceipt.data}, status=status.HTTP_200_OK)

        except Receipts.DoesNotExist:
            return JsonResponse(
                {"error": "No Receipt was found with this id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as error:
            return JsonResponse({"error": error}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_receipt_id(request):
    # send the receipt id
    if request.method == "GET":
        try:
            receipt = Receipts.objects.filter(id=request.query_params.get("receiptId"))
            if receipt:
                user = User.objects.get(id=request.user_id)
                userData = UserSerializer(user, many=False).data
                draftReceipts = ReceiptSerializer(receipt, many=True).data
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
                        c["unit_price"] * (100 - c["discount"]) * c["quantity"]
                        + c["tax_amount"]
                        for c in data["products"]
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
            errorsDict = {}
            if "email" not in request.data["customer"]:
                return JsonResponse(
                    {"error": "Enter email id of customer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            productData = request.data["products"]
            for product in productData:
                cat = Category.objects.filter(name=product["category_name"])
                if len(cat) == 0:
                    return JsonResponse(
                        {"error": "There is no category with this name"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                catSerializer = CategorySerializer(cat[0]).data
                inventory = Inventory.objects.filter(
                    category=catSerializer["id"], name=product["name"]
                )
                if len(inventory) == 0:
                    return JsonResponse(
                        {"error": "There are no items in inventory with this product"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                invSerializer = InventorySerializer(inventory[0]).data
                print(invSerializer["quantity"])
                if invSerializer["quantity"] < product["quantity"]:
                    return JsonResponse(
                        {"error": "There are less number of products in inventory"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                product["categoryId"] = catSerializer["id"]
                product["unit_price"] = float(invSerializer["price"])
            customerData = request.data["customer"]
            customerData["user"] = request.user_id
            cust = CustomerDetails.objects.filter(
                email=request.data["customer"]["email"], user=request.user_id
            )
            print(cust)
            if len(cust) == 0:
                customerSerializer = CustomersSerializer(data=customerData)
                is_customer_valid = customerSerializer.is_valid()
                if is_customer_valid:
                    customerSerializer.save()
            cust = CustomerDetails.objects.get(
                email=request.data["customer"]["email"], user=request.user_id
            )
            customerSerializer = CustomersSerializer(cust)
            receiptData = request.data["receipt"]
            receiptData["user"] = request.user_id
            productData = request.data["products"]

            if customerSerializer:

                receiptData["customer"] = customerSerializer.data["id"]

                receipts = Receipts.objects.filter(id=receiptData["id"]).update(
                    **receiptData
                )

                receipts = Receipts.objects.get(id=receiptData["id"])
                receiptSerailizer = ReceiptSerializer(receipts)

                if receiptData["partPayment"]:
                    serailizer = NotificationsSerializer(
                        data={
                            "user": request.user_id,
                            "delivered": False,
                            "title": " Remainder ",
                            "message": "Payment Remainder Receipt-"
                            + receiptSerailizer.data["receipt_number"],
                            "date_to_deliver": receiptData["partPaymentDateTime"],
                        }
                    )
                    if serailizer.is_valid():
                        serailizer.save()

                for product in productData:
                    inventory = Inventory.objects.get(
                        category=product["categoryId"], name=product["name"]
                    )
                    invSerializer = InventorySerializer(inventory).data
                    inventory.quantity = invSerializer["quantity"] - product["quantity"]
                    inventory.save()
                    product["receipt"] = receiptSerailizer.data["id"]

                productSerializer = ProductSerializer(data=productData, many=True)

                if productSerializer.is_valid():
                    productSerializer.save()

                else:
                    print(productSerializer.errors)
                    errorsDict.update(productSerializer.errors)

                    return JsonResponse(errorsDict, status=status.HTTP_400_BAD_REQUEST)

                return JsonResponse(
                    {
                        "productData": productSerializer.data,
                        "receiptData": receiptSerailizer.data,
                        "customerData": customerSerializer.data,
                    },
                    status=status.HTTP_200_OK,
                )

            else:
                errorsDict = {}
                errorsDict.update(customerSerializer.errors)

                return JsonResponse(errorsDict, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            return JsonResponse(error, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
def upload_receipt_signature(request):
    if request.method == "PUT":
        try:
            receipt = Receipts.objects.get(id=request.data["receiptId"])
            receipt.signature = request.FILES["signature"]
            receipt.save()
            receiptData = ReceiptSerializer(receipt)
            data = {
                "message": "Signature updated successfully",
                "data": receiptData.data,
                "status": status.HTTP_200_OK,
            }
            return JsonResponse(data, status=status.HTTP_200_OK)
        except Receipts.DoesNotExist:
            return JsonResponse(
                {"error": "Receipts Does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )


@api_view(["POST"])
def create_business(request):
    if request.method == "POST":
        data = {
            "name": request.data["name"],
            "phone_number": request.data["phone_number"],
            "address": request.data["address"],
            "user": request.user_id,
        }
        if "email_address" in request.data:
            data["email_address"] = request.data["email_address"]
        if "slogan" in request.data:
            data["slogan"] = request.data["slogan"]
        if "logo" in request.FILES:
            data["logo"] = request.FILES["logo"]
        serializer = BusinessInfoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_business(request):
    if request.method == "GET":
        try:
            bus = BusinessInfo.objects.all().order_by("name")
            business = BusinessInfoSerializer(bus, many=True)
            return JsonResponse({"data": business.data}, status=status.HTTP_200_OK)
        except BusinessInfo.DoesNotExist:
            return JsonResponse(
                {"error": "No Business created yet"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as error:
            return JsonResponse({"error": error}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
def update_business(request):
    if request.method == "PUT":
        try:
            if "businessId" not in request.data:
                return JsonResponse(
                    {"error": "Enter businessId"}, status=status.HTTP_400_BAD_REQUEST
                )
            bus = BusinessInfo.objects.get(id=request.data["businessId"])
            if "name" in request.data:
                bus.name = request.data["name"]
            if "phone_number" in request.data:
                bus.phone_number = request.data["phone_number"]
            if "address" in request.data:
                bus.address = request.data["address"]
            if "email_address" in request.data:
                bus.email_address = request.data["email_address"]
            if "slogan" in request.data:
                bus.slogan = request.data["slogan"]
            if "logo" in request.FILES:
                bus.logo = request.FILES["logo"]
            bus.save()
            business = BusinessInfoSerializer(bus, many=False)
            return JsonResponse({"data": business.data}, status=status.HTTP_200_OK)
        except BusinessInfo.DoesNotExist:
            return JsonResponse(
                {"error": "No Business found with this id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as error:
            return JsonResponse({"error": error}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_user_business(request):
    if request.method == "GET":
        try:
            bus = BusinessInfo.objects.filter(user=request.user_id)
            if bus:
                businessSerializer = BusinessInfoSerializer(bus, many=True)
                return JsonResponse(
                    {"data": businessSerializer.data}, status=status.HTTP_200_OK
                )
            else:
                return JsonResponse(
                    {"data": "User does not have any Business registered"},
                    status=status.HTTP_200_OK,
                )

        except Exception as error:
            return JsonResponse({"error": error}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_all_categories(request):
    if request.method == "GET":
        category = Category.objects.filter(user=request.user_id)
        categorySerializer = CategorySerializer(category, many=True)
        return JsonResponse(
            {"data": categorySerializer.data}, status=status.HTTP_200_OK
        )


@api_view(["GET"])
def get_items_inventory(request):
    if request.method == "GET":
        inventory = Inventory.objects.filter(user=request.user_id)
        inventorySerializer = InventorySerializer(inventory, many=True)
        for inv in inventorySerializer.data:
            cat = Category.objects.get(id=inv["category"])
            inv["category"] = CategorySerializer(cat).data
        return JsonResponse(
            {"data": inventorySerializer.data}, status=status.HTTP_200_OK
        )


@api_view(["POST"])
def add_data_to_inventory(request):
    if request.method == "POST":
        if "category_name" not in request.data:
            return JsonResponse(
                {"error": "Enter category_name"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "product_name" not in request.data:
            return JsonResponse(
                {"error": "Enter product_name"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "quantity" not in request.data:
            return JsonResponse(
                {"error": "Enter quantity"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "price" not in request.data:
            return JsonResponse(
                {"error": "Enter price"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            cat = Category.objects.get(
                name=request.data["category_name"], user=request.user_id
            )
            categoryData = CategorySerializer(cat)
        except Category.DoesNotExist:
            categoryData = CategorySerializer(
                data={"name": request.data["category_name"], "user": request.user_id}
            )
            if categoryData.is_valid():
                categoryData.save()
            cat = Category.objects.get(name=request.data["category_name"])
        try:
            inventory = Inventory.objects.get(
                name=request.data["product_name"],
                category=categoryData.data["id"],
                user=request.user_id,
            )
            inventoryData = InventorySerializer(inventory)
        except Inventory.DoesNotExist:
            inventoryData = {
                "name": request.data["product_name"],
                "category": categoryData.data["id"],
                "quantity": request.data["quantity"],
                "user": request.user_id,
                "price": request.data["price"],
            }
            inventoryData = InventorySerializer(data=inventoryData)
            if inventoryData.is_valid():
                inventoryData.save()
                return JsonResponse(
                    {"data": inventoryData.data}, status=status.HTTP_200_OK
                )
            return JsonResponse(
                {"errors": inventoryData.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            quantity = inventoryData.data["quantity"]
            inventory.quantity = quantity + float(request.data["quantity"])
            inventory.category = categoryData.data["id"]
            inventory.price = request.data["price"]
            inventory.name = request.data["product_name"]
            inventory.save()
            inventoryData = InventorySerializer(inventory)
            return JsonResponse({"data": inventoryData.data}, status=status.HTTP_200_OK)
