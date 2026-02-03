"""Validators for the Academic domain."""
from django.core.exceptions import ValidationError


def validate_academic_year_sequence(start_year, end_year):
    """
    Validate that end_year is exactly start_year + 1.
    
    Args:
        start_year: The starting year
        end_year: The ending year
        
    Raises:
        ValidationError: If the sequence is invalid
    """
    if end_year != start_year + 1:
        raise ValidationError(
            f"End year must be {start_year + 1}, got {end_year}"
        )


def validate_term_order(order, term_type):
    """
    Validate that term order is within valid range for term type.
    
    Args:
        order: The order value to validate
        term_type: The TermType instance
        
    Raises:
        ValidationError: If order is invalid
    """
    if order <= 0:
        raise ValidationError("Order must be greater than 0")
    
    if order > term_type.period_count:
        raise ValidationError(
            f"Order cannot exceed {term_type.period_count} "
            f"for term type '{term_type}'"
        )


def validate_track_for_cycle(track, cycle):
    """
    Validate that a track is appropriate for a cycle.
    
    Args:
        track: The Track instance (can be None)
        cycle: The Cycle instance
        
    Raises:
        ValidationError: If track is invalid for the cycle
    """
    if cycle.has_track and not track:
        raise ValidationError(
            f"Track is required for cycle '{cycle}'"
        )
    
    if not cycle.has_track and track:
        raise ValidationError(
            f"Cycle '{cycle}' does not support tracks"
        )
    
    if track and track.cycle_id != cycle.id:
        raise ValidationError(
            "Track must belong to the same cycle"
        )


def validate_positive_period_count(value):
    """
    Validate that period count is positive.
    
    Args:
        value: The period count to validate
        
    Raises:
        ValidationError: If value is not positive
    """
    if value <= 0:
        raise ValidationError("Period count must be greater than 0")
