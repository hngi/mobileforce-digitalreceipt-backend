"""digitalReceipt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
#from .router import router
from rest_framework.authtoken import views
from django.views.generic import TemplateView
from .cron.notification import start
from .views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('checkserver/',index, name='index' ),
    path('auth/', include('authapp.urls')),
    path('v1/user/', include('userManagement.urls')),
    path('v1/business/', include('businessManagement.urls')),
    path('v1/customer/', include('customers.urls')),
    path('google/', TemplateView.as_view(template_name = 'login/index.html')),
    path('accounts/google/login/callback/logged/', TemplateView.as_view(template_name = 'login/loged.html')),
]

start()
