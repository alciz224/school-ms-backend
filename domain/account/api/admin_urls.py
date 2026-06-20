"""
URL configuration for admin user management.

Wired from config/urls.py at /api/v1/admin/users/.
"""

from django.urls import path

from domain.account.api.views.admin_user import AdminUserViewSet

app_name = "admin_users"

urlpatterns = [
    path("", AdminUserViewSet.as_view({"get": "list", "post": "create"}), name="user_list"),
    path("me/", AdminUserViewSet.as_view({"get": "me"}), name="user_me"),
    path(
        "<uuid:pk>/",
        AdminUserViewSet.as_view({
            "get": "retrieve",
            "patch": "partial_update",
            "delete": "destroy",
        }),
        name="user_detail",
    ),
]
