from rest_framework import serializers

from domain.finance.models import FeeType


class FeeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeType
        fields = [
            "id",
            "name",
            "category",
            "description",
            "default_amount",
            "payment_frequency",
            "is_active",
        ]
