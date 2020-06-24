import time

import jwt
from django.http import HttpResponseForbidden

from digitalReceipt import settings
from userManagement.models import User


class AuthorizationMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        jwtEscapeUrls = ['/v1/user/otp_register','/v1/user/change_password','/v1/user/email/exists',
                         '/v1/user/register','/v1/user/login','admin']
        print(request.path)
        print(request.path in jwtEscapeUrls)
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
                        user = User.objects.get(id=request.user_id)
                        response = self.get_response(request)
                        print(response)
                        return response
                    else:
                        return HttpResponseForbidden("Token got expired.Login again")
                except Exception as error:
                    return HttpResponseForbidden(error)
            else:
                return HttpResponseForbidden("Non-exposed endpoint, Please Login First")

