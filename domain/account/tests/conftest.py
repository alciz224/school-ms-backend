"""
Pytest fixtures for account tests.

Provides common fixtures for user creation, authentication, and API client setup.
"""

import pytest


@pytest.fixture
def api_client():
    """Return an unauthenticated API client."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def user_data():
    """Return valid user registration data."""
    return {
        "email": "testuser@example.com",
        "phone": "+224620123456",
        "password": "TestPass123!",
        "password_confirm": "TestPass123!",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture
def user(db):
    """Create and return a test user."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        email="testuser@example.com",
        phone="+224620123456",
        password="TestPass123!",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def verified_user(db):
    """Create and return a verified test user."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create_user(
        email="verified@example.com",
        phone="+224620111111",
        password="TestPass123!",
        first_name="Verified",
        last_name="User",
    )
    user.email_verified = True
    user.phone_verified = True
    user.save()
    return user


@pytest.fixture
def another_user(db):
    """Create and return another test user."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        email="another@example.com",
        phone="+224620999999",
        password="AnotherPass123!",
        first_name="Another",
        last_name="User",
    )


@pytest.fixture
def auth_client(api_client, user):
    """Return an authenticated API client."""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def verified_auth_client(api_client, verified_user):
    """Return an authenticated API client for verified user."""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(verified_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def tokens(user):
    """Return access and refresh tokens for a user."""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


# URL helpers
class URLs:
    """API endpoint URLs."""
    
    # Auth
    LOGIN = "/api/v1/auth/login/"
    REGISTER = "/api/v1/auth/register/"
    LOGOUT = "/api/v1/auth/logout/"
    REFRESH = "/api/v1/auth/refresh/"
    
    # User Profile
    ME = "/api/v1/auth/me/"
    ME_EMAIL = "/api/v1/auth/me/email/"
    ME_PHONE = "/api/v1/auth/me/phone/"
    
    # Verification
    VERIFY_STATUS = "/api/v1/auth/verify/status/"
    VERIFY_SEND = "/api/v1/auth/verify/send/"
    VERIFY_CONFIRM = "/api/v1/auth/verify/confirm/"
    
    # Password
    PASSWORD_CHANGE = "/api/v1/auth/password/change/"
    PASSWORD_RESET = "/api/v1/auth/password/reset/"
    PASSWORD_RESET_CONFIRM = "/api/v1/auth/password/reset/confirm/"
    PASSWORD_STRENGTH = "/api/v1/auth/password/strength/"
    
    # Security Questions
    SECURITY_QUESTIONS = "/api/v1/auth/security-questions/"
    SECURITY_QUESTIONS_MINE = "/api/v1/auth/security-questions/mine/"
    SECURITY_QUESTIONS_SETUP = "/api/v1/auth/security-questions/setup/"
    SECURITY_QUESTIONS_VERIFY = "/api/v1/auth/security-questions/verify/"


@pytest.fixture
def urls():
    """Return URL helper class."""
    return URLs


@pytest.fixture
def staff_user(db):
    """Create and return a staff user."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        email="staff@example.com",
        phone="+224620222222",
        password="StaffPass123!",
        first_name="Staff",
        last_name="User",
        is_staff=True,
    )


@pytest.fixture
def superuser(db):
    """Create and return a superuser."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_superuser(
        email="admin@example.com",
        phone="+224620333333",
        password="AdminPass123!",
        first_name="Admin",
        last_name="User",
    )


@pytest.fixture
def test_locality(db):
    """Create and return a valid geographic locality."""
    from domain.geography.models import Country, RegionAdministrative, AdministrativeUnit, Locality
    country = Country.objects.create(name="Guinea", code="GN")
    region = RegionAdministrative.objects.create(country=country, name="Conakry", code="CKY")
    unit = AdministrativeUnit.objects.create(region=region, name="Ratoma", code="RTM", type="COMMUNE")
    return Locality.objects.create(administrative_unit=unit, name="Kipé", code="KIPE")


