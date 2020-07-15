import datetime

import jwt
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.core.validators import validate_email
from fcm_django.models import FCMDevice
from rest_framework import status
from rest_framework.decorators import api_view
import random as r

from businessManagement.models import Notifications
from businessManagement.serializers import NotificationsSerializer
from digitalReceipt import settings
from services.email_verification import Gmail
from .models import User
from .serializers import UserSerializer


def otpgen():
    otp = ""
    for i in range(4):
        otp += str(r.randint(1, 9))
    return otp


def emailOtpMessage(otp):
    html = (
            """
            <html>
                <body>
                    <p>Hello,<br><br>
                    Thanks for registering in our application<br><br>
                    Please verify your OTP. Your OTP number is below
                    <br><br>
                     <b>"""
            + otp
            + """</b>
                    </p>
                </body>
            </html>
        """
    )
    return html


@api_view(["GET"])
def check_if_user_exists(request):
    if request.method == "GET":
        try:
            if request.query_params.get("email_address") is None:
                return JsonResponse(
                    {"error": "Enter email address"}, status=status.HTTP_400_BAD_REQUEST
                )
            print(request.query_params.get("email_address"))
            user = User.objects.get(
                email_address=request.query_params.get("email_address")
            )
            userData = UserSerializer(user, many=False).data
            data = {
                "message": "Email exists successfully",
                "data": userData,
                "status": status.HTTP_200_OK,
            }
            return JsonResponse(data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return JsonResponse(
                {"error": "User Does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return JsonResponse({"error": e}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def user_registration_send_email(request):
    if request.method == "POST":
        if "email_address" not in request.data:
            return JsonResponse(
                {"error": "Enter email address"}, status=status.HTTP_400_BAD_REQUEST
            )
        email_address = request.data["email_address"]
        try:
            validate_email(email_address)
        except ValidationError as e:
            return JsonResponse(
                {"error": "Enter valid email address"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            # Check if there is any user with this email address
            try:
                userData = User.objects.get(email_address=request.data["email_address"])
            except User.DoesNotExist:
                otp = otpgen()
                try:
                    gm = Gmail(settings.email_address, settings.email_app_password)
                    gm.send_message(
                        "Email OTP Verification - Digital Receipt",
                        emailOtpMessage(otp),
                        request.data["email_address"],
                    )
                    return JsonResponse(
                        {
                            "data": {
                                "otp": otp,
                                "email_address": request.data["email_address"],
                            },
                            "message": "Sent email with otp successfully",
                            "status": status.HTTP_200_OK,
                        },
                        status=status.HTTP_200_OK,
                    )
                except Exception as error:
                    return JsonResponse(
                        {"error": error}, status=status.HTTP_400_BAD_REQUEST
                    )
            except Exception as e:
                return JsonResponse({"error": e}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return JsonResponse(
                    {"error": "Email address is already registered"},
                    status=status.HTTP_400_BAD_REQUEST,
                )


@api_view(["POST"])
def user_send_email(request):
    if request.method == "POST":
        if "email_address" not in request.data:
            return JsonResponse(
                {"error": "Enter email address"}, status=status.HTTP_400_BAD_REQUEST
            )
        email_address = request.data["email_address"]
        try:
            validate_email(email_address)
        except ValidationError as e:
            return JsonResponse(
                {"error": "Enter valid email address"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            # Check if there is any user with this email address
            try:
                userData = User.objects.get(email_address=request.data["email_address"])
                otp = otpgen()
                try:
                    gm = Gmail(settings.email_address, settings.email_app_password)
                    gm.send_message(
                        "Forgot Password OTP  - Digital Receipt",
                        emailOtpMessage(otp),
                        request.data["email_address"],
                    )
                    return JsonResponse(
                        {
                            "data": {
                                "otp": otp,
                                "email_address": request.data["email_address"],
                            },
                            "message": "Sent email with otp successfully",
                            "status": status.HTTP_200_OK,
                        },
                        status=status.HTTP_200_OK,
                    )
                except Exception as error:
                    return JsonResponse(
                        {"error": error}, status=status.HTTP_400_BAD_REQUEST
                    )
            except User.DoesNotExist:
                return JsonResponse({"error": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return JsonResponse({"error": e}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return JsonResponse(
                    {"error": "Email address is already registered"},
                    status=status.HTTP_400_BAD_REQUEST,
                )


@api_view(["POST"])
def user_send_email_pdf(request):
    if request.method == "POST":
        if "email_address" not in request.data:
            return JsonResponse(
                {"error": "Enter email address"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "subject" not in request.data:
            return JsonResponse(
                {"error": "Enter subject"}, status=status.HTTP_400_BAD_REQUEST
            )
        email_address = request.data["email_address"]
        try:
            validate_email(email_address)
        except ValidationError as e:
            return JsonResponse(
                {"error": "Enter valid email address"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            # Check if there is any user with this email address
            try:
                gm = Gmail(settings.email_address, settings.email_app_password)
                gm.send_pdf_message(
                    request.data["subject"],
                    request.data["email_address"],
                    request.FILES['receipt']
                )
                return JsonResponse(
                    {
                        "message": "Sent email with successfully",
                        "status": status.HTTP_200_OK,
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return JsonResponse({"error": e}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def create_user(request):
    if request.method == "POST":
        if "email_address" not in request.data:
            return JsonResponse(
                {"error": "Enter email address"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "name" not in request.data:
            return JsonResponse(
                {"error": "Enter name"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "password" not in request.data:
            return JsonResponse(
                {"error": "Enter password"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            validate_email(request.data["email_address"])
        except ValidationError as e:
            return JsonResponse(
                {"error": "Enter correct email address"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            request.data._mutable = True
            request.data["password"] = make_password(request.data["password"])
            request.data._mutable = False
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=status.HTTP_200_OK)
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def login(request):
    if request.method == "POST":
        if "email_address" not in request.data:
            return JsonResponse(
                {"error": "Enter email address"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "password" not in request.data:
            return JsonResponse(
                {"error": "Enter password"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "deviceType" not in request.data:
            return JsonResponse(
                {"error": "Enter device type (andriod/ios)"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if "registration_id" not in request.data:
            return JsonResponse(
                {"error": "Enter registration id of device"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not (
                request.data["deviceType"] == "andriod"
                or request.data["deviceType"] == "ios"
        ):
            return JsonResponse(
                {"error": "Enter valid device type (andriod/ios)"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(
                email_address=request.data["email_address"],
            )
            userData = UserSerializer(user, many=False).data
            if not check_password(request.data["password"], userData['password']):
                return JsonResponse({"error": "Invalid username/password"}, status=status.HTTP_400_BAD_REQUEST)
            if userData['active']:
                return JsonResponse({"error": "Cannot login in more that one device"},
                                    status=status.HTTP_400_BAD_REQUEST)
            userData["exp"] = datetime.datetime.utcnow() + datetime.timedelta(
                seconds=7 * 86400
            )
            token = jwt.encode(
                userData,
                "b&!_55_-n0p33)lx=#)$@h#9u13kxz%ucughc%k@w_^x0gyz!b",
                algorithm="HS256",
            )
            reg_id = request.data["registration_id"]
            fcm_device = FCMDevice.objects.create(
                type=request.data["deviceType"], registration_id=reg_id
            )
            fcm_device.send_message(
                title="Notification",
                body="Login successful",
                data={"click_action": "FLUTTER_NOTIFICATION_CLICK"},
            )
            User.objects.filter(id=userData["id"]).update(
                registration_id=reg_id,
                deviceType=request.data["deviceType"],
                active=True,
            )
            data = {
                "message": "Retreived token successfully",
                "data": {"_id": userData["id"], "auth_token": token.decode("utf-8")},
                "status": status.HTTP_200_OK,
            }
            return JsonResponse(data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return JsonResponse(
                {"error": "User Does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return JsonResponse({"error": e}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
def change_password(request):
    if request.method == "PUT":
        if "email_address" not in request.data:
            return JsonResponse(
                {"error": "Enter email address"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "current_password" not in request.data:
            return JsonResponse(
                {"error": "Enter current_password"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "password" not in request.data:
            return JsonResponse(
                {"error": "Enter password"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(email_address=request.data["email_address"])
            userData = UserSerializer(user).data
            if not check_password(request.data["password"], userData['password']):
                return JsonResponse({"error": "Invalid username/password"}, status=status.HTTP_400_BAD_REQUEST)
            userUpdated = User.objects.filter(id=request.user_id
                                              ).update(password=make_password(request.data["password"]))
            print(userUpdated)
            data = {
                "message": "Updated password successfully"
                if userUpdated == 1
                else "Incorrect password entered",
                "status": status.HTTP_200_OK,
            }
            return JsonResponse(data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return JsonResponse(
                {"error": "User Does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return JsonResponse({"error": e}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_user_details(request):
    try:
        user = User.objects.get(id=request.user_id)
        userData = UserSerializer(user, many=False).data
        return JsonResponse(userData, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return JsonResponse(
            {"error": "User Does not exist"}, status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return JsonResponse({"error": e}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
def forgot_password(request):
    if request.method == "PUT":
        if "email_address" not in request.data:
            return JsonResponse(
                {"error": "Enter email address"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "password" not in request.data:
            return JsonResponse(
                {"error": "Enter password"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(email_address=request.data["email_address"])
            userData = UserSerializer(user, many=False).data
            userUpdated = User.objects.filter(
                email_address=request.data["email_address"]
            ).update(password=make_password(request.data["password"]),
                     registration_id=None, deviceType=None, active=False
                     )
            if userData['active']:
                FCMDevice.objects.filter(
                    type=userData["deviceType"], registration_id=userData["registration_id"]
                ).delete()
            data = {
                "message": "Updated password successfully",
                "status": status.HTTP_200_OK,
            }
            return JsonResponse(data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return JsonResponse(
                {"error": "User Does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return JsonResponse({"error": e}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def logout(request):
    if request.method == "POST":
        try:
            user = User.objects.get(id=request.user_id)
            userData = UserSerializer(user, many=False).data
            user = User.objects.filter(id=request.user_id).update(
                registration_id=None, deviceType=None, active=False
            )
            FCMDevice.objects.filter(
                type=userData["deviceType"], registration_id=userData["registration_id"]
            ).delete()
            data = {"message": "Logged out successfully", "status": status.HTTP_200_OK}
            return JsonResponse(data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return JsonResponse(
                {"error": "User Does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return JsonResponse({"error": e}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
def update_registration_id(request):
    if request.method == "PUT":
        if "deviceType" not in request.data:
            return JsonResponse(
                {"error": "Enter device type (andriod/ios)"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if "registration_id" not in request.data:
            return JsonResponse(
                {"error": "Enter registration id of device"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not (
                request.data["deviceType"] == "andriod"
                or request.data["deviceType"] == "ios"
        ):
            return JsonResponse(
                {"error": "Enter valid device type (andriod/ios)"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            User.objects.filter(id=request.user_id).update(
                registration_id=request.data["registration_id"],
                deviceType=request.data["deviceType"],
            )
            data = {"message": "Updated successfully", "status": status.HTTP_200_OK}
            return JsonResponse(data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return JsonResponse(
                {"error": "User Does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return JsonResponse({"error": e}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def send_notification_now(request):
    if request.method == "POST":
        if "user_id" not in request.data:
            return JsonResponse(
                {"error": "Enter user id"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "title" not in request.data:
            return JsonResponse(
                {"error": "Enter title"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "message" not in request.data:
            return JsonResponse(
                {"error": "Enter message"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(id=request.data["user_id"])
            data = {
                "user": request.data["user_id"],
                "delivered": True,
                "title": request.data["title"],
                "message": request.data["message"],
                "date_to_deliver": datetime.datetime.now(),
            }
            notification = NotificationsSerializer(data=data)
            if notification.is_valid():
                notification.save()
            users_data = UserSerializer(user, many=False).data
            if users_data["active"]:
                fcm_device = FCMDevice.objects.get(
                    type=users_data["deviceType"],
                    registration_id=users_data["registration_id"],
                )
                fcm_device.send_message(
                    title=request.data["title"],
                    body=request.data["message"],
                    data={"click_action": "FLUTTER_NOTIFICATION_CLICK"},
                )
                data = {"message": "sent successfully", "status": status.HTTP_200_OK}
                return JsonResponse(data, status=status.HTTP_200_OK)
            else:
                data = {
                    "message": "User is inactive..Saved notification",
                    "status": status.HTTP_400_BAD_REQUEST,
                }
                return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return JsonResponse(
                {"error": "User Does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return JsonResponse({"error": e}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def create_notification(request):
    if request.method == "POST":
        if "user_id" not in request.data:
            return JsonResponse(
                {"error": "Enter user id"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "title" not in request.data:
            return JsonResponse(
                {"error": "Enter title"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "message" not in request.data:
            return JsonResponse(
                {"error": "Enter message"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "date_to_deliver" not in request.data:
            return JsonResponse(
                {"error": "Enter date_to_deliver"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(id=request.data["user_id"])
            data = {
                "user": request.data["user_id"],
                "delivered": False,
                "title": request.data["title"],
                "message": request.data["message"],
                "date_to_deliver": request.data["date_to_deliver"],
            }
            notification = NotificationsSerializer(data=data)
            if notification.is_valid():
                notification.save()
                return JsonResponse(notification.data, status=status.HTTP_200_OK)
            return JsonResponse(notification.errors, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return JsonResponse(
                {"error": "User Does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return JsonResponse({"error": e}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_all_notifications(request):
    if request.method == "GET":
        try:
            notifications = Notifications.objects.filter(user=request.user_id)
            if notifications:
                notificationSerializer = NotificationsSerializer(
                    notifications, many=True
                )
                return JsonResponse(
                    {
                        "message": "Retreived all Notifications for this user",
                        "data": notificationSerializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return JsonResponse(
                    {"message": "There are no notifications created for this User"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as error:
            return JsonResponse({"message": error}, status=status.HTTP_400_BAD_REQUEST, )

@api_view(["PUT"])
def update_user(request):
    if request.method == "PUT":
        try:
            if "UserId" not in request.data:
                return JsonResponse(
                    {"error": "Enter UserId"}, status=status.HTTP_400_BAD_REQUEST
                )
            user = User.objects.get(id=request.data["UserId"])
            if "name" in request.data:
                user.name = request.data["name"]
            if "email_address" in request.data:
                user.email_address = request.data["email_address"]
            if "password" in request.data:
                user.password = request.data["password"]
            if "deviceType" in request.data:
                user.deviceType = request.data["deviceType"]
            user.save()
            users = UserSerializer(user, many=False)
            return JsonResponse({"data": users.data}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return JsonResponse(
                {"error": "No User found with this id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as error:
            return JsonResponse({"error": error}, status=status.HTTP_400_BAD_REQUEST)
