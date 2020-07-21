from django.urls import path
from .views import create_promotion, update_promotion, delete_promotion

urlpatterns = [
    path("promotion/create", create_promotion),
    path("promotion/update", update_promotion),
    path("promotion/<int:id>", delete_promotion),
]
