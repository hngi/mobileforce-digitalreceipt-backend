import time

import jwt
from django.http import HttpResponseForbidden, JsonResponse
from fcm_django.models import FCMDevice
from rest_framework import status

from userManagement.models import User, Token
from userManagement.serializers import UserSerializer


class AuthorizationMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        jwtEscapeUrls = ['/', '/v1/user/otp_register', '/v1/user/forgot_password/', '/v1/user/email/exists',
                         '/v1/user/send_email','/v1/user/notification','/v1/business/promotions',
                         '/v1/user/register/', '/v1/user/login/', '/google', '/v1/user/questions/']
        if 'media' in request.path:
            response = self.get_response(request)
            return response
        if 'admin' in request.path:
            response = self.get_response(request)
            return response
        if 'device/logged' in request.path:
            response = self.get_response(request)
            return response
        if request.path in jwtEscapeUrls:
            response = self.get_response(request)
            return response
        else:
            header_token = request.META.get('HTTP_TOKEN', None)
            if header_token is not None:
                try:
                    token = Token.objects.filter(key=header_token)
                    if len(token) == 0:
                        return JsonResponse({"error": "Permission denied"},
                                            status=status.HTTP_401_UNAUTHORIZED)
                    request.user_id = token[0].user.id
                    request.userToken_id = token[0].userToken.id
                    request.key = header_token
                    user = User.objects.get(id=request.user_id)
                    userData = UserSerializer(user).data
                    response = self.get_response(request)
                    print(request.user_id)
                    return response
                except User.doesNotExist:
                    print("user does not exist")
                    return JsonResponse({"error": "Invalid session.Please login"},
                                        status=status.HTTP_401_UNAUTHORIZED)
                except Exception as error:
                    return JsonResponse({"error": error},
                                        status=status.HTTP_400_BAD_REQUEST)
            else:
                return JsonResponse({"error": "Please Login to view data"},
                                    status=status.HTTP_401_UNAUTHORIZED)
