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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
#from .router import router
from rest_framework.authtoken import views
from django.views.generic import TemplateView

from . import settings
from .cron.notification import start
from .views import index
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from oauthlogin import views


schema_view = get_schema_view(
   openapi.Info(
      title="Digital Receipt API",
      default_version='v1',
      description="Test the API here using Swagger, For postman please go here: https://documenter.getpostman.com/view/6370926/T17AkB4N?version=latest ",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('checkserver/',index, name='index' ),
    path('v1/user/', include('userManagement.urls')),
    path('v1/business/', include('businessManagement.urls')),
    path('v1/customer/', include('customers.urls')),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('hello/', views.HelloView.as_view(), name='hello'),
    path('google', views.GoogleView.as_view(), name='google'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

start()
