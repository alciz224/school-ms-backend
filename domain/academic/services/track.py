"""Track service - basic implementation."""

from domain.academic.models import Track

class TrackService:
    """Service for track operations."""

    @staticmethod
    def create(*, code: str, name: str, cycle, user=None) -> Track:
        track = Track(code=code.strip(), name=name.strip(), cycle=cycle, created_by=user)
        track.save()
        return track

    @staticmethod
    def update(*, track: Track, code: str = None, name: str = None, user=None) -> Track:
        if code: track.code = code.strip()
        if name: track.name = name.strip()
        track.updated_by = user
        track.save()
        return track

    @staticmethod
    def delete(*, track: Track, user=None, hard: bool = False) -> None:
        if hard:
            track.hard_delete()
        else:
            track.deleted_by = user
            track.delete()