@pytest.fixture
def user_with_student_enrollment(db, test_locality):
    """Create a user with student enrollment."""
    from django.contrib.auth import get_user_model
    from domain.enrollment.models import StudentEnrollment
    from domain.school_operations.models import SchoolYear, SchoolYearCycle, SchoolYearLevel
    from domain.academic.models import AcademicYear, Cycle, Level, TermType
    from domain.school_operations.models import School
    
    User = get_user_model()
    
    # Create user
    user = User.objects.create_user(
        email="student@example.com",
        phone="+224620444444",
        password="StudentPass123!",
        first_name="Student",
        last_name="User",
    )
    
    # Create necessary related objects
    school = School.objects.create(
        name="Test School",
        code="TS001",
        locality=test_locality,
    )
    
    academic_year = AcademicYear.objects.create(
        start_year=2024,
        end_year=2025,
    )
    
    school_year = SchoolYear.objects.create(
        school=school,
        academic_year=academic_year,
        name="2024-2025",
        start_date="2024-09-01",
        end_date="2025-06-30",
    )
    
    cycle = Cycle.objects.create(
        name="Primary",
        code="PRI",
    )
    
    term_type = TermType.objects.create(
        name="Trimester",
        code="TRIM",
        period_count=3,
    )
    
    school_year_cycle = SchoolYearCycle.objects.create(
        school_year=school_year,
        cycle=cycle,
        term_type=term_type,
    )
    
    level = Level.objects.create(
        cycle=cycle,
        name="Grade 1",
        code="G1",
        order=1,
    )
    
    school_year_level = SchoolYearLevel.objects.create(
        school_year_cycle=school_year_cycle,
        level=level,
    )
    
    # Create student enrollment
    enrollment = StudentEnrollment.objects.create(
        student=user,
        first_name=user.first_name,
        last_name=user.last_name,
        school_year_level=school_year_level,
        enrollment_date="2024-09-01",
        annual_identifier=f"STU-{user.id}",
    )
    
    return user, enrollment


@pytest.fixture
def user_with_teacher_assignment(db, test_locality):
    """Create a user with teacher assignment."""
    from django.contrib.auth import get_user_model
    from domain.school_operations.models import SchoolYear, SchoolYearTeacher, School
    from domain.academic.models import AcademicYear
    
    User = get_user_model()
    
    # Create user
    user = User.objects.create_user(
        email="teacher@example.com",
        phone="+224620555555",
        password="TeacherPass123!",
        first_name="Teacher",
        last_name="User",
    )
    
    # Create necessary related objects
    school = School.objects.create(
        name="Test School 2",
        code="TS002",
        locality=test_locality,
    )
    
    academic_year, _ = AcademicYear.objects.get_or_create(
        start_year=2023,
        end_year=2024,
    )
    
    school_year = SchoolYear.objects.create(
        school=school,
        academic_year=academic_year,
        name="2023-2024",
        start_date="2023-09-01",
        end_date="2024-06-30",
    )
    
    # Create teacher assignment
    teacher_assignment = SchoolYearTeacher.objects.create(
        school_year=school_year,
        teacher=user,
        status="ACTIVE",
    )
    
    return user, teacher_assignment


@pytest.fixture
def user_with_parent_relationship(db):
    """Create a user with parent-child relationship."""
    from django.contrib.auth import get_user_model
    from domain.account.models import ParentChild
    
    User = get_user_model()
    
    # Create parent user
    parent = User.objects.create_user(
        email="parent@example.com",
        phone="+224620666666",
        password="ParentPass123!",
        first_name="Parent",
        last_name="User",
    )
    
    # Create child user
    child = User.objects.create_user(
        email="child@example.com",
        phone="+224620777777",
        password="ChildPass123!",
        first_name="Child",
        last_name="User",
    )
    
    # Create parent-child relationship
    parent_child = ParentChild.objects.create(
        parent=parent,
        child=child,
        relationship_type="FATHER",
        is_primary=True,
    )
    
    return parent, parent_child


@pytest.fixture
def user_with_multiple_roles(db, user_with_student_enrollment, user_with_teacher_assignment):
    """Create a user with both student and teacher roles."""
    from django.contrib.auth import get_user_model
    from domain.school_operations.models import SchoolYearTeacher
    
    User = get_user_model()
    
    # Use the student user and add teacher role
    user, enrollment = user_with_student_enrollment
    teacher_user, teacher_assignment = user_with_teacher_assignment
    
    # Update teacher assignment to use the student user
    teacher_assignment.teacher = user
    teacher_assignment.save()
    
    # Delete the separate teacher user
    teacher_user.delete()
    
    return user
