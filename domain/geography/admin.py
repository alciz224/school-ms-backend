"""
Geography admin configuration.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from domain.geography.models import (
    Country,
    RegionAdministrative,
    AdministrativeUnit,
    Locality,
)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    """Admin configuration for Country."""
    
    list_display = ['code', 'name', 'regions_count', 'is_deleted', 'created_at']
    list_filter = ['is_deleted', 'created_at']
    search_fields = ['code', 'name']
    ordering = ['name']
    readonly_fields = [
        'created_at', 'updated_at', 'created_by', 'updated_by',
        'is_deleted', 'deleted_at', 'deleted_by'
    ]
    
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'description')
        }),
        (_('Audit'), {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by',
                'is_deleted', 'deleted_at', 'deleted_by'
            ),
            'classes': ('collapse',)
        }),
    )


@admin.register(RegionAdministrative)
class RegionAdministrativeAdmin(admin.ModelAdmin):
    """Admin configuration for RegionAdministrative."""
    
    list_display = [
        'code', 'name', 'country', 'administrative_units_count', 
        'is_deleted', 'created_at'
    ]
    list_filter = ['country', 'is_deleted', 'created_at']
    search_fields = ['code', 'name', 'country__name']
    ordering = ['country__name', 'name']
    readonly_fields = [
        'created_at', 'updated_at', 'created_by', 'updated_by',
        'is_deleted', 'deleted_at', 'deleted_by'
    ]
    autocomplete_fields = ['country']
    
    fieldsets = (
        (None, {
            'fields': ('country', 'code', 'name', 'description')
        }),
        (_('Audit'), {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by',
                'is_deleted', 'deleted_at', 'deleted_by'
            ),
            'classes': ('collapse',)
        }),
    )


@admin.register(AdministrativeUnit)
class AdministrativeUnitAdmin(admin.ModelAdmin):
    """Admin configuration for AdministrativeUnit."""
    
    list_display = [
        'code', 'name', 'type', 'region', 'parent',
        'localities_count', 'is_deleted', 'created_at'
    ]
    list_filter = ['type', 'region__country', 'region', 'is_deleted', 'created_at']
    search_fields = ['code', 'name', 'region__name', 'parent__name']
    ordering = ['region__name', 'type', 'name']
    readonly_fields = [
        'created_at', 'updated_at', 'created_by', 'updated_by',
        'is_deleted', 'deleted_at', 'deleted_by'
    ]
    autocomplete_fields = ['region', 'parent']
    
    fieldsets = (
        (None, {
            'fields': ('region', 'parent', 'code', 'name', 'type')
        }),
        (_('Audit'), {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by',
                'is_deleted', 'deleted_at', 'deleted_by'
            ),
            'classes': ('collapse',)
        }),
    )


@admin.register(Locality)
class LocalityAdmin(admin.ModelAdmin):
    """Admin configuration for Locality."""
    
    list_display = [
        'code', 'name', 'administrative_unit', 'is_deleted', 'created_at'
    ]
    list_filter = [
        'administrative_unit__region__country',
        'administrative_unit__region',
        'administrative_unit',
        'is_deleted',
        'created_at'
    ]
    search_fields = ['code', 'name', 'administrative_unit__name']
    ordering = ['administrative_unit__name', 'name']
    readonly_fields = [
        'created_at', 'updated_at', 'created_by', 'updated_by',
        'is_deleted', 'deleted_at', 'deleted_by'
    ]
    autocomplete_fields = ['administrative_unit']
    
    fieldsets = (
        (None, {
            'fields': ('administrative_unit', 'code', 'name')
        }),
        (_('Audit'), {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by',
                'is_deleted', 'deleted_at', 'deleted_by'
            ),
            'classes': ('collapse',)
        }),
    )
