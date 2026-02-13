"""
SchoolYear serializers.
"""

from rest_framework import serializers

from domain.school_operations.models import School, SchoolYear
from domain.school_operations.constants import SchoolYearStatus
from domain.academic.models import AcademicYear


class SchoolYearListSerializer(serializers.ModelSerializer):
    """Serializer for listing school years."""
    
    school_name = serializers.CharField(source='school.name', read_only=True)
    school_code = serializers.CharField(source='school.code', read_only=True)
    academic_year_code = serializers.CharField(source='academic_year.code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Computed fields
    is_enrollment_open = serializers.SerializerMethodField()
    available_capacity = serializers.SerializerMethodField()
    enrollment_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = SchoolYear
        fields = [
            'id',
            'school',
            'school_name',
            'school_code',
            'academic_year',
            'academic_year_code',
            'name',
            'code',
            'start_date',
            'end_date',
            'enrollment_start_date',
            'enrollment_end_date',
            'capacity',
            'current_enrollment_count',
            'status',
            'status_display',
            'is_current',
            'is_enrollment_open',
            'available_capacity',
            'enrollment_percentage',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'code',
            'current_enrollment_count',
            'created_at',
            'updated_at',
        ]
    
    def get_is_enrollment_open(self, obj) -> bool:
        """Check if enrollment is open."""
        return obj.is_enrollment_open()
    
    def get_available_capacity(self, obj) -> int:
        """Get available capacity."""
        return obj.available_capacity()
    
    def get_enrollment_percentage(self, obj) -> float | None:
        """Calculate enrollment percentage."""
        if obj.capacity and obj.capacity > 0:
            return round((obj.current_enrollment_count / obj.capacity) * 100, 2)
        return None


class SchoolYearDetailSerializer(serializers.ModelSerializer):
    """Serializer for school year details."""
    
    school_name = serializers.CharField(source='school.name', read_only=True)
    school_code = serializers.CharField(source='school.code', read_only=True)
    school_type = serializers.CharField(source='school.school_type', read_only=True)
    academic_year_code = serializers.CharField(source='academic_year.code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Computed fields
    is_enrollment_open = serializers.SerializerMethodField()
    available_capacity = serializers.SerializerMethodField()
    enrollment_percentage = serializers.SerializerMethodField()
    can_be_deleted = serializers.SerializerMethodField()
    
    # Audit fields
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    updated_by_email = serializers.EmailField(source='updated_by.email', read_only=True)
    
    class Meta:
        model = SchoolYear
        fields = [
            'id',
            'school',
            'school_name',
            'school_code',
            'school_type',
            'academic_year',
            'academic_year_code',
            'name',
            'code',
            'start_date',
            'end_date',
            'enrollment_start_date',
            'enrollment_end_date',
            'capacity',
            'current_enrollment_count',
            'status',
            'status_display',
            'is_current',
            'settings',
            'description',
            'is_enrollment_open',
            'available_capacity',
            'enrollment_percentage',
            'can_be_deleted',
            'is_active',
            'created_at',
            'updated_at',
            'created_by_email',
            'updated_by_email',
        ]
        read_only_fields = [
            'id',
            'code',
            'current_enrollment_count',
            'is_active',
            'created_at',
            'updated_at',
        ]
    
    def get_is_enrollment_open(self, obj) -> bool:
        """Check if enrollment is open."""
        return obj.is_enrollment_open()
    
    def get_available_capacity(self, obj) -> int:
        """Get available capacity."""
        return obj.available_capacity()
    
    def get_enrollment_percentage(self, obj) -> float | None:
        """Calculate enrollment percentage."""
        if obj.capacity and obj.capacity > 0:
            return round((obj.current_enrollment_count / obj.capacity) * 100, 2)
        return None
    
    def get_can_be_deleted(self, obj) -> dict:
        """Check if can be deleted."""
        can_delete, reason = obj.can_be_deleted()
        return {
            'allowed': can_delete,
            'reason': reason if not can_delete else ''
        }


class SchoolYearCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating school years."""
    
    use_guinea_defaults = serializers.BooleanField(
        default=True,
        write_only=True,
        help_text="Use Guinea's default academic calendar (October to June)"
    )
    
    class Meta:
        model = SchoolYear
        fields = [
            'school',
            'academic_year',
            'name',
            'start_date',
            'end_date',
            'enrollment_start_date',
            'enrollment_end_date',
            'capacity',
            'description',
            'settings',
            'use_guinea_defaults',
        ]
    
    def validate(self, attrs):
        """Validate school year data."""
        use_guinea_defaults = attrs.pop('use_guinea_defaults', True)
        
        # If using Guinea defaults, dates might not be required
        if use_guinea_defaults:
            # Will be set by service
            attrs['start_date'] = attrs.get('start_date')
            attrs['end_date'] = attrs.get('end_date')
        else:
            # Require explicit dates
            if not attrs.get('start_date'):
                raise serializers.ValidationError({
                    'start_date': 'Required when not using Guinea defaults'
                })
            if not attrs.get('end_date'):
                raise serializers.ValidationError({
                    'end_date': 'Required when not using Guinea defaults'
                })
        
        # Store for later use in create
        attrs['_use_guinea_defaults'] = use_guinea_defaults
        
        return attrs
    
    def create(self, validated_data):
        """Create school year using service layer."""
        from domain.school_operations.services.school_year import SchoolYearService
        
        use_guinea_defaults = validated_data.pop('_use_guinea_defaults', True)
        user = self.context.get('request').user if self.context.get('request') else None
        
        if use_guinea_defaults:
            return SchoolYearService.create_school_year_for_guinea(
                school=validated_data['school'],
                academic_year=validated_data['academic_year'],
                capacity=validated_data.get('capacity'),
                custom_settings=validated_data.get('settings'),
                user=user
            )
        else:
            return SchoolYearService.create_school_year(
                school=validated_data['school'],
                academic_year=validated_data['academic_year'],
                start_date=validated_data['start_date'],
                end_date=validated_data['end_date'],
                enrollment_start_date=validated_data.get('enrollment_start_date'),
                enrollment_end_date=validated_data.get('enrollment_end_date'),
                capacity=validated_data.get('capacity'),
                description=validated_data.get('description', ''),
                settings=validated_data.get('settings'),
                user=user
            )


class SchoolYearUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating school years."""
    
    class Meta:
        model = SchoolYear
        fields = [
            'name',
            'start_date',
            'end_date',
            'enrollment_start_date',
            'enrollment_end_date',
            'capacity',
            'description',
            'settings',
        ]
    
    def update(self, instance, validated_data):
        """Update school year using service layer."""
        from domain.school_operations.services.school_year import SchoolYearService
        
        user = self.context.get('request').user if self.context.get('request') else None
        
        return SchoolYearService.update_school_year(
            school_year=instance,
            start_date=validated_data.get('start_date'),
            end_date=validated_data.get('end_date'),
            enrollment_start_date=validated_data.get('enrollment_start_date'),
            enrollment_end_date=validated_data.get('enrollment_end_date'),
            capacity=validated_data.get('capacity'),
            description=validated_data.get('description'),
            settings=validated_data.get('settings'),
            user=user
        )


class SchoolYearStatusSerializer(serializers.Serializer):
    """Serializer for status transitions."""
    
    action = serializers.ChoiceField(
        choices=['activate', 'complete', 'archive'],
        help_text="Action to perform"
    )


class SchoolYearHolidaySerializer(serializers.Serializer):
    """Serializer for adding holidays."""
    
    name = serializers.CharField(max_length=200)
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False, allow_null=True)


class SchoolYearSettingSerializer(serializers.Serializer):
    """Serializer for updating settings."""
    
    key = serializers.CharField(
        max_length=100,
        help_text="Setting key in dot notation (e.g., 'assessment.passing_grade')"
    )
    value = serializers.JSONField(
        help_text="Setting value"
    )


class SchoolYearStatisticsSerializer(serializers.Serializer):
    """Serializer for school year statistics."""
    
    total_capacity = serializers.IntegerField()
    current_enrollment = serializers.IntegerField()
    available_capacity = serializers.IntegerField(allow_null=True)
    enrollment_percentage = serializers.FloatField()
    is_full = serializers.BooleanField()
    has_capacity = serializers.BooleanField()
    is_enrollment_open = serializers.BooleanField()
