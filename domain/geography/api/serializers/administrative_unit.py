"""
AdministrativeUnit serializers.
"""

from rest_framework import serializers

from domain.geography.models import RegionAdministrative, AdministrativeUnit
from domain.geography.constants import AdministrativeUnitType


class UnitRegionSerializer(serializers.ModelSerializer):
    """Nested serializer for region in unit responses."""
    
    class Meta:
        model = RegionAdministrative
        fields = ['id', 'code', 'name']
        read_only_fields = fields


class UnitParentSerializer(serializers.ModelSerializer):
    """Nested serializer for parent unit in responses."""
    
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = AdministrativeUnit
        fields = ['id', 'code', 'name', 'type', 'type_display']
        read_only_fields = fields


class AdministrativeUnitListSerializer(serializers.ModelSerializer):
    """Serializer for administrative unit list view."""
    
    region = UnitRegionSerializer(read_only=True)
    parent = UnitParentSerializer(read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    localities_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = AdministrativeUnit
        fields = [
            'id', 'code', 'name', 'type', 'type_display',
            'region', 'parent', 'localities_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields


class AdministrativeUnitDetailSerializer(serializers.ModelSerializer):
    """Serializer for administrative unit detail view."""
    
    region = UnitRegionSerializer(read_only=True)
    parent = UnitParentSerializer(read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    localities_count = serializers.IntegerField(read_only=True)
    children_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = AdministrativeUnit
        fields = [
            'id', 'code', 'name', 'type', 'type_display',
            'region', 'parent', 'localities_count', 'children_count',
            'created_at', 'updated_at', 'created_by', 'updated_by',
            'is_deleted', 'deleted_at', 'deleted_by'
        ]
        read_only_fields = fields


class AdministrativeUnitCreateSerializer(serializers.Serializer):
    """Serializer for administrative unit creation."""
    
    region_id = serializers.IntegerField(help_text='ID of the region')
    parent_id = serializers.IntegerField(
        required=False, 
        allow_null=True,
        help_text='ID of the parent unit (required for subprefectures)'
    )
    code = serializers.CharField(max_length=20, help_text='Short code (e.g., KAMSAR)')
    name = serializers.CharField(max_length=100, help_text='Full name')
    type = serializers.ChoiceField(
        choices=AdministrativeUnitType.choices,
        help_text='Type of administrative unit'
    )

    def validate_region_id(self, value):
        """Validate region exists."""
        if not RegionAdministrative.objects.filter(id=value, is_deleted=False).exists():
            raise serializers.ValidationError('Region not found.')
        return value

    def validate_parent_id(self, value):
        """Validate parent exists if provided."""
        if value is not None:
            if not AdministrativeUnit.objects.filter(id=value, is_deleted=False).exists():
                raise serializers.ValidationError('Parent unit not found.')
        return value

    def validate(self, attrs):
        """Validate hierarchy rules and uniqueness."""
        region_id = attrs.get('region_id')
        parent_id = attrs.get('parent_id')
        code = attrs.get('code', '').upper().strip()
        name = attrs.get('name', '').strip()
        unit_type = attrs.get('type')

        # Validate hierarchy rules
        if unit_type == AdministrativeUnitType.SUBPREFECTURE:
            if not parent_id:
                raise serializers.ValidationError({
                    'parent_id': 'A subprefecture must have a parent prefecture.'
                })
            parent = AdministrativeUnit.objects.filter(id=parent_id).first()
            if parent and parent.type != AdministrativeUnitType.PREFECTURE:
                raise serializers.ValidationError({
                    'parent_id': 'A subprefecture parent must be a prefecture.'
                })
            if parent and parent.region_id != region_id:
                raise serializers.ValidationError({
                    'parent_id': 'Parent must belong to the same region.'
                })
        elif unit_type in (AdministrativeUnitType.PREFECTURE, AdministrativeUnitType.COMMUNE):
            if parent_id:
                raise serializers.ValidationError({
                    'parent_id': f'A {unit_type.lower()} cannot have a parent.'
                })

        # Validate uniqueness
        if AdministrativeUnit.objects.filter(
            region_id=region_id, code__iexact=code, is_deleted=False
        ).exists():
            raise serializers.ValidationError({
                'code': 'A unit with this code already exists in this region.'
            })

        if AdministrativeUnit.objects.filter(
            region_id=region_id, name__iexact=name, is_deleted=False
        ).exists():
            raise serializers.ValidationError({
                'name': 'A unit with this name already exists in this region.'
            })

        return attrs


class AdministrativeUnitUpdateSerializer(serializers.Serializer):
    """Serializer for administrative unit update."""
    
    parent_id = serializers.IntegerField(required=False, allow_null=True)
    code = serializers.CharField(max_length=20, required=False)
    name = serializers.CharField(max_length=100, required=False)
    type = serializers.ChoiceField(choices=AdministrativeUnitType.choices, required=False)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('unit', None)
        super().__init__(*args, **kwargs)

    def validate_parent_id(self, value):
        """Validate parent exists if provided."""
        if value is not None:
            if not AdministrativeUnit.objects.filter(id=value, is_deleted=False).exists():
                raise serializers.ValidationError('Parent unit not found.')
        return value

    def validate(self, attrs):
        """Validate hierarchy rules and uniqueness."""
        if not self.instance:
            return attrs

        region_id = self.instance.region_id
        parent_id = attrs.get('parent_id', self.instance.parent_id)
        code = attrs.get('code')
        name = attrs.get('name')
        unit_type = attrs.get('type', self.instance.type)

        # Validate hierarchy rules
        if unit_type == AdministrativeUnitType.SUBPREFECTURE:
            if not parent_id:
                raise serializers.ValidationError({
                    'parent_id': 'A subprefecture must have a parent prefecture.'
                })
            parent = AdministrativeUnit.objects.filter(id=parent_id).first()
            if parent and parent.type != AdministrativeUnitType.PREFECTURE:
                raise serializers.ValidationError({
                    'parent_id': 'A subprefecture parent must be a prefecture.'
                })
            if parent and parent.region_id != region_id:
                raise serializers.ValidationError({
                    'parent_id': 'Parent must belong to the same region.'
                })
        elif unit_type in (AdministrativeUnitType.PREFECTURE, AdministrativeUnitType.COMMUNE):
            if parent_id:
                raise serializers.ValidationError({
                    'parent_id': f'A {unit_type.lower()} cannot have a parent.'
                })

        # Validate uniqueness
        if code:
            code = code.upper().strip()
            if AdministrativeUnit.objects.filter(
                region_id=region_id, code__iexact=code, is_deleted=False
            ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError({
                    'code': 'A unit with this code already exists in this region.'
                })

        if name:
            name = name.strip()
            if AdministrativeUnit.objects.filter(
                region_id=region_id, name__iexact=name, is_deleted=False
            ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError({
                    'name': 'A unit with this name already exists in this region.'
                })

        return attrs
