from rest_framework import serializers

class StatusResponseSerializer(serializers.Serializer):
    """Serializer for status change responses."""
    id = serializers.IntegerField()
    status = serializers.CharField()
