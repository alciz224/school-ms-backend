"""
Admin interface for school operations.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import School, SchoolYear, SchoolYearCycle, SchoolYearLevel
from .constants import SchoolStatus, SchoolYearStatus


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    """Admin interface for School model."""
    
    list_display = [
        'name',
        'code',
        'school_type',
        'ownership',
        'status_display',
        'locality',
        'capacity',
        'director',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'school_type',
        'ownership',
        'status',
        'is_active',
        'locality__administrative_unit__region',
        'locality__administrative_unit',
        'created_at'
    ]
    
    search_fields = [
        'name',
        'code',
        'locality__name',
        'locality__administrative_unit__name',
        'director__first_name',
        'director__last_name',
        'director__email'
    ]
    
    ordering = ['name']
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
        'deleted_at',
        'deleted_by',
        'geographic_path'
    ]
    
    fieldsets = (
        (_('Informations générales'), {
            'fields': (
                'name',
                'code',
                'school_type',
                'ownership',
                'status'
            )
        }),
        (_('Localisation'), {
            'fields': (
                'locality',
                'geographic_path',
                'address'
            )
        }),
        (_('Contact'), {
            'fields': (
                'phone',
                'email',
                'website'
            ),
            'classes': ['collapse']
        }),
        (_('Opérations'), {
            'fields': (
                'capacity',
                'director',
                'registrar',
                'is_active'
            )
        }),
        (_('Paramètres'), {
            'fields': ('settings',),
            'classes': ['collapse'],
            'description': _('Configuration JSON spécifique à cette école')
        }),
        (_('Audit'), {
            'fields': (
                'created_at',
                'created_by',
                'updated_at',
                'updated_by',
                'deleted_at',
                'deleted_by'
            ),
            'classes': ['collapse']
        })
    )
    
    raw_id_fields = ['locality', 'director', 'registrar']
    
    actions = ['activate_schools', 'suspend_schools', 'make_active']
    
    def status_display(self, obj):
        """Display status with colored badge."""
        colors = {
            SchoolStatus.DRAFT: 'gray',
            SchoolStatus.ACTIVE: 'green',
            SchoolStatus.SUSPENDED: 'orange',
            SchoolStatus.CLOSED: 'red',
        }
        
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = _('État')
    
    def geographic_path(self, obj):
        """Display full geographic path."""
        return obj.geographic_path
    geographic_path.short_description = _('Chemin géographique')
    
    def activate_schools(self, request, queryset):
        """Activate selected schools."""
        activated = 0
        for school in queryset.filter(status=SchoolStatus.DRAFT):
            try:
                school.activate(user=request.user)
                activated += 1
            except Exception:
                continue
        
        self.message_user(
            request,
            _('%(count)d école(s) activée(s).') % {'count': activated}
        )
    activate_schools.short_description = _('Activer les écoles sélectionnées')
    
    def suspend_schools(self, request, queryset):
        """Suspend selected schools."""
        suspended = 0
        for school in queryset.filter(status=SchoolStatus.ACTIVE):
            try:
                school.suspend(user=request.user)
                suspended += 1
            except Exception:
                continue
        
        self.message_user(
            request,
            _('%(count)d école(s) suspendue(s).') % {'count': suspended}
        )
    suspend_schools.short_description = _('Suspendre les écoles sélectionnées')
    
    def make_active(self, request, queryset):
        """Make selected objects active (is_active=True)."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            _('%(count)d école(s) marquée(s) comme active(s).') % {'count': updated}
        )
    make_active.short_description = _('Marquer comme actif')
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'locality',
            'locality__administrative_unit',
            'locality__administrative_unit__region',
            'locality__administrative_unit__region__country',
            'director',
            'registrar',
            'created_by',
            'updated_by'
        )
    
    def save_model(self, request, obj, form, change):
        """Save model with user tracking."""
        obj.save_by(user=request.user)
    
    def has_delete_permission(self, request, obj=None):
        """Only allow soft delete."""
        return True
    
    def delete_model(self, request, obj):
        """Perform soft delete."""
        obj.soft_delete(user=request.user)
    
    def delete_queryset(self, request, queryset):
        """Perform bulk soft delete."""
        for obj in queryset:
            obj.soft_delete(user=request.user)


