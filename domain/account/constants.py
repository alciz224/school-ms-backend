"""
Constants for the account application.
"""

from django.db import models


class VerificationType(models.TextChoices):
    """Verification type."""

    EMAIL = "email", "Email"
    PHONE = "phone", "Phone"
    SECURITY = "security", "Security Questions"


class VerificationMethod(models.TextChoices):
    """Verification method (subset of types)."""

    EMAIL = "email", "Email"
    PHONE = "phone", "Phone"


class VerificationPurpose(models.TextChoices):
    """Verification purpose."""

    ACCOUNT_VERIFICATION = "verify", "Account Verification"
    PASSWORD_RESET = "reset", "Password Reset"
    LOGIN_OTP = "login", "OTP Login"
    PHONE_CHANGE = "phone_change", "Phone Change"
    EMAIL_CHANGE = "email_change", "Email Change"


class PhoneRemovalReason(models.TextChoices):
    """Reason for phone number removal."""

    CHANGED = "changed", "Changed to a new one"
    LOST = "lost", "Lost / No longer accessible"
    REMOVED = "removed", "Voluntarily removed"
    REPLACED = "replaced", "Replaced by user"


class LoginFailureReason(models.TextChoices):
    """Login failure reason."""

    INVALID_CREDENTIALS = "invalid_credentials", "Invalid credentials"
    ACCOUNT_DISABLED = "account_disabled", "Account disabled"
    ACCOUNT_LOCKED = "account_locked", "Account locked"
    NOT_FOUND = "not_found", "Account not found"


class SecurityLevel(models.TextChoices):
    """Account security level."""

    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"


class UserRole(models.TextChoices):
    """User roles in the system."""

    STUDENT = "student", "Student"
    TEACHER = "teacher", "Teacher"
    PARENT = "parent", "Parent"
    ADMIN = "admin", "Admin"
    SCHOOL_ADMIN = "school_admin", "School Admin"
    SUPER_ADMIN = "super_admin", "Super Admin"


class Gender(models.TextChoices):
    """Genre / sexe (état civil)."""

    MALE = "M", "Masculin"
    FEMALE = "F", "Féminin"


class DiplomaLevel(models.TextChoices):
    """Niveau de diplôme (système éducatif guinéen)."""

    BEPC = "bepc", "BEPC"
    BAC = "bac", "Baccalauréat"
    BTS = "bts", "BTS"
    DUT = "dut", "DUT"
    LICENCE = "licence", "Licence"
    MASTER = "master", "Master"
    DOCTORAT = "doctorat", "Doctorat"
    AUTRE = "autre", "Autre"


class EmploymentType(models.TextChoices):
    """Statut d'emploi enseignant (Guinée)."""

    FONCTIONNAIRE = "fonctionnaire", "Fonctionnaire"
    CONTRACTUEL = "contractuel", "Contractuel"
    VACATAIRE = "vacataire", "Vacataire"
    BENEVOLE = "benevole", "Bénévole"


class ParentRelationshipType(models.TextChoices):
    """Type de relation parent-enfant."""

    FATHER = "FATHER", "Père"
    MOTHER = "MOTHER", "Mère"
    GUARDIAN = "GUARDIAN", "Tuteur légal"
    OTHER = "OTHER", "Autre"


class SchoolAdminPosition(models.TextChoices):
    """Poste d'un school admin dans une école."""

    DIRECTOR = "director", "Directeur"
    DEPUTY_DIRECTOR = "deputy_director", "Directeur adjoint"
    CENSOR = "censor", "Censeur"
    GENERAL_SECRETARY = "general_secretary", "Secrétaire général"
    REGISTRAR = "registrar", "Surveillant général"
    BURSAR = "bursar", "Économe"
    OTHER = "other", "Autre"


# Session keys
ACTIVE_ROLE_SESSION_KEY = "active_role"


# Predefined security questions
PREDEFINED_SECURITY_QUESTIONS = [
    # School context
    "What is the name of your primary school?",
    "What is the name of your favorite teacher?",
    "In which city did you take your first exam?",
    # Family context
    "What is your mother's first name?",
    "What is the name of your childhood neighborhood?",
    "What is your paternal grandfather's first name?",
    # Personal context
    "What is your favorite traditional dish?",
    "What is the name of your childhood best friend?",
    "What is the name of the market closest to your home?",
    "What is the name of your neighborhood mosque or church?",
]
