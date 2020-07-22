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
    user_send_email_pdf,
    get_user_details, user_send_email, send_notifications_all_now)

urlpatterns = [
    path("otp_register", user_registration_send_email),
    path("register", create_user),
    path("login", login),
    path("change_password", change_password),
    path('send_email',user_send_email),
    path("forgot_password", forgot_password),
    path("email/exists", check_if_user_exists),
    path("info", get_user_details),
    path("logout", logout),
    path("notification/create", create_notification),
    path("notification/all", get_all_notifications),
    path("notification", send_notifications_all_now),
    path("notification/create/send/now", send_notification_now),
    path("sendemail/pdf",user_send_email_pdf)
]
