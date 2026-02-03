"""Management command to seed academic reference data."""
from django.core.management.base import BaseCommand
from django.db import transaction

from domain.academic.models import (
    AcademicYear,
    AssessmentType,
    Cycle,
    Level,
    Subject,
    Term,
    TermType,
    Track,
)


class Command(BaseCommand):
    """Seed academic reference data."""

    help = "Seed academic reference data (cycles, subjects, term types, etc.)"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before seeding",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        if options["clear"]:
            self.stdout.write(self.style.WARNING("Clearing existing data..."))
            self.clear_data()

        self.stdout.write(self.style.SUCCESS("Starting academic data seeding..."))

        with transaction.atomic():
            self.seed_cycles()
            self.seed_tracks()
            self.seed_levels()
            self.seed_subjects()
            self.seed_assessment_types()
            self.seed_term_types()
            self.seed_terms()
            self.seed_academic_years()

        self.stdout.write(self.style.SUCCESS("Academic data seeding completed!"))

    def clear_data(self):
        """Clear existing academic data."""
        Term.objects.all().delete()
        TermType.objects.all().delete()
        Level.objects.all().delete()
        Track.objects.all().delete()
        Subject.objects.all().delete()
        AssessmentType.objects.all().delete()
        Cycle.objects.all().delete()
        AcademicYear.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Existing data cleared"))

    def seed_cycles(self):
        """Seed educational cycles."""
        cycles_data = [
            {"code": "MAT", "name": "Maternelle", "has_track": False},
            {"code": "PRI", "name": "Primaire", "has_track": False},
            {"code": "COL", "name": "Collège", "has_track": False},
            {"code": "LYC", "name": "Lycée", "has_track": True},
        ]

        for data in cycles_data:
            cycle, created = Cycle.objects.get_or_create(
                code=data["code"],
                defaults=data,
            )
            if created:
                self.stdout.write(f"  ✓ Created cycle: {cycle}")

    def seed_tracks(self):
        """Seed tracks/specializations for Lycée."""
        lycee = Cycle.objects.get(code="LYC")

        tracks_data = [
            {"code": "SM", "name": "Sciences Mathématiques"},
            {"code": "SE", "name": "Sciences Expérimentales"},
            {"code": "SS", "name": "Sciences Sociales"},
            {"code": "L", "name": "Lettres"},
        ]

        for data in tracks_data:
            track, created = Track.objects.get_or_create(
                cycle=lycee,
                code=data["code"],
                defaults={"name": data["name"]},
            )
            if created:
                self.stdout.write(f"  ✓ Created track: {track}")

    def seed_levels(self):
        """Seed educational levels."""
        # Maternelle levels
        maternelle = Cycle.objects.get(code="MAT")
        mat_levels = [
            {"code": "PS", "name": "Petite Section", "order": 1},
            {"code": "MS", "name": "Moyenne Section", "order": 2},
            {"code": "GS", "name": "Grande Section", "order": 3},
        ]
        for data in mat_levels:
            level, created = Level.objects.get_or_create(
                cycle=maternelle,
                code=data["code"],
                defaults={"name": data["name"], "order": data["order"]},
            )
            if created:
                self.stdout.write(f"  ✓ Created level: {level}")

        # Primaire levels
        primaire = Cycle.objects.get(code="PRI")
        pri_levels = [
            {"code": "CP", "name": "Cours Préparatoire", "order": 1},
            {"code": "CE1", "name": "Cours Élémentaire 1", "order": 2},
            {"code": "CE2", "name": "Cours Élémentaire 2", "order": 3},
            {"code": "CM1", "name": "Cours Moyen 1", "order": 4},
            {"code": "CM2", "name": "Cours Moyen 2", "order": 5},
        ]
        for data in pri_levels:
            level, created = Level.objects.get_or_create(
                cycle=primaire,
                code=data["code"],
                defaults={"name": data["name"], "order": data["order"]},
            )
            if created:
                self.stdout.write(f"  ✓ Created level: {level}")

        # Collège levels
        college = Cycle.objects.get(code="COL")
        col_levels = [
            {"code": "6EME", "name": "6ème", "order": 1},
            {"code": "5EME", "name": "5ème", "order": 2},
            {"code": "4EME", "name": "4ème", "order": 3},
            {"code": "3EME", "name": "3ème", "order": 4},
        ]
        for data in col_levels:
            level, created = Level.objects.get_or_create(
                cycle=college,
                code=data["code"],
                defaults={"name": data["name"], "order": data["order"]},
            )
            if created:
                self.stdout.write(f"  ✓ Created level: {level}")

        # Lycée levels (with tracks)
        lycee = Cycle.objects.get(code="LYC")
        tracks = Track.objects.filter(cycle=lycee)

        # Seconde doesn't need tracks (it's a general level before specialization)
        # So we create it in the Collège cycle instead, or skip tracks for this level
        # For now, we'll just create track-based levels for Lycée
        
        lyc_levels = [
            {"code": "1ERE", "name": "Première", "order": 1},
            {"code": "TER", "name": "Terminale", "order": 2},
        ]

        for data in lyc_levels:
            # All Lycée levels need tracks
            for track in tracks:
                code = f"{data['code']}_{track.code}"
                name = f"{data['name']} {track.code}"
                level, created = Level.objects.get_or_create(
                    cycle=lycee,
                    code=code,
                    track=track,
                    defaults={"name": name, "order": data["order"]},
                )
                if created:
                    self.stdout.write(f"  ✓ Created level: {level}")

    def seed_subjects(self):
        """Seed academic subjects."""
        subjects_data = [
            {"code": "MATH", "name": "Mathématiques"},
            {"code": "PHYS", "name": "Physique"},
            {"code": "CHIM", "name": "Chimie"},
            {"code": "BIO", "name": "Biologie"},
            {"code": "FRAN", "name": "Français"},
            {"code": "ANG", "name": "Anglais"},
            {"code": "HIST", "name": "Histoire"},
            {"code": "GEO", "name": "Géographie"},
            {"code": "PHILO", "name": "Philosophie"},
            {"code": "SVT", "name": "Sciences de la Vie et de la Terre"},
            {"code": "EPS", "name": "Éducation Physique et Sportive"},
            {"code": "ART", "name": "Arts Plastiques"},
            {"code": "MUS", "name": "Musique"},
            {"code": "INFO", "name": "Informatique"},
        ]

        for data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                code=data["code"],
                defaults={"name": data["name"]},
            )
            if created:
                self.stdout.write(f"  ✓ Created subject: {subject}")

    def seed_assessment_types(self):
        """Seed assessment types."""
        assessment_types_data = [
            {
                "code": "COMPO",
                "name": "Composition",
                "description": "Évaluation formelle officielle",
            },
            {
                "code": "COURS",
                "name": "Note de cours",
                "description": "Notes de travaux en classe",
            },
            {
                "code": "DEVOIR",
                "name": "Devoir",
                "description": "Devoirs à domicile",
            },
            {
                "code": "PART",
                "name": "Participation",
                "description": "Note de participation",
            },
            {
                "code": "ORAL",
                "name": "Oral",
                "description": "Présentation orale",
            },
            {
                "code": "TP",
                "name": "Travaux Pratiques",
                "description": "Évaluation de travaux pratiques",
            },
        ]

        for data in assessment_types_data:
            assessment_type, created = AssessmentType.objects.get_or_create(
                code=data["code"],
                defaults={
                    "name": data["name"],
                    "description": data.get("description", ""),
                },
            )
            if created:
                self.stdout.write(f"  ✓ Created assessment type: {assessment_type}")

    def seed_term_types(self):
        """Seed term types."""
        term_types_data = [
            {"code": "TRIMESTER", "name": "Trimestre", "period_count": 3},
            {"code": "SEMESTER", "name": "Semestre", "period_count": 2},
            {"code": "QUARTER", "name": "Quadrimestre", "period_count": 4},
        ]

        for data in term_types_data:
            term_type, created = TermType.objects.get_or_create(
                code=data["code"],
                defaults={
                    "name": data["name"],
                    "period_count": data["period_count"],
                },
            )
            if created:
                self.stdout.write(f"  ✓ Created term type: {term_type}")

    def seed_terms(self):
        """Seed terms for each term type."""
        # Trimester terms
        trimester = TermType.objects.get(code="TRIMESTER")
        trimester_terms = [
            {"code": "T1", "name": "Trimestre 1", "order": 1},
            {"code": "T2", "name": "Trimestre 2", "order": 2},
            {"code": "T3", "name": "Trimestre 3", "order": 3},
        ]
        for data in trimester_terms:
            term, created = Term.objects.get_or_create(
                term_type=trimester,
                code=data["code"],
                defaults={"name": data["name"], "order": data["order"]},
            )
            if created:
                self.stdout.write(f"  ✓ Created term: {term}")

        # Semester terms
        semester = TermType.objects.get(code="SEMESTER")
        semester_terms = [
            {"code": "S1", "name": "Semestre 1", "order": 1},
            {"code": "S2", "name": "Semestre 2", "order": 2},
        ]
        for data in semester_terms:
            term, created = Term.objects.get_or_create(
                term_type=semester,
                code=data["code"],
                defaults={"name": data["name"], "order": data["order"]},
            )
            if created:
                self.stdout.write(f"  ✓ Created term: {term}")

        # Quarter terms
        quarter = TermType.objects.get(code="QUARTER")
        quarter_terms = [
            {"code": "Q1", "name": "Quadrimestre 1", "order": 1},
            {"code": "Q2", "name": "Quadrimestre 2", "order": 2},
            {"code": "Q3", "name": "Quadrimestre 3", "order": 3},
            {"code": "Q4", "name": "Quadrimestre 4", "order": 4},
        ]
        for data in quarter_terms:
            term, created = Term.objects.get_or_create(
                term_type=quarter,
                code=data["code"],
                defaults={"name": data["name"], "order": data["order"]},
            )
            if created:
                self.stdout.write(f"  ✓ Created term: {term}")

    def seed_academic_years(self):
        """Seed sample academic years."""
        import datetime

        current_year = datetime.datetime.now().year

        years_data = [
            {
                "start_year": current_year - 1,
                "end_year": current_year,
                "status": "ARCHIVED",
                "is_current": False,
            },
            {
                "start_year": current_year,
                "end_year": current_year + 1,
                "status": "ACTIVE",
                "is_current": True,
            },
            {
                "start_year": current_year + 1,
                "end_year": current_year + 2,
                "status": "DRAFT",
                "is_current": False,
            },
        ]

        for data in years_data:
            code = f"{data['start_year']}-{data['end_year']}"
            academic_year, created = AcademicYear.objects.get_or_create(
                code=code,
                defaults=data,
            )
            if created:
                self.stdout.write(f"  ✓ Created academic year: {academic_year}")
