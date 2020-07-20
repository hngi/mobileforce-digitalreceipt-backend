from .views import add_promotion
from django.urls import path

url_patterns = [path("promotion/create", add_promotion)]
