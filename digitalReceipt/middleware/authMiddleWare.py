import time

import jwt
from django.http import HttpResponseForbidden, JsonResponse
from rest_framework import status

from userManagement.models import User


class AuthorizationMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        jwtEscapeUrls = ['/','/v1/user/otp_register','/v1/user/change_password','/v1/user/email/exists',
                         '/v1/user/register','/v1/user/login','/google']
        if 'media' in request.path:
            response = self.get_response(request)
            return response
        if request.path in jwtEscapeUrls:
            response = self.get_response(request)
            return response
        else:
            header_token = request.META.get('HTTP_TOKEN', None)
            if header_token is not None:
                try:
                    vaildate_token = jwt.decode(header_token, "b&!_55_-n0p33)lx=#)$@h#9u13kxz%ucughc%k@w_^x0gyz!b", algorithm='HS256')
                    if time.time() < vaildate_token['exp']:
                        request.user_id = vaildate_token['id']
                        try:
                            user = User.objects.get(id=request.user_id)
                            response = self.get_response(request)
                            return response
                        except User.doesNotExist:
                            return JsonResponse({"error": "Invalid session.Please login"},
                                                status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        return JsonResponse({"error": "Please Login to renew your session"},
                                            status=status.HTTP_401_UNAUTHORIZED)
                except Exception as error:
                    return JsonResponse({"error": error},
                                        status=status.HTTP_400_BAD_REQUEST)
            else:
                return JsonResponse({"error": "Please Login to view data"},
                                    status=status.HTTP_401_UNAUTHORIZED)

