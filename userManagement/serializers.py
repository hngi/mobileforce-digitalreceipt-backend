from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class SocialSerializer(serializers.Serializer):
	provider = 'facebook'
	access_token = serializers.CharField(max_length=4096, required=True, trim_whitespace=True)