@admin.register(SchoolYear)
class SchoolYearAdmin(admin.ModelAdmin):
    """Admin interface for SchoolYear model."""
    
    list_display = [
        'name',
        'code',
        'school_name',
        'academic_year_code',
        'status_display',
        'is_current_display',
        'enrollment_period_display',
        'capacity_display',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'is_current',
        'academic_year',
        'school__school_type',
        'school__ownership',
        'is_active',
        'created_at'
    ]
    
    search_fields = [
        'name',
        'code',
        'school__name',
        'school__code',
        'academic_year__code',
        'description'
    ]
    
    ordering = ['-start_date', 'school__name']
    
    readonly_fields = [
        'code',
        'current_enrollment_count',
        'is_enrollment_open_display',
        'available_capacity_display',
        'enrollment_percentage_display',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
        'deleted_at',
        'deleted_by'
    ]
    
    fieldsets = (
        (_('Informations générales'), {
            'fields': (
                'school',
                'academic_year',
                'name',
                'code',
                'status',
                'is_current'
            )
        }),
        (_('Dates'), {
            'fields': (
                'start_date',
                'end_date',
                'enrollment_start_date',
                'enrollment_end_date',
                'is_enrollment_open_display'
            )
        }),
        (_('Capacité et inscriptions'), {
            'fields': (
                'capacity',
                'current_enrollment_count',
                'available_capacity_display',
                'enrollment_percentage_display'
            )
        }),
        (_('Description'), {
            'fields': ('description',),
            'classes': ['collapse']
        }),
        (_('Paramètres'), {
            'fields': ('settings',),
            'classes': ['collapse'],
            'description': _('Configuration JSON spécifique à cette année scolaire')
        }),
        (_('Audit'), {
            'fields': (
                'is_active',
                'created_at',
                'created_by',
                'updated_at',
                'updated_by',
                'deleted_at',
                'deleted_by'
            ),
            'classes': ['collapse']
        })
    )
    
    raw_id_fields = ['school', 'academic_year']
    
    actions = [
        'activate_school_years',
        'complete_school_years',
        'archive_school_years',
        'make_active'
    ]
    
    def school_name(self, obj):
        """Display school name."""
        return obj.school.name
    school_name.short_description = _('École')
    school_name.admin_order_field = 'school__name'
    
    def academic_year_code(self, obj):
        """Display academic year code."""
        return obj.academic_year.code
    academic_year_code.short_description = _('Année académique')
    academic_year_code.admin_order_field = 'academic_year__code'
    
    def status_display(self, obj):
        """Display status with colored badge."""
        colors = {
            SchoolYearStatus.PLANNING: '#6c757d',    # Gray
            SchoolYearStatus.ACTIVE: '#28a745',      # Green
            SchoolYearStatus.COMPLETED: '#007bff',   # Blue
            SchoolYearStatus.ARCHIVED: '#6c757d',    # Gray
        }
        
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 4px; font-size: 11px; font-weight: 500;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = _('Statut')
    status_display.admin_order_field = 'status'
    
    def is_current_display(self, obj):
        """Display current status with icon."""
        if obj.is_current:
            return format_html(
                '<span style="color: #28a745; font-size: 16px;" title="Année actuelle">✓</span>'
            )
        return format_html(
            '<span style="color: #ccc; font-size: 16px;">—</span>'
        )
    is_current_display.short_description = _('Actuelle')
    is_current_display.admin_order_field = 'is_current'
    
    def enrollment_period_display(self, obj):
        """Display enrollment period."""
        if obj.enrollment_start_date and obj.enrollment_end_date:
            is_open = obj.is_enrollment_open()
            color = 'green' if is_open else 'gray'
            status_text = 'Ouvert' if is_open else 'Fermé'
            
            return format_html(
                '<div style="font-size: 11px;">'
                '<div>{} - {}</div>'
                '<div><span style="background-color: {}; color: white; padding: 1px 6px; '
                'border-radius: 3px; font-size: 10px;">{}</span></div>'
                '</div>',
                obj.enrollment_start_date.strftime('%d/%m/%Y'),
                obj.enrollment_end_date.strftime('%d/%m/%Y'),
                color,
                status_text
            )
        return format_html('<span style="color: #999;">Non défini</span>')
    enrollment_period_display.short_description = _('Période d\'inscription')
    
    def capacity_display(self, obj):
        """Display capacity with progress bar."""
        if obj.capacity:
            percentage = (obj.current_enrollment_count / obj.capacity) * 100
            color = '#dc3545' if percentage >= 100 else '#ffc107' if percentage >= 80 else '#28a745'
            
            return format_html(
                '<div style="font-size: 11px;">'
                '<div>{} / {} élèves</div>'
                '<div style="width: 100px; height: 8px; background-color: #e9ecef; '
                'border-radius: 4px; overflow: hidden; margin-top: 2px;">'
                '<div style="width: {}%; height: 100%; background-color: {}; '
                'transition: width 0.3s ease;"></div>'
                '</div>'
                '</div>',
                obj.current_enrollment_count,
                obj.capacity,
                min(percentage, 100),
                color
            )
        return format_html(
            '<span style="font-size: 11px;">{} élèves</span>',
            obj.current_enrollment_count
        )
    capacity_display.short_description = _('Capacité')
    
    def is_enrollment_open_display(self, obj):
        """Display enrollment status."""
        is_open = obj.is_enrollment_open()
        if is_open:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 4px; font-size: 11px;">Ouvert</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 3px 10px; '
            'border-radius: 4px; font-size: 11px;">Fermé</span>'
        )
    is_enrollment_open_display.short_description = _('Inscriptions')
    
    def available_capacity_display(self, obj):
        """Display available capacity."""
        available = obj.available_capacity()
        if available is None:
            return format_html('<span style="color: #999;">Illimitée</span>')
        
        color = '#dc3545' if available == 0 else '#ffc107' if available < 50 else '#28a745'
        return format_html(
            '<span style="color: {}; font-weight: 500;">{} places</span>',
            color,
            available
        )
    available_capacity_display.short_description = _('Places disponibles')
    
    def enrollment_percentage_display(self, obj):
        """Display enrollment percentage."""
        if obj.capacity and obj.capacity > 0:
            percentage = round((obj.current_enrollment_count / obj.capacity) * 100, 1)
            return format_html('{}%', percentage)
        return format_html('<span style="color: #999;">—</span>')
    enrollment_percentage_display.short_description = _('Taux de remplissage')
    
    def activate_school_years(self, request, queryset):
        """Activate selected school years."""
        activated = 0
        errors = []
        
        for school_year in queryset.filter(status=SchoolYearStatus.PLANNING):
            try:
                school_year.activate(user=request.user)
                activated += 1
            except Exception as e:
                errors.append(f"{school_year.name}: {str(e)}")
        
        if activated > 0:
            self.message_user(
                request,
                _('%(count)d année(s) scolaire(s) activée(s).') % {'count': activated}
            )
        
        if errors:
            self.message_user(
                request,
                _('Erreurs: %(errors)s') % {'errors': ', '.join(errors)},
                level='error'
            )
    activate_school_years.short_description = _('Activer les années scolaires sélectionnées')
    
    def complete_school_years(self, request, queryset):
        """Complete selected school years."""
        completed = 0
        errors = []
        
        for school_year in queryset.filter(status=SchoolYearStatus.ACTIVE):
            try:
                school_year.complete(user=request.user)
                completed += 1
            except Exception as e:
                errors.append(f"{school_year.name}: {str(e)}")
        
        if completed > 0:
            self.message_user(
                request,
                _('%(count)d année(s) scolaire(s) terminée(s).') % {'count': completed}
            )
        
        if errors:
            self.message_user(
                request,
                _('Erreurs: %(errors)s') % {'errors': ', '.join(errors)},
                level='error'
            )
    complete_school_years.short_description = _('Terminer les années scolaires sélectionnées')
    
    def archive_school_years(self, request, queryset):
        """Archive selected school years."""
        archived = 0
        errors = []
        
        for school_year in queryset.filter(status=SchoolYearStatus.COMPLETED):
            try:
                school_year.archive(user=request.user)
                archived += 1
            except Exception as e:
                errors.append(f"{school_year.name}: {str(e)}")
        
        if archived > 0:
            self.message_user(
                request,
                _('%(count)d année(s) scolaire(s) archivée(s).') % {'count': archived}
            )
        
        if errors:
            self.message_user(
                request,
                _('Erreurs: %(errors)s') % {'errors': ', '.join(errors)},
                level='error'
            )
    archive_school_years.short_description = _('Archiver les années scolaires sélectionnées')
    
    def make_active(self, request, queryset):
        """Make selected objects active (is_active=True)."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            _('%(count)d année(s) scolaire(s) marquée(s) comme active(s).') % {'count': updated}
        )
    make_active.short_description = _('Marquer comme actif')
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'school',
            'school__locality',
            'academic_year',
            'created_by',
            'updated_by'
        )
    
    def save_model(self, request, obj, form, change):
        """Save model with user tracking."""
        obj.save_by(user=request.user)
    
    def has_delete_permission(self, request, obj=None):
        """Only allow soft delete."""
        return True
    
    def delete_model(self, request, obj):
        """Perform soft delete."""
        can_delete, reason = obj.can_be_deleted()
        if can_delete:
            obj.soft_delete(user=request.user)
        else:
            self.message_user(request, reason, level='error')
    
    def delete_queryset(self, request, queryset):
        """Perform bulk soft delete."""
        for obj in queryset:
            can_delete, reason = obj.can_be_deleted()
            if can_delete:
                obj.soft_delete(user=request.user)


@admin.register(SchoolYearCycle)
class SchoolYearCycleAdmin(admin.ModelAdmin):
    """Admin interface for SchoolYearCycle model."""
    
    list_display = [
        'id',
        'school_year_display',
        'cycle_display',
        'term_type_display',
        'school_name',
        'created_at'
    ]
    
    list_filter = [
        'cycle',
        'term_type',
        'school_year__academic_year',
        'school_year__school__school_type',
        'is_active',
        'created_at'
    ]
    
    search_fields = [
        'school_year__name',
        'school_year__code',
        'school_year__school__name',
        'cycle__name',
        'cycle__code',
        'term_type__name'
    ]
    
    ordering = ['-school_year__start_date', 'cycle__code']
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
        'deleted_at',
        'deleted_by'
    ]
    
    fieldsets = (
        (_('Configuration du cycle'), {
            'fields': (
                'school_year',
                'cycle',
                'term_type'
            )
        }),
        (_('Audit'), {
            'fields': (
                'is_active',
                'created_at',
                'created_by',
                'updated_at',
                'updated_by',
                'deleted_at',
                'deleted_by'
            ),
            'classes': ['collapse']
        })
    )
    
    raw_id_fields = ['school_year', 'cycle', 'term_type']
    
    actions = ['make_active']
    
    def school_year_display(self, obj):
        """Display school year."""
        return format_html(
            '<div style="font-size: 11px;">'
            '<div style="font-weight: 500;">{}</div>'
            '<div style="color: #999;">{}</div>'
            '</div>',
            obj.school_year.name,
            obj.school_year.code
        )
    school_year_display.short_description = _('Année scolaire')
    school_year_display.admin_order_field = 'school_year__name'
    
    def cycle_display(self, obj):
        """Display cycle."""
        return format_html(
            '<span style="background-color: #007bff; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            obj.cycle.name
        )
    cycle_display.short_description = _('Cycle')
    cycle_display.admin_order_field = 'cycle__name'
    
    def term_type_display(self, obj):
        """Display term type."""
        return format_html(
            '<div style="font-size: 11px;">'
            '<div>{}</div>'
            '<div style="color: #999;">{} périodes</div>'
            '</div>',
            obj.term_type.name,
            obj.term_type.period_count
        )
    term_type_display.short_description = _('Type de période')
    term_type_display.admin_order_field = 'term_type__name'
    
    def school_name(self, obj):
        """Display school name."""
        return obj.school_year.school.name
    school_name.short_description = _('École')
    school_name.admin_order_field = 'school_year__school__name'
    
    def make_active(self, request, queryset):
        """Make selected objects active (is_active=True)."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            _('%(count)d cycle(s) marqué(s) comme actif(s).') % {'count': updated}
        )
    make_active.short_description = _('Marquer comme actif')
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'school_year',
            'school_year__school',
            'school_year__academic_year',
            'cycle',
            'term_type',
            'created_by',
            'updated_by'
        )
    
    def save_model(self, request, obj, form, change):
        """Save model with user tracking."""
        if not change:  # Creating new
            obj.created_by = request.user
        obj.updated_by = request.user
        obj.save()
    
    def has_delete_permission(self, request, obj=None):
        """Only allow soft delete."""
        return True
    
    def delete_model(self, request, obj):
        """Perform soft delete."""
        if obj.can_delete():
            obj.is_deleted = True
            obj.deleted_by = request.user
            obj.save()
        else:
            self.message_user(
                request,
                _('Impossible de supprimer ce cycle car il a des niveaux ou évaluations associés.'),
                level='error'
            )
    
    def delete_queryset(self, request, queryset):
        """Perform bulk soft delete."""
        for obj in queryset:
            if obj.can_delete():
                obj.is_deleted = True
                obj.deleted_by = request.user
                obj.save()


