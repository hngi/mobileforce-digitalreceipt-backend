import datetime
import jwt
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
from userManagement.models import User
from userManagement.serializers import UserSerializer


class HelloView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)


def login(user):
    user = User.objects.get(email_address=user['email_address'], password=user['password'])
    userData = UserSerializer(user, many=False).data
    userData['exp'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=7 * 86400)
    token = jwt.encode(userData, 'b&!_55_-n0p33)lx=#)$@h#9u13kxz%ucughc%k@w_^x0gyz!b', algorithm='HS256')
    fcm_device = FCMDevice.objects.create(
        type=userData['deviceType'],
        registration_id=userData['registration_id'])
    fcm_device.send_message(title="Notification", body="Login successful",
                            data={"click_action": "FLUTTER_NOTIFICATION_CLICK"})
    data = {
        'message': 'Retreived token successfully',
        'data': {
            '_id': userData['id'],
            'auth_token': token.decode("utf-8")
        },
        "status": status.HTTP_200_OK
    }
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
        try:
            User.objects.filter(email_address=data['email']).update(registration_id=request.data['registration_id'],
                                                                    deviceType=request.data['deviceType'],
                                                                    active=True)
            user = User.objects.get(email_address=data['email'])
            userData = UserSerializer(user, many=False).data
            data = login(userData)
            return JsonResponse(data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            user = {
                'email_address': data['email'],
                'name': data['email'],
                'password': make_password(BaseUserManager().make_random_password()),
                'registration_id': request.data['registration_id'],
                'deviceType': request.data['deviceType'],
                'active': True,
            }
            serializer = UserSerializer(data=user)
            # provider random default password
            if serializer.is_valid():
                serializer.save()
                user = User.objects.get(email_address=data['email'])
                userData = UserSerializer(user, many=False).data
                data = login(userData)
                return JsonResponse(data, status=status.HTTP_200_OK)
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
