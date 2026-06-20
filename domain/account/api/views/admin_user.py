"""
Admin user management views for the super-admin portal.

API endpoints (V1, JWT):
    GET    /api/v1/admin/users/       — list all users
    POST   /api/v1/admin/users/       — create a user
    GET    /api/v1/admin/users/{id}/  — retrieve user detail + profiles
    PATCH  /api/v1/admin/users/{id}/  — update user
    DELETE /api/v1/admin/users/{id}/  — soft-delete user (deactivate)
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema

from domain.account.api.serializers.admin_user import (
    AdminUserCreateResponseSerializer,
    AdminUserCreateSerializer,
    AdminUserDetailSerializer,
    AdminUserListSerializer,
    AdminUserUpdateSerializer,
)
from domain.account.selectors.admin_user import AdminUserSelector
from domain.account.services.admin_user import AdminUserService


@extend_schema(tags=["Admin Users"])
class AdminUserViewSet(viewsets.ViewSet):
    """ViewSet for super-admin user management.

    Uses ViewSet (not ModelViewSet) to keep full control over
    serializers, status codes, and response shapes.
    """

    permission_classes = [IsAdminUser]
    serializer_class = AdminUserListSerializer

    @extend_schema(
        summary="List all users",
        responses=AdminUserListSerializer(many=True),
    )
    def list(self, request):
        """GET /api/v1/admin/users/ — list all users."""
        queryset = AdminUserSelector.get_all_users()
        serializer = AdminUserListSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Create a user",
        request=AdminUserCreateSerializer,
        responses=AdminUserCreateResponseSerializer,
    )
    def create(self, request):
        """POST /api/v1/admin/users/ — create a user.

        Returns the generated password in the response so the admin
        can share initial credentials with the user.
        """
        serializer = AdminUserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user, password = AdminUserService.create_user(
            **serializer.validated_data,
            user=request.user,
        )
        out = AdminUserCreateResponseSerializer(instance=user, context={"password": password})
        return Response(out.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Retrieve user with profiles",
        responses=AdminUserDetailSerializer,
    )
    def retrieve(self, request, pk=None):
        """GET /api/v1/admin/users/{id}/ — retrieve user with profiles."""
        user = AdminUserSelector.get_user_by_id(user_id=pk)
        serializer = AdminUserDetailSerializer(user)
        return Response(serializer.data)

    @extend_schema(
        summary="Update user fields",
        request=AdminUserUpdateSerializer,
        responses=AdminUserDetailSerializer,
    )
    def partial_update(self, request, pk=None):
        """PATCH /api/v1/admin/users/{id}/ — update user fields."""
        user = AdminUserSelector.get_user_by_id(user_id=pk)
        serializer = AdminUserUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        cleaned = {k: v for k, v in serializer.validated_data.items() if v is not None}
        if cleaned:
            AdminUserService.update_user(
                target_user=user,
                data=cleaned,
                updater=request.user,
            )
        out = AdminUserDetailSerializer(user)
        return Response(out.data)

    @extend_schema(summary="Soft-delete a user", responses=None)
    def destroy(self, request, pk=None):
        """DELETE /api/v1/admin/users/{id}/ — soft-delete a user."""
        user = AdminUserSelector.get_user_by_id(user_id=pk)
        AdminUserService.delete_user(target_user=user, deleter=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Current admin's own detail",
        responses=AdminUserDetailSerializer,
    )
    @action(detail=False, methods=["get"])
    def me(self, request):
        """GET /api/v1/admin/users/me/ — current admin's own detail."""
        serializer = AdminUserDetailSerializer(request.user)
        return Response(serializer.data)
