from django.urls import path
from .views import (
	create_promotion, 
	update_promotion, 
	delete_promotion)

urlpatterns = [
    path("create", create_promotion),
    path("update", update_promotion),
    path("<int:id>", delete_promotion),
]
