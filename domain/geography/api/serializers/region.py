"""
RegionAdministrative serializers.
"""

from rest_framework import serializers

from domain.geography.models import Country, RegionAdministrative


class RegionCountrySerializer(serializers.ModelSerializer):
    """Nested serializer for country in region responses."""
    
    class Meta:
        model = Country
        fields = ['id', 'code', 'name']
        read_only_fields = fields


class RegionListSerializer(serializers.ModelSerializer):
    """Serializer for region list view."""
    
    country = RegionCountrySerializer(read_only=True)
    administrative_units_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = RegionAdministrative
        fields = [
            'id', 'code', 'name', 'country', 
            'administrative_units_count', 'created_at', 'updated_at'
        ]
        read_only_fields = fields


class RegionDetailSerializer(serializers.ModelSerializer):
    """Serializer for region detail view."""
    
    country = RegionCountrySerializer(read_only=True)
    administrative_units_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = RegionAdministrative
        fields = [
            'id', 'code', 'name', 'description', 'country',
            'administrative_units_count',
            'created_at', 'updated_at', 'created_by', 'updated_by',
            'is_deleted', 'deleted_at', 'deleted_by'
        ]
        read_only_fields = fields


class RegionCreateSerializer(serializers.Serializer):
    """Serializer for region creation."""
    
    country_id = serializers.IntegerField(help_text='ID of the country')
    code = serializers.CharField(max_length=20, help_text='Short code (e.g., BOKE)')
    name = serializers.CharField(max_length=100, help_text='Full region name')
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_country_id(self, value):
        """Validate country exists."""
        if not Country.objects.filter(id=value, is_deleted=False).exists():
            raise serializers.ValidationError('Country not found.')
        return value

    def validate(self, attrs):
        """Validate code and name uniqueness within country."""
        country_id = attrs.get('country_id')
        code = attrs.get('code', '').upper().strip()
        name = attrs.get('name', '').strip()

        if RegionAdministrative.objects.filter(
            country_id=country_id, code__iexact=code, is_deleted=False
        ).exists():
            raise serializers.ValidationError({
                'code': 'A region with this code already exists in this country.'
            })

        if RegionAdministrative.objects.filter(
            country_id=country_id, name__iexact=name, is_deleted=False
        ).exists():
            raise serializers.ValidationError({
                'name': 'A region with this name already exists in this country.'
            })

        return attrs


class RegionUpdateSerializer(serializers.Serializer):
    """Serializer for region update."""
    
    code = serializers.CharField(max_length=20, required=False)
    name = serializers.CharField(max_length=100, required=False)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('region', None)
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        """Validate code and name uniqueness within country."""
        if not self.instance:
            return attrs

        code = attrs.get('code')
        name = attrs.get('name')

        if code:
            code = code.upper().strip()
            if RegionAdministrative.objects.filter(
                country_id=self.instance.country_id,
                code__iexact=code,
                is_deleted=False
            ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError({
                    'code': 'A region with this code already exists in this country.'
                })

        if name:
            name = name.strip()
            if RegionAdministrative.objects.filter(
                country_id=self.instance.country_id,
                name__iexact=name,
                is_deleted=False
            ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError({
                    'name': 'A region with this name already exists in this country.'
                })

        return attrs
