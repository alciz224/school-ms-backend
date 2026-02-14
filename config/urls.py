"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/

API Contract: See API_ENDPOINTS.md for full specification.
Base URL: /api/v1/auth/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # API v1 - Authentication & User Management (JWT-based)
    # All account endpoints are prefixed with /api/v1/auth/ per API_ENDPOINTS.md
    path("api/v1/auth/", include("domain.account.api.urls", namespace="account")),
    # API v2 - Authentication & User Management (Session-based)
    # Session-based authentication for Next.js frontend
    path("api/v2/auth/", include("domain.account.api.urls_v2", namespace="account_v2")),
    # API v1 - Geography (no app name prefix in URL)
    # URLs: /api/v1/countries/, /api/v1/regions/, /api/v1/administrative-units/, /api/v1/localities/
    path("api/v1/", include("domain.geography.api.urls", namespace="geography")),
    # API v1 - Academic (master reference data)
    # URLs: /api/v1/academic/*
    path("api/v1/academic/", include("domain.academic.api.urls", namespace="academic")),
    # API v1 - School Operations
    # URLs: /api/v1/school-operations/*
    path("api/v1/school-operations/", include("domain.school_operations.api.urls", namespace="school_operations")),
    # API v1 - Enrollment
    # URLs: /api/v1/enrollment/*
    path("api/v1/enrollment/", include("domain.enrollment.api.urls", namespace="enrollment")),
    # API v1 - Assessment
    # URLs: /api/v1/assessment/*
    path("api/v1/assessment/", include("domain.assessment.api.urls", namespace="assessment")),
    # API v1 - Scheduling
    # URLs: /api/v1/scheduling/*
    path("api/v1/scheduling/", include("domain.scheduling.api.urls", namespace="scheduling")),

    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

# Debug toolbar (development only)
if settings.DEBUG:
    urlpatterns += [
        # Add browsable API authentication
        path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    ]
