from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Receipts)
admin.site.register(Products)
admin.site.register(Notifications)
admin.site.register(Promotions)
admin.site.register(Category)
admin.site.register(Inventory)
admin.site.register(BusinessInfo)