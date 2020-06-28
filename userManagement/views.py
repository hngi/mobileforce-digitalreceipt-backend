import datetime

import jwt
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.core.validators import validate_email
from fcm_django.models import FCMDevice
from rest_framework import status
from rest_framework.decorators import api_view
import random as r

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
    html = """
            <html>
                <body>
                    <p>Hello,<br><br>
                    Thanks for registering in our application<br><br>
                    Please verify your OTP. Your OTP number is below
                    <br><br>
                     <b>""" + otp + """</b>
                    </p>
                </body>
            </html>
        """
    return html


@api_view(['GET'])
def check_if_user_exists(request):
    if request.method == 'GET':
        try:
            if request.query_params.get('email_address') is None:
                return JsonResponse({"error": "Enter email address"},
                                    status=status.HTTP_400_BAD_REQUEST)
            print(request.query_params.get('email_address'))
            user = User.objects.get(email_address=request.query_params.get('email_address'))
            userData = UserSerializer(user, many=False).data
            data = {
                'message': 'Email exists successfully',
                'data': userData,
                "status": status.HTTP_200_OK
            }
            return JsonResponse(data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return JsonResponse({
                'error': "User Does not exist"
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({
                'error': e
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def user_registration_send_email(request):
    if request.method == 'POST':
        if 'email_address' not in request.data:
            return JsonResponse({"error": "Enter email address"},
                                status=status.HTTP_400_BAD_REQUEST)
        email_address = request.data['email_address']
        try:
            validate_email(email_address)
        except ValidationError as e:
            return JsonResponse({
                "error": "Enter valid email address"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Check if there is any user with this email address
            try:
                userData = User.objects.get(email_address=request.data['email_address'])
            except User.DoesNotExist:
                otp = otpgen()
                try:
                    gm = Gmail(settings.email_address, settings.email_app_password)
                    gm.send_message("Email OTP Verification - Digital Receipt", emailOtpMessage(otp),
                                    request.data['email_address'])
                    return JsonResponse({
                        "data": {
                            "otp": otp,
                            "email_address": request.data['email_address']
                        },
                        "message": "Sent email with otp successfully",
                        "status": status.HTTP_200_OK
                    }, status=status.HTTP_200_OK)
                except Exception as error:
                    return JsonResponse({
                        "error": error
                    }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return JsonResponse({
                    "error": e
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return JsonResponse({
                    "error": "Email address is already registered"
                }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_user(request):
    if request.method == 'POST':
        if 'email_address' not in request.data:
            return JsonResponse({"error": "Enter email address"},
                                status=status.HTTP_400_BAD_REQUEST)
        if 'name' not in request.data:
            return JsonResponse({"error": "Enter name"},
                                status=status.HTTP_400_BAD_REQUEST)
        if 'password' not in request.data:
            return JsonResponse({"error": "Enter password"},
                                status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_email(request.data['email_address'])
        except ValidationError as e:
            return JsonResponse({
                "error": "Enter correct email address"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=status.HTTP_200_OK)
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        if 'email_address' not in request.data:
            return JsonResponse({"error": "Enter email address"},
                                status=status.HTTP_400_BAD_REQUEST)
        if 'password' not in request.data:
            return JsonResponse({"error": "Enter password"},
                                status=status.HTTP_400_BAD_REQUEST)
        if 'deviceType' not in request.data:
            return JsonResponse({"error": "Enter device type (andriod/ios)"},
                                status=status.HTTP_400_BAD_REQUEST)
        if 'registration_id' not in request.data:
            return JsonResponse({"error": "Enter registration id of device"},
                                status=status.HTTP_400_BAD_REQUEST)
        if not (request.data['deviceType'] == 'andriod' or request.data['deviceType'] == 'ios'):
            return JsonResponse({"error": "Enter valid device type (andriod/ios)"},
                                status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email_address=request.data['email_address'], password=request.data['password'])
            userData = UserSerializer(user, many=False).data
            userData['exp'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=7 * 86400)
            token = jwt.encode(userData, 'b&!_55_-n0p33)lx=#)$@h#9u13kxz%ucughc%k@w_^x0gyz!b', algorithm='HS256')
            reg_id = request.data['registration_id']
            fcm_device = FCMDevice.objects.create(
                type=request.data['deviceType'],
                registration_id=reg_id)
            fcm_device.send_message(title="Notification", body="Login successful",
                                    data={"click_action": "FLUTTER_NOTIFICATION_CLICK"})
            User.objects.filter(id=userData['id']).update(registration_id=reg_id, deviceType=request.data['deviceType'],
                                                          active=True)
            data = {
                'message': 'Retreived token successfully',
                'data': {
                    '_id': userData['id'],
                    'auth_token': token.decode("utf-8")
                },
                "status": status.HTTP_200_OK
            }
            return JsonResponse(data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return JsonResponse({
                'error': "User Does not exist"
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({
                'error': e
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def change_password(request):
    if request.method == 'PUT':
        if 'email_address' not in request.data:
            return JsonResponse({"error": "Enter email address"},
                                status=status.HTTP_400_BAD_REQUEST)
        if 'password' not in request.data:
            return JsonResponse({"error": "Enter password"},
                                status=status.HTTP_400_BAD_REQUEST)
        try:
            userUpdated = User.objects.filter(email_address=request.data['email_address']).update(
                password=request.data['password'])
            data = {
                'message': 'Updated password successfully',
                "status": status.HTTP_200_OK
            }
            return JsonResponse(data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return JsonResponse({
                'error': "User Does not exist"
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({
                'error': e
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def logout(request):
    if request.method == 'PUT':
        try:
            user_data = User.objects.get(id=request.user_id)
            user = User.objects.filter(id=request.user_id).update(
                registration_id=None, deviceType=None,
                active=False)
            FCMDevice.objects.filter(type=user_data.deviceType,
                                     registration_id=user_data.registration_id).delete()
            data = {
                'message': 'Logged out successfully',
                "status": status.HTTP_200_OK
            }
            return JsonResponse(data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return JsonResponse({
                'error': "User Does not exist"
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({
                'error': e
            }, status=status.HTTP_400_BAD_REQUEST)
