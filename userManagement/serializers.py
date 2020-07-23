from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class SocialSerializer(serializers.Serializer):
	provider = 'facebook'
	for user in User.objects.all():
		tokens = Token.objects.get_or_create(user=user, trim_whitespace=True)
		token = token.key