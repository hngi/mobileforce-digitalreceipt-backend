from django.urls import path, include
from rest_framework import routers
from . import views
from .views import create_customer, get_customer

router = routers.DefaultRouter()
router.register(r'customers', views.indexViewSet)

urlpatterns = [
	path('', include(router.urls)),
	path('customers-auth', include('rest_framework.urls', namespace = 'rest_framework')),
	path('customer/<int:id>/', views.single),
	path('register', create_customer),
	path('<int:id>',get_customer)
]