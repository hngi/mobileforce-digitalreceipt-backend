from django.urls import path

from .views import (
    user_registration_send_email,
    create_user,
    login,
    change_password,
    check_if_user_exists,
    create_notification,
    send_notification_now,
    logout,
    forgot_password,
    get_all_notifications,
)

urlpatterns = [
    path("otp_register", user_registration_send_email),
    path("register", create_user),
    path("login", login),
    path("change_password", change_password),
    path("forgot_password", forgot_password),
    path("email/exists", check_if_user_exists),
    path("logout", logout),
    path("notification/create", create_notification),
    path("notification/all", get_all_notifications),
    path("notification/create/send/now", send_notification_now),
]
