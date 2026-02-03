"""Signals for the Academic domain."""
from django.db.models.signals import pre_save
from django.dispatch import receiver

from domain.academic.models import AcademicYear


@receiver(pre_save, sender=AcademicYear)
def set_academic_year_code(sender, instance, **kwargs):
    """
    Automatically set the code based on start_year and end_year.
    
    This ensures consistency and prevents manual code entry errors.
    """
    if instance.start_year and instance.end_year:
        instance.code = f"{instance.start_year}-{instance.end_year}"
