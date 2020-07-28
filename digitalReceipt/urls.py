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
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


from . import settings
# from .cron.notification import start

from oauthlogin import views


schema_view = get_schema_view(
    openapi.Info(
        title="Digital Receipt API",
        default_version="v1",
        description="Test the API here using Swagger, For postman please go here: https://documenter.getpostman.com/view/6370926/T17AkB4N?version=latest ",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("v1/business/", include("businessManagement.urls")),
    path("v1/customer/", include("customers.urls")),
    path("v1/user/", include("userManagement.urls")),
    path("", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("google", views.GoogleView.as_view(), name="google"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# start()