@admin.register(SchoolYearLevel)
class SchoolYearLevelAdmin(admin.ModelAdmin):
    """Admin interface for SchoolYearLevel model."""
    
    list_display = [
        'id',
        'school_year_display',
        'cycle_display',
        'level_display',
        'track_display',
        'school_name',
        'created_at'
    ]
    
    list_filter = [
        'school_year_cycle__cycle',
        'level',
        'track',
        'school_year_cycle__school_year__academic_year',
        'is_active',
        'created_at'
    ]
    
    search_fields = [
        'school_year_cycle__school_year__name',
        'school_year_cycle__school_year__code',
        'school_year_cycle__school_year__school__name',
        'level__name',
        'level__code',
        'track__name',
        'track__code'
    ]
    
    ordering = ['-school_year_cycle__school_year__start_date', 'level__order']
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
        'deleted_at',
        'deleted_by'
    ]
    
    fieldsets = (
        (_('Configuration du niveau'), {
            'fields': (
                'school_year_cycle',
                'level',
                'track'
            )
        }),
        (_('Audit'), {
            'fields': (
                'is_active',
                'created_at',
                'created_by',
                'updated_at',
                'updated_by',
                'deleted_at',
                'deleted_by'
            ),
            'classes': ['collapse']
        })
    )
    
    raw_id_fields = ['school_year_cycle', 'level', 'track']
    
    actions = ['make_active']
    
    def school_year_display(self, obj):
        """Display school year."""
        return format_html(
            '<div style="font-size: 11px;">'
            '<div style="font-weight: 500;">{}</div>'
            '<div style="color: #999;">{}</div>'
            '</div>',
            obj.school_year_cycle.school_year.name,
            obj.school_year_cycle.school_year.code
        )
    school_year_display.short_description = _('Année scolaire')
    school_year_display.admin_order_field = 'school_year_cycle__school_year__name'
    
    def cycle_display(self, obj):
        """Display cycle."""
        return format_html(
            '<span style="background-color: #007bff; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            obj.school_year_cycle.cycle.name
        )
    cycle_display.short_description = _('Cycle')
    cycle_display.admin_order_field = 'school_year_cycle__cycle__name'
    
    def level_display(self, obj):
        """Display level."""
        return format_html(
            '<div style="font-size: 11px;">'
            '<div style="font-weight: 500;">{}</div>'
            '<div style="color: #999;">Ordre: {}</div>'
            '</div>',
            obj.level.name,
            obj.level.order
        )
    level_display.short_description = _('Niveau')
    level_display.admin_order_field = 'level__order'
    
    def track_display(self, obj):
        """Display track."""
        if obj.track:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px;">{}</span>',
                obj.track.name
            )
        return format_html(
            '<span style="color: #999; font-style: italic;">Aucune</span>'
        )
    track_display.short_description = _('Filière')
    track_display.admin_order_field = 'track__name'
    
    def school_name(self, obj):
        """Display school name."""
        return obj.school_year_cycle.school_year.school.name
    school_name.short_description = _('École')
    school_name.admin_order_field = 'school_year_cycle__school_year__school__name'
    
    def make_active(self, request, queryset):
        """Make selected objects active (is_active=True)."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            _('%(count)d niveau(x) marqué(s) comme actif(s).') % {'count': updated}
        )
    make_active.short_description = _('Marquer comme actif')
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'school_year_cycle',
            'school_year_cycle__school_year',
            'school_year_cycle__school_year__school',
            'school_year_cycle__school_year__academic_year',
            'school_year_cycle__cycle',
            'school_year_cycle__term_type',
            'level',
            'level__cycle',
            'track',
            'track__cycle',
            'created_by',
            'updated_by'
        )
    
    def save_model(self, request, obj, form, change):
        """Save model with user tracking."""
        if not change:  # Creating new
            obj.created_by = request.user
        obj.updated_by = request.user
        obj.save()
    
    def has_delete_permission(self, request, obj=None):
        """Only allow soft delete."""
        return True
    
    def delete_model(self, request, obj):
        """Perform soft delete."""
        if obj.can_delete():
            obj.is_deleted = True
            obj.deleted_by = request.user
            obj.save()
        else:
            self.message_user(
                request,
                _('Impossible de supprimer ce niveau car il a des classes ou matières associées.'),
                level='error'
            )
    
    def delete_queryset(self, request, queryset):
        """Perform bulk soft delete."""
        for obj in queryset:
            if obj.can_delete():
                obj.is_deleted = True
                obj.deleted_by = request.user
                obj.save()