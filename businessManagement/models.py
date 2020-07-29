from datetime import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
import uuid

# Create your models here.
from customers.models import CustomerDetails


def user_directory_path(instance, filename):
    img_extension = filename.split('.')[1]
    return 'receipts/{0}.{1}'.format(instance.id, img_extension)


def logo_directory_path(instance, filename):
    img_extension = filename.split('.')[1]
    return 'logos/{0}.{1}'.format(instance.id, img_extension)


class Receipts(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    receipt_number = models.CharField(
        null=True, max_length=1000
    )  # need to customize this
    date = models.DateTimeField(null=True, default=datetime.now, blank=True)
    font = models.CharField(null=True, max_length=1000)
    color = models.CharField(null=True, max_length=1000)
    preset = models.BooleanField(null=True, default=False)
    paid_stamp = models.BooleanField(null=True, default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    issued = models.BooleanField(null=True, default=False)
    deleted = models.BooleanField(null=True, default=False)
    signature = models.FileField(null=True, upload_to=user_directory_path)
    platform = models.CharField(max_length=50, null=True)
    partPayment = models.BooleanField(null=True, default=False)
    partPaymentDateTime = models.DateTimeField(null=True, default=datetime.now)
    currency = models.CharField(max_length=14, null=True)
    sellerName = models.CharField(max_length=120, null=True)
    customer = models.ForeignKey(CustomerDetails, on_delete=models.CASCADE, null=True)
    active = models.BooleanField(null=True, default=True)


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


class Products(models.Model):
    receipt = models.ForeignKey(Receipts, on_delete=models.CASCADE, null=False)
    category_name = models.CharField(null=True, max_length=100)
    name = models.CharField(null=False, max_length=100)
    quantity = models.PositiveIntegerField(
        null=False, validators=[MinValueValidator(1)]
    )
    unit_price = models.FloatField(null=False, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    tax_amount = models.FloatField(null=False, validators=[MinValueValidator(0)], default=Decimal('0.00'))
    discount = models.DecimalField(decimal_places=2, max_digits=10, default=Decimal('0.00'))
    updated_at = models.DateTimeField(auto_now=True)
    unit = models.CharField(max_length=20, null=True)


class Notifications(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivered = models.BooleanField(default=False)
    title = models.CharField(null=True, max_length=100)
    message = models.CharField(null=True, max_length=100)
    date_to_deliver = models.DateTimeField(null=True, default=datetime.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BusinessInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(null=False, max_length=150)
    phone_number = models.CharField(max_length=50, null=False)
    address = models.CharField(max_length=200, null=False)
    slogan = models.CharField(null=True, max_length=50)
    email_address = models.CharField(null=True, max_length=100)
    logo = models.FileField(null=True, upload_to=logo_directory_path)
    user = models.ForeignKey(User, unique=True, on_delete=models.CASCADE)
    signature=models.CharField(max_length=200000, null=True)
    currency=models.CharField(max_length=20, null=True)

class Inventory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(null=False, max_length=100)
    quantity = models.PositiveIntegerField(
        null=False, validators=[MinValueValidator(1)]
    )
    unit = models.CharField(max_length=20, null=True)
    price = models.FloatField(null=False, validators=[MinValueValidator(0)], default=Decimal('0.00'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    tax_amount = models.FloatField(null=False, validators=[MinValueValidator(0)], default=Decimal('0.00'))
    discount = models.DecimalField(decimal_places=2, max_digits=10, default=Decimal('0.00'))


class Promotions(models.Model):
    imageUrl = models.CharField(null=True, max_length=1000)
    text = models.CharField(null=True, max_length=1000)
    link = models.CharField(null=True, max_length=1000)
    versionNumber = models.CharField(null=True, max_length=1000)
    isPromotion = models.BooleanField(null=True, default=True)
