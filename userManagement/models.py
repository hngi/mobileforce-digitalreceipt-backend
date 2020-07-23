import rest_framework.authtoken.models
from django.contrib.auth.models import User
from django.db import models
import uuid
from django.utils.translation import ugettext_lazy as _

import rest_framework.authentication


class UserToken(models.Model):
    registration_id = models.CharField(max_length=10000, null=True)
    deviceType = models.CharField(max_length=10000, null=True, default=None)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)


class SecurityQuestion(models.Model):
    question = models.CharField(max_length=1000, primary_key=True, null=False, unique=True)
    active = models.BooleanField(default=True, null=True)


class UserDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=False, blank=True)
    securityQuestion1 = models.CharField(max_length=1000, null=False)
    securityQuestion2 = models.CharField(max_length=1000, null=False)
    securityAnswer1 = models.CharField(max_length=1000, null=False)
    securityAnswer2 = models.CharField(max_length=1000, null=False)
    is_premium_user = models.BooleanField(default=False, null=True)


class Token(rest_framework.authtoken.models.Token):
    """
        create multi token per user - override default rest_framework Token class
        replace model one-to-one relationship with foreign key
        """
    key = models.CharField(_("Key"), max_length=40, db_index=True, unique=True, primary_key=True)
    # Foreign key relationship to user for many-to-one relationship
    user = models.ForeignKey(
        User, related_name='auth_token',
        on_delete=models.CASCADE, verbose_name=_("User")
    )
    userToken = models.ForeignKey(UserToken, on_delete=models.CASCADE, null=True)


class TokenAuthentication(rest_framework.authentication.TokenAuthentication):
    model = Token
