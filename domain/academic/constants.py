"""Constants for the Academic domain."""

# AcademicYear Status
class AcademicYearStatus:
    """Status choices for AcademicYear."""

    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"

    CHOICES = [
        (DRAFT, "Draft"),
        (ACTIVE, "Active"),
        (ARCHIVED, "Archived"),
    ]


# TermType codes
class TermTypeCode:
    """Standard term type codes."""

    TRIMESTER = "TRIMESTER"
    SEMESTER = "SEMESTER"
    QUARTER = "QUARTER"

    CHOICES = [
        (TRIMESTER, "Trimester"),
        (SEMESTER, "Semester"),
        (QUARTER, "Quarter"),
    ]


# Common cycle codes
class CycleCode:
    """Standard cycle codes."""

    MATERNELLE = "MAT"
    PRIMAIRE = "PRI"
    COLLEGE = "COL"
    LYCEE = "LYC"

    CHOICES = [
        (MATERNELLE, "Maternelle"),
        (PRIMAIRE, "Primaire"),
        (COLLEGE, "Collège"),
        (LYCEE, "Lycée"),
    ]
