import datetime

import jwt
from django.contrib.auth import get_user_model, login
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.core.validators import validate_email
from fcm_django.models import FCMDevice
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
import random as r

from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from businessManagement.models import Notifications
from businessManagement.serializers import NotificationsSerializer
from digitalReceipt import settings
from services.email_verification import Gmail
from .models import User, SecurityQuestion, Token, UserToken
from .serializers import UserSerializer, SecurityQuestionSerializer, UserDetailsSerializer, UserTokenSerializer


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
                email=request.query_params.get("email_address")
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
                userData = User.objects.get(email=request.data["email_address"])
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
                userData = User.objects.get(email=request.data["email_address"])
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
            user = User.objects.get(email=request.data["email_address"])
            userData = UserSerializer(user).data
            if not check_password(request.data["current_password"], userData['password']):
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
            userToken = UserToken.objects.get(id=request.userToken_id)
            FCMDevice.objects.filter(
                type=userToken.deviceType, registration_id=userToken.registration_id
            ).delete()
            Token.objects.get(key=request.key).delete()
            userToken.delete()
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
def send_notifications_all_now(request):
    if request.method == "POST":
        if "title" not in request.data:
            return JsonResponse(
                {"error": "Enter title"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "message" not in request.data:
            return JsonResponse(
                {"error": "Enter message"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:

            fcm_device = FCMDevice.objects.all()
            fcm_device.send_message(
                title=request.data["title"],
                body=request.data["message"],
                data={"click_action": "FLUTTER_NOTIFICATION_CLICK"},
            )
            data = {"message": "sent successfully", "status": status.HTTP_200_OK}
            return JsonResponse(data, status=status.HTTP_200_OK)
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


@api_view(["GET"])
def device_logged(request, registrationId):
    if request.method == "GET":
        try:
            token = UserToken.objects.filter(registration_id=registrationId)
            return JsonResponse(
                {"logged": len(token) != 0},
                status=status.HTTP_200_OK,
            )
        except Exception as error:
            return JsonResponse({"message": error}, status=status.HTTP_400_BAD_REQUEST, )


class SecurityAPIs(viewsets.GenericViewSet):
    serializer_class = SecurityQuestionSerializer

    def get_queryset(self):
        return None

    def list(self, request):
        """getting the list of questions"""
        questions = SecurityQuestion.objects.all()
        return JsonResponse({'questions': SecurityQuestionSerializer(questions, many=True).data},
                            status=status.HTTP_200_OK)


class UserAPIs(viewsets.GenericViewSet):
    """
        Handling user api that are dont need authentication
    """
    serializer_class = UserSerializer

    permission_classes = (AllowAny,)

    def get_queryset(self):
        return None

    @action(detail=False, methods=['post'])
    def register(self, request):
        """
            Registering user
            User needs to enter username,email,password
        """
        print("email")
        if "email" not in request.data:
            return JsonResponse(
                {"error": "Enter email address"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "username" not in request.data:
            return JsonResponse(
                {"error": "Enter name"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "password" not in request.data:
            return JsonResponse(
                {"error": "Enter password"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "securityQuestion1" not in request.data:
            return JsonResponse(
                {"error": "Enter securityQuestion1"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "securityQuestion2" not in request.data:
            return JsonResponse(
                {"error": "Enter securityQuestion2"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "securityAnswer1" not in request.data:
            return JsonResponse(
                {"error": "Enter securityAnswer1"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "securityAnswer2" not in request.data:
            return JsonResponse(
                {"error": "Enter securityAnswer2"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            validate_email(request.data["email"])
        except ValidationError as e:
            return JsonResponse(
                {"error": "Enter correct email address"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Validating if the username already exists
        user = User.objects.filter(username=request.data['username'])
        if len(user) != 0:
            return JsonResponse(
                {"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST
            )
        # Validating if the email already exists
        user = User.objects.filter(email=request.data['email'])
        if len(user) != 0:
            return JsonResponse(
                {"error": "Email address already exists"}, status=status.HTTP_400_BAD_REQUEST
            )
        # Checking if all the valid fields are entere
        VALID_USER_FIELDS = [f.name for f in get_user_model()._meta.fields]
        # Creating user
        data = {
            'email': request.data['email'],
            'username': request.data['username'],
            'password': request.data['password']
        }
        # Creating user
        serialized = UserSerializer(data=data)
        if serialized.is_valid():
            user_data = {field: data for (field, data) in data.items() if field in VALID_USER_FIELDS}
            user = get_user_model().objects.create_user(
                **user_data
            )
            userDetails = {
                'securityQuestion1': request.data['securityQuestion1'],
                'securityQuestion2': request.data['securityQuestion2'],
                'securityAnswer1': request.data['securityAnswer1'],
                'securityAnswer2': request.data['securityAnswer2'],
                'user': user.id
            }
            if 'is_premium_user' in request.data:
                userDetails['is_premium_user'] = request.data['is_premium_user']
            serializer = UserDetailsSerializer(data=userDetails)
            if serializer.is_valid():
                serializer.save()
            print(serializer.errors)
            return Response(UserSerializer(instance=user).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """
                   Login
                   User needs to enter username,password
        """
        print("email")
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
        print(request.data)
        try:
            # Checking  if the user exists using the username and also checking if the user is active
            # Here the user is inactive if the user deleted his/her account
            user = User.objects.get(email__exact=request.data['email_address'], is_active=True)
            print(user.id)
            # If the username matches in any of the user doc
            # checking if the passwords are matching
            if user is not None and user.check_password(request.data['password']) == True:
                # UserTokenSerializer
                reg_id = request.data["registration_id"]
                fcm_device = FCMDevice.objects.filter(
                    type=request.data["deviceType"], registration_id=reg_id
                )

                if len(fcm_device) == 0:
                    fcm_device = FCMDevice.objects.create(
                        type=request.data["deviceType"], registration_id=reg_id
                    )
                    tokenSerailizer = UserTokenSerializer(data={
                        'registration_id': reg_id,
                        'deviceType': request.data["deviceType"],
                        'user': user.id
                    })
                    if tokenSerailizer.is_valid():
                        tokenSerailizer.save()
                else:
                    fcm_device = fcm_device[0]
                userToken = UserToken.objects.get(registration_id=reg_id, deviceType=request.data["deviceType"])
                # deleting the token if the user has already one
                token = Token.objects.filter(user=user, userToken=userToken)
                if len(token) == 0:
                    login(request, user)
                    token = Token.objects.create(user=request.user, userToken=userToken)
                else:
                    token = token[0]
                fcm_device.send_message(
                    title="Notification",
                    body="Login successful",
                    data={"click_action": "FLUTTER_NOTIFICATION_CLICK"},
                )
                userData = UserSerializer(user).data
                return JsonResponse(
                    {"token": token.key, "user": userData}, status=status.HTTP_200_OK
                )
            else:
                return JsonResponse(
                    {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
                )
        except User.DoesNotExist:
            return JsonResponse(
                {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['put'])
    def forgot_password(self, request):
        """
                          Forgot password
                          User needs to enter email,password
               """
        if "email_address" not in request.data:
            return JsonResponse(
                {"error": "Enter password"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "password" not in request.data:
            return JsonResponse(
                {"error": "Enter password"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            # checking if the user exists with the given email id
            user = User.objects.get(email=request.data['email_address'])
            # setting the password
            user.set_password(request.data['password'])
            user.save()
            UserToken.objects.filter(user=user.id).delete()
            Token.objects.filter(user=user.id).delete()
            return JsonResponse(
                {"data": UserSerializer(user).data}, status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            # if the user does not exist
            return JsonResponse(
                {"error": "Invalid email address"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as error:
            return JsonResponse(
                {"error": error}, status=status.HTTP_400_BAD_REQUEST
            )
