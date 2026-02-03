"""
Country serializers.
"""

from rest_framework import serializers

from domain.geography.models import Country


class CountryListSerializer(serializers.ModelSerializer):
    """Serializer for country list view."""

    regions_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Country
        fields = ["id", "code", "name", "regions_count", "created_at", "updated_at"]
        read_only_fields = fields


class CountryDetailSerializer(serializers.ModelSerializer):
    """Serializer for country detail view."""

    regions_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Country
        fields = [
            "id",
            "code",
            "name",
            "description",
            "regions_count",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_deleted",
            "deleted_at",
            "deleted_by",
        ]
        read_only_fields = fields


class CountryCreateSerializer(serializers.Serializer):
    """Serializer for country creation."""

    code = serializers.CharField(
        max_length=10, help_text="ISO or short code (e.g., GN)"
    )
    name = serializers.CharField(max_length=100, help_text="Full country name")
    description = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    def validate_code(self, value):
        """Validate code uniqueness."""
        code = value.upper().strip()
        if Country.objects.filter(code__iexact=code).exists():
            raise serializers.ValidationError(
                "A country with this code already exists."
            )
        return code

    def validate_name(self, value):
        """Validate name uniqueness."""
        name = value.strip()
        if Country.objects.filter(name__iexact=name).exists():
            raise serializers.ValidationError(
                "A country with this name already exists."
            )
        return name


class CountryUpdateSerializer(serializers.Serializer):
    """Serializer for country update."""

    code = serializers.CharField(max_length=10, required=False)
    name = serializers.CharField(max_length=100, required=False)
    description = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop("country", None)
        super().__init__(*args, **kwargs)

    def validate_code(self, value):
        """Validate code uniqueness."""
        if value is None:
            return value
        code = value.upper().strip()
        queryset = Country.objects.filter(code__iexact=code)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        if queryset.exists():
            raise serializers.ValidationError(
                "A country with this code already exists."
            )
        return code

    def validate_name(self, value):
        """Validate name uniqueness."""
        if value is None:
            return value
        name = value.strip()
        queryset = Country.objects.filter(name__iexact=name)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        if queryset.exists():
            raise serializers.ValidationError(
                "A country with this name already exists."
            )
        return name
