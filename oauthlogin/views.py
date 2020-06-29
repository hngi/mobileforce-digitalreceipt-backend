import datetime
import jwt
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from fcm_django.models import FCMDevice
from rest_framework import generics, permissions, status, views
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import requests
from userManagement.models import User
from userManagement.serializers import UserSerializer
#fb dependencies 
from requests.exceptions import HTTPError
from social_django.utils import load_strategy, load_backend
from social_core.backends.oauth import BaseOAuth2
from social_core.exceptions import MissingBackend, AuthTokenError, AuthForbidden
from . import serializers

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
                'password': make_password(BaseUserManager().make_random_password())[:40],
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

#Facebook view 
class SocialLoginView(generics.GenericAPIView):
    """Log in using facebook"""
    serializer_class = serializers.SocialSerializer
    permission_classes = [permissions.AllowAny]
 
    def post(self, request):
        """Authenticate user through the provider and access_token"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        provider = serializer.data.get('provider', None)
        strategy = load_strategy(request)
 
        try:
            backend = load_backend(strategy=strategy, name=provider,
            redirect_uri=None)
 
        except MissingBackend:
            return Response({'error': 'Please provide a valid provider'},
            status=status.HTTP_400_BAD_REQUEST)
        try:
            if isinstance(backend, BaseOAuth2):
                access_token = serializer.data.get('access_token')
            user = backend.do_auth(access_token)
        except HTTPError as error:
            return Response({
                "error": {
                    "access_token": "Invalid token",
                    "details": str(error)
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        except AuthTokenError as error:
            return Response({
                "error": "Invalid credentials",
                "details": str(error)
            }, status=status.HTTP_400_BAD_REQUEST)
 
        try:
            authenticated_user = backend.do_auth(access_token, user=user)
       
        except HTTPError as error:
            return Response({
                "error":"invalid token",
                "details": str(error)
            }, status=status.HTTP_400_BAD_REQUEST)
       
        except AuthForbidden as error:
            return Response({
                "error":"invalid token",
                "details": str(error)
            }, status=status.HTTP_400_BAD_REQUEST)
 
        if authenticated_user and authenticated_user.is_active:
            #generate JWT token
            login(request, authenticated_user)
            data={
                "token": jwt_encode_handler(
                    jwt_payload_handler(user)
                )}
            #customize the response to your needs
            response = {
                "email": authenticated_user.email,
                "username": authenticated_user.username,
                "token": data.get('token')
            }
            return Response(status=status.HTTP_200_OK, data=response)