"""
Locality serializers.
"""

from rest_framework import serializers

from domain.geography.models import AdministrativeUnit, Locality


class LocalityUnitSerializer(serializers.ModelSerializer):
    """Nested serializer for administrative unit in locality responses."""
    
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = AdministrativeUnit
        fields = ['id', 'code', 'name', 'type', 'type_display']
        read_only_fields = fields


class LocalityListSerializer(serializers.ModelSerializer):
    """Serializer for locality list view."""
    
    administrative_unit = LocalityUnitSerializer(read_only=True)

    class Meta:
        model = Locality
        fields = [
            'id', 'code', 'name', 'administrative_unit',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields


class LocalityDetailSerializer(serializers.ModelSerializer):
    """Serializer for locality detail view."""
    
    administrative_unit = LocalityUnitSerializer(read_only=True)
    full_path = serializers.CharField(read_only=True)

    class Meta:
        model = Locality
        fields = [
            'id', 'code', 'name', 'administrative_unit', 'full_path',
            'created_at', 'updated_at', 'created_by', 'updated_by',
            'is_deleted', 'deleted_at', 'deleted_by'
        ]
        read_only_fields = fields


class LocalityCreateSerializer(serializers.Serializer):
    """Serializer for locality creation."""
    
    administrative_unit_id = serializers.IntegerField(
        help_text='ID of the administrative unit'
    )
    code = serializers.CharField(max_length=20, help_text='Short code (e.g., KASSAPO)')
    name = serializers.CharField(max_length=100, help_text='Full name')

    def validate_administrative_unit_id(self, value):
        """Validate administrative unit exists."""
        if not AdministrativeUnit.objects.filter(id=value, is_deleted=False).exists():
            raise serializers.ValidationError('Administrative unit not found.')
        return value

    def validate(self, attrs):
        """Validate code and name uniqueness within administrative unit."""
        unit_id = attrs.get('administrative_unit_id')
        code = attrs.get('code', '').upper().strip()
        name = attrs.get('name', '').strip()

        if Locality.objects.filter(
            administrative_unit_id=unit_id, code__iexact=code, is_deleted=False
        ).exists():
            raise serializers.ValidationError({
                'code': 'A locality with this code already exists in this administrative unit.'
            })

        if Locality.objects.filter(
            administrative_unit_id=unit_id, name__iexact=name, is_deleted=False
        ).exists():
            raise serializers.ValidationError({
                'name': 'A locality with this name already exists in this administrative unit.'
            })

        return attrs


class LocalityUpdateSerializer(serializers.Serializer):
    """Serializer for locality update."""
    
    administrative_unit_id = serializers.IntegerField(required=False)
    code = serializers.CharField(max_length=20, required=False)
    name = serializers.CharField(max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('locality', None)
        super().__init__(*args, **kwargs)

    def validate_administrative_unit_id(self, value):
        """Validate administrative unit exists."""
        if value is not None:
            if not AdministrativeUnit.objects.filter(id=value, is_deleted=False).exists():
                raise serializers.ValidationError('Administrative unit not found.')
        return value

    def validate(self, attrs):
        """Validate code and name uniqueness within administrative unit."""
        if not self.instance:
            return attrs

        unit_id = attrs.get('administrative_unit_id', self.instance.administrative_unit_id)
        code = attrs.get('code')
        name = attrs.get('name')

        if code:
            code = code.upper().strip()
            if Locality.objects.filter(
                administrative_unit_id=unit_id, code__iexact=code, is_deleted=False
            ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError({
                    'code': 'A locality with this code already exists in this administrative unit.'
                })

        if name:
            name = name.strip()
            if Locality.objects.filter(
                administrative_unit_id=unit_id, name__iexact=name, is_deleted=False
            ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError({
                    'name': 'A locality with this name already exists in this administrative unit.'
                })

        return attrs
