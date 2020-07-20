from rest_framework import serializers

from .models import Promotions


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotions
        fieids = "__all__"
