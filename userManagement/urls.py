from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers

from .views import (
    user_registration_send_email,
    create_user,
    change_password,
    check_if_user_exists,
    create_notification,
    logout,
    forgot_password,
    get_all_notifications,
    user_send_email_pdf,
    get_user_details, user_send_email, send_notifications_all_now, SecurityAPIs, UserAPIs, device_logged)

router = routers.DefaultRouter()
router.register(r'', SecurityAPIs, basename='game')

userRouter = routers.DefaultRouter()
userRouter.register(r'', UserAPIs, basename='user')

urlpatterns = [
    url(r'^questions/', include(router.urls)),
    path("otp_register", user_registration_send_email),
    path("register", create_user),
    path("login", login),
    url(r'^', include(userRouter.urls)),
    path("change_password", change_password),
    path('send_email', user_send_email),
    path("email/exists", check_if_user_exists),
    path("info", get_user_details),
    path("logout", logout),
    path("notification/create", create_notification),
    path("notification/all", get_all_notifications),
    path("notification", send_notifications_all_now),
    path("sendemail/pdf", user_send_email_pdf),
    path("<str:registrationId>/device/logged", device_logged)
]
