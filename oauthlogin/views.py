import datetime
import jwt
from django.contrib.auth import login
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from fcm_django.models import FCMDevice
from rest_framework import status
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import requests
from userManagement.models import User, UserToken, Token
from userManagement.serializers import UserSerializer, UserTokenSerializer


class HelloView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)


def loginUser(user,userData,request):
    user = User.objects.get(email__exact=user['email'], is_active=True)
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
    data={"token": token.key, "user": userData}
    return data


class GoogleView(APIView):
    def post(self, request):
        if 'deviceType' not in request.data:
            return JsonResponse({"error": "Enter device type (andriod/ios)"},
                                status=status.HTTP_400_BAD_REQUEST)
        if 'registration_id' not in request.data:
            return JsonResponse({"error": "Enter registration id of device"},
                                status=status.HTTP_400_BAD_REQUEST)
        if not (request.data['deviceType'] == 'andriod' or request.data['deviceType'] == 'ios'):
            return JsonResponse({"error": "Enter valid device type (andriod/ios)"},
                                status=status.HTTP_400_BAD_REQUEST)
        if "token" not in request.data:
            return JsonResponse({"error": "Enter token"},
                                status=status.HTTP_400_BAD_REQUEST)
        payload = {'access_token': request.data["token"]}  # validate the token
        r = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', params=payload)
        data = json.loads(r.text)
        if 'error' in data:
            content = {'message': 'wrong google token / this google token is already expired.'}
            return Response(content)
        # create user if not exist
        print(data)
        try:
            user = User.objects.get(email=data['email'])
            userData = UserSerializer(user, many=False).data
            data = loginUser(userData,user,request)
            return JsonResponse(data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            user = {
                'email': data['email'],
                'username': data['email'],
                'password': data['email'],
            }
            serializer = UserSerializer(data=user)
            # provider random default password
            if serializer.is_valid():
                serializer.save()
                user = User.objects.get(email=data['email'])
                userData = UserSerializer(user, many=False).data
                data = loginUser(userData,user,request)
                return JsonResponse(data, status=status.HTTP_200_OK)
